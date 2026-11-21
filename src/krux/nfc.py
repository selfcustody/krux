# The MIT License (MIT)

# Copyright (c) 2021-2026 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""NFC card storage - KEF envelopes on ISO14443A tags.

Reader: a WS1850S on I2C (M5Stack RFID Unit 2), configured under
Settings > Hardware > NFC and loaded only when used. Tags: MIFARE Classic 1K,
presented to callers as one flat byte array.

This module is the tag layer and the record layer. It knows how to wake a card,
select it, walk its blocks and read a record out of them, and it knows none of
that in terms of any particular chip - the reader behind self.reader answers
the eight calls in nfc_reader.py and nothing more is asked of it.

A card is input where an attacker picked every byte, and it only has to be held
near the device. Every layer here refuses anything that is not exactly what
Krux writes.

Record layout - 16 byte header at linear offset 0, payload right after:

    0..3    magic "KRN1"
    4       record type (RECORD_KEF, RECORD_DESCRIPTOR, RECORD_DATUM, RECORD_XPUB)
    5       reserved, must be zero
    6..7    payload length, big endian
    8..15   reserved, must be zero

The magic tags the format, not the device. It is shared with the Kern NFC
branch, which originated this layout, so a card written by either firmware
reads on the other. There is no checksum: the KEF envelope is authenticated, so
a half-written or decaying card fails to decrypt.

The type byte says what is inside the envelope, not how it is wrapped - every
type is KEF sealed, so every type is authenticated and compressed. RECORD_KEF
keeps the name it shipped under, when a seed was the only thing there was.
Asking for the wrong type reads as no record at all, so a descriptor card
cannot walk into the mnemonic loader and a seed card cannot walk into the
wallet. One thing it deliberately is not is a permission: what a type buys is a
parser, and each caller still runs the same validation that data arriving by QR
or SD would face.
"""

from .nfc_reader import (
    NFCError,
    NFCNotFound,
    NFCSizeError,
    FIFO_SIZE,
    CRC_LEN,
)

# Re-exported so callers keep importing their errors from krux.nfc
__all__ = ("NFC", "NFCError", "NFCNotFound", "NFCSizeError")

HEADER_LEN = 16
RECORD_MAGIC = b"KRN1"
RECORD_KEF = 1
RECORD_DESCRIPTOR = 2
RECORD_DATUM = 3
RECORD_XPUB = 4
KNOWN_RECORD_TYPES = (RECORD_KEF, RECORD_DESCRIPTOR, RECORD_DATUM, RECORD_XPUB)

# Largest payload Krux will read off a card, whatever the card claims to hold.
# A KEF-wrapped 24 word seed is under 100 bytes; the ceiling stops a hostile tag
# from driving a large allocation on a device with about 1 MB of heap.
MAX_PAYLOAD = 704

# PICC commands
CMD_WUPA = 0x52
CMD_HALT = 0x50
CMD_SEL_CL1 = 0x93
CMD_SEL_CL2 = 0x95
CMD_READ = 0x30
CMD_MF_WRITE = 0xA0

# SAK values Krux accepts: MIFARE Classic 1K, the only family that has been
# through a card. Anything else reads as an empty field - the point is to talk
# only to what we know how to talk to. 0x88 is the same 1K silicon from a second
# source, and clone chips are erratic about which of the two they report.
SAK_CLASSIC = (0x08, 0x88)
SAK_CASCADE_BIT = 0x04
CASCADE_TAG = 0x88

# MIFARE Classic 1K geometry.
MF_BLOCK_SIZE = 16
MF_DATA_BLOCKS = 47  # 64 blocks less block 0 and 16 sector trailers

# A Classic READ answers with one whole block.
READ_LEN = 16

# Nothing larger than one record is ever addressable, whatever a tag claims.
MAX_CAPACITY = MAX_PAYLOAD + HEADER_LEN


def parse_header(header, capacity, record_type=None):
    """Validates a header read off a tag, returns the payload length.

    capacity is the tag's usable linear byte count including the header, so the
    declared length is checked against what the card can physically hold as well
    as against the ceiling.

    record_type None accepts any type Krux knows how to write, which is what
    "is there already a record here" has to ask before overwriting one. A caller
    that is about to parse the payload names the type it can parse instead - one
    type, or several for a caller that can parse several - and anything else
    reads as no record.
    """
    if len(header) < HEADER_LEN or bytes(header[:4]) != RECORD_MAGIC:
        raise NFCNotFound("Not a Krux record")

    if record_type is None:
        wanted = KNOWN_RECORD_TYPES
    elif isinstance(record_type, int):
        wanted = (record_type,)
    else:
        wanted = tuple(record_type)

    # A known type, and reserved bytes that must be zero: it denies the field
    # as a covert channel and stops stale bytes from silently acquiring meaning
    # in a later format version.
    if header[4] not in wanted or header[5] != 0 or any(header[8:HEADER_LEN]):
        raise NFCNotFound("Not a Krux record")

    # A number a stranger picked. Bound it before it sizes an allocation.
    length = (header[6] << 8) | header[7]
    if not 0 < length <= min(MAX_PAYLOAD, capacity - HEADER_LEN):
        raise NFCSizeError("Invalid record length")
    return length


def build_header(length, capacity, record_type=RECORD_KEF):
    """Serializes the header for a payload about to be written"""
    if record_type not in KNOWN_RECORD_TYPES:
        raise NFCError("Unknown record type")
    if not 0 < length <= min(MAX_PAYLOAD, capacity - HEADER_LEN):
        raise NFCSizeError("Invalid record length")
    header = bytearray(HEADER_LEN)
    header[0:4] = RECORD_MAGIC
    header[4] = record_type
    header[6] = length >> 8
    header[7] = length & 0xFF
    return header


def open_reader(settings=None):
    """Builds the reader, importing the driver only when one is asked for.

    The driver is several hundred lines of constants and methods and the device
    has about 1 MB of heap, so it should not be resident on a device whose owner
    never switched NFC on. That is why this is a function and not an import at
    the top.
    """
    if settings is None:
        from .krux_settings import Settings

        settings = Settings().hardware.nfc

    from .nfc_ws1850s import WS1850S

    return WS1850S(settings.scl_pin, settings.sda_pin)


class NFC:
    """Tag layer and record I/O over any supported reader"""

    def __init__(self, reader=None):
        self.reader = open_reader() if reader is None else reader
        self.authed_sector = None
        self.tag = None

    @property
    def ready(self):
        """True once the reader is up"""
        return self.reader.ready

    # ---------- Lifecycle ----------

    def init(self):
        """Brings the reader up with the field off. Idempotent."""
        self.reader.init()

    def deinit(self):
        """Releases the tag and the reader, field off first"""
        if self.reader.ready:
            try:
                self.release()
            except NFCError:
                pass
        self.reader.deinit()

    def field(self, on):
        """Energizes or drops the RF antenna"""
        if not self.reader.ready:
            raise NFCError("Reader not ready")
        if not on:
            self.release()
        self.reader.field(on)

    # ---------- Selection ----------

    def _cascade(self, sel_cmd):
        """Runs one anticollision and select level, returning (uid, sak)"""
        reply, _ = self.reader.transceive(bytes([sel_cmd, 0x20]), 0, 5)
        if len(reply) != 5:
            raise NFCError("Bad anticollision")
        # BCC is a plain XOR check. A mismatch means a malformed frame, so stop
        # rather than build a UID out of it.
        if reply[0] ^ reply[1] ^ reply[2] ^ reply[3] != reply[4]:
            raise NFCError("Bad BCC")

        sak = self.reader.transceive_crc(bytes([sel_cmd, 0x70]) + reply, 1 + CRC_LEN)
        if len(sak) != 1:
            raise NFCError("Bad SAK")
        return reply[:4], sak[0]

    def poll(self):
        """Wakes, identifies and selects one tag.

        Raises NFCNotFound when the field is empty, holds more than one tag, or
        holds a family Krux does not accept.
        """
        if not self.reader.ready:
            raise NFCError("Reader not ready")
        self.release()

        try:
            # WUPA rather than REQA, as a 7 bit frame: release() just halted
            # whatever was there, and a halted tag answers WUPA but ignores
            # REQA, which would make the card unselectable while it stays in
            # the field.
            atqa, _ = self.reader.transceive(bytes([CMD_WUPA]), 7, 2)
            if len(atqa) != 2:
                raise NFCError("Bad ATQA")

            uid, sak = self._cascade(CMD_SEL_CL1)
            if sak & SAK_CASCADE_BIT:
                # Double size UID: the first byte of level 1 is the cascade tag,
                # not UID data. Ten byte UIDs are not supported, not guessed at.
                if uid[0] != CASCADE_TAG:
                    raise NFCError("Unsupported UID")
                head = uid[1:4]
                uid, sak = self._cascade(CMD_SEL_CL2)
                if sak & SAK_CASCADE_BIT:
                    raise NFCError("Unsupported UID")
                uid = head + uid
        except NFCError as exc:
            raise NFCNotFound("No card") from exc

        if sak not in SAK_CLASSIC:
            self.release()
            raise NFCNotFound("Unsupported card")
        self.tag = (uid, min(MF_DATA_BLOCKS * MF_BLOCK_SIZE, MAX_CAPACITY))
        return self.tag

    def release(self):
        """Halts the tag and drops any crypto1 session. Safe to call always."""
        self.authed_sector = None
        self.tag = None
        if not self.reader.ready:
            return
        # HALT goes out before crypto is dropped: while a sector is
        # authenticated the reader enciphers the frame, and a plaintext HALT
        # would be ignored, leaving the tag awake in a state it thinks is still
        # authenticated. HALT draws no reply, so a timeout is the success case.
        try:
            halt = bytes([CMD_HALT, 0x00])
            self.reader.transceive(halt + self.reader.calc_crc(halt))
        except NFCError:
            pass
        self.reader.clear_crypto()

    # ---------- Linear addressing ----------

    @staticmethod
    def _block(index):
        """Maps a data block index onto a physical MIFARE Classic block.

        Skips the manufacturer block and every sector trailer: sector 0
        contributes two data blocks, every later sector three. A corrupted
        trailer bricks its sector permanently, so the result is re-checked - it
        catches a future edit to the arithmetic before it destroys a card.
        """
        if index >= MF_DATA_BLOCKS:
            raise NFCSizeError("Block out of range")
        rest = index - 2
        block = index + 1 if index < 2 else (rest // 3 + 1) * 4 + rest % 3
        if block == 0 or block % 4 == 3:
            raise NFCError("Refusing to touch a sector trailer")
        return block

    def _authenticate(self, uid, block):
        """Authenticates a sector with the factory key A, once per sector.

        The protection is the KEF password, not the sector key: the card stays
        readable by any reader, and what a reader finds is ciphertext.
        """
        sector = block // 4
        if sector == self.authed_sector:
            return
        self.authed_sector = None
        self.reader.authenticate(uid, block)
        self.authed_sector = sector

    def _ack(self, data):
        """Sends one frame and requires a 4 bit ACK back.

        A MIFARE write is two such frames. An ACK is exactly one nibble holding
        0x0A; anything else - a NAK, a full byte, a longer frame - is a failed
        write, not a partial success.
        """
        if len(data) + CRC_LEN > FIFO_SIZE:
            raise NFCSizeError("Frame too long")
        reply, valid_bits = self.reader.transceive(
            bytes(data) + self.reader.calc_crc(data), 0, 1
        )
        if len(reply) != 1 or valid_bits != 4 or reply[0] & 0x0F != 0x0A:
            raise NFCError("Write not acknowledged")

    def _check_range(self, offset, length):
        """Refuses a range that falls outside the selected tag"""
        if self.tag is None:
            raise NFCError("No tag selected")
        capacity = self.tag[1]
        if not length or offset > capacity or length > capacity - offset:
            raise NFCSizeError("Range outside tag")

    def read(self, offset, length):
        """Reads bytes at a linear offset, spanning blocks as needed"""
        self._check_range(offset, length)
        uid, _ = self.tag

        out = bytearray()
        while len(out) < length:
            pos = offset + len(out)
            aligned = pos - pos % READ_LEN
            skip = pos - aligned
            take = min(READ_LEN - skip, length - len(out))

            block = self._block(aligned // MF_BLOCK_SIZE)
            self._authenticate(uid, block)

            # The block arrives with its CRC_A attached; the buffer has to hold
            # both or the reply reads as oversized.
            data = self.reader.transceive_crc(
                bytes([CMD_READ, block]), READ_LEN + CRC_LEN
            )
            if len(data) != READ_LEN:
                raise NFCError("Bad block read")
            out += data[skip : skip + take]
        return bytes(out)

    def write(self, offset, data):
        """Writes data at a block aligned linear offset, zero padding the tail"""
        self._check_range(offset, len(data))
        uid, _ = self.tag
        if offset % MF_BLOCK_SIZE:
            raise NFCSizeError("Unaligned write")

        done = 0
        while done < len(data):
            # Pad the tail so a short final block still writes a full block; the
            # record header carries the real length.
            chunk = bytearray(MF_BLOCK_SIZE)
            take = min(MF_BLOCK_SIZE, len(data) - done)
            chunk[0:take] = data[done : done + take]

            block = self._block((offset + done) // MF_BLOCK_SIZE)
            self._authenticate(uid, block)
            self._ack(bytes([CMD_MF_WRITE, block]))
            self._ack(chunk)
            done += MF_BLOCK_SIZE

    def erase(self):
        """Zeroes every data block on the selected tag.

        Not the header alone. A record whose header is gone is unreadable, not
        absent: the KEF envelope is still lying on the card, and one taken off a
        discarded backup can be attacked offline for as long as its password
        holds. So the whole data area goes.

        That includes the two blocks past the record ceiling. A record can never
        reach them, but MAX_PAYLOAD is a bound on what Krux will allocate for a
        stranger's card, not a statement about what is written on this one - a
        card that has been through another tool, or a future Krux with a higher
        ceiling, may well have bytes there.

        Block 0 and the sector trailers are never touched: _block refuses them,
        and a corrupted trailer bricks its sector permanently.
        """
        if self.tag is None:
            raise NFCError("No tag selected")
        uid, _ = self.tag
        blank = bytes(MF_BLOCK_SIZE)
        for index in range(MF_DATA_BLOCKS):
            block = self._block(index)
            self._authenticate(uid, block)
            self._ack(bytes([CMD_MF_WRITE, block]))
            self._ack(blank)

    # ---------- Records ----------

    def has_record(self):
        """True when the selected tag already carries a Krux record, of any type.

        Any type on purpose: this is what the overwrite warning asks, and a seed
        a descriptor is about to land on has to count as something to lose.

        Absent or unreadable records report False, so callers can warn before
        overwriting without a card fault looking like a refusal.
        """
        try:
            parse_header(self.read(0, HEADER_LEN), self.tag[1])
            return True
        except NFCError:
            return False

    def read_record(self, record_type=RECORD_KEF):
        """Reads a record of the named type, validating it throughout"""
        length = parse_header(self.read(0, HEADER_LEN), self.tag[1], record_type)
        # length is already bounded by the ceiling and by this tag's capacity
        return self.read(HEADER_LEN, length)

    def write_record(self, data, record_type=RECORD_KEF):
        """Writes a record, replacing whatever was there.

        Header and payload go out as one contiguous image so the write stays
        block aligned from offset zero and never touches a block it does not
        fully own.
        """
        header = build_header(len(data), self.tag[1], record_type)
        self.write(0, bytes(header) + bytes(data))
