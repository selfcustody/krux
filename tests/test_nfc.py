# NFC reader, tag layer and record tests
#
# The reader and one MIFARE Classic 1K are emulated at the I2C level, so the
# whole stack - register access, ISO14443A framing, sector authentication,
# linear addressing and the record header - runs end to end without hardware.
#
# The card supplies every byte of a record header, so much of this is about
# what the parser refuses. Each malformed header is something a hostile or
# half-written tag can present.

import pytest

UID = b"\xde\xad\xbe\xef"
CAPACITY = 720  # a 1K Classic clamped to one record's worth
SMALL_TAG = 144  # a capacity smaller than a record, to exercise the bounds


def crc_a(data):
    """ISO14443-A CRC, the value the reader's coprocessor produces"""
    crc = 0x6363
    for byte in data:
        byte ^= crc & 0xFF
        byte = (byte ^ (byte << 4)) & 0xFF
        crc = ((crc >> 8) ^ (byte << 8) ^ (byte << 3) ^ (byte >> 4)) & 0xFFFF
    return bytes([crc & 0xFF, crc >> 8])


class FakeClassic:
    """A MIFARE Classic 1K that answers the frames Krux sends it"""

    def __init__(self, uid=UID, sak=0x08):
        self.uid = uid
        self.sak = sak
        self.blocks = [bytearray(16) for _ in range(64)]
        self.authed = False
        self.write_target = None

    def frame(self, data, tx_last_bits):
        """Returns (reply, rx_last_bits), or None for silence"""
        bcc = self.uid[0] ^ self.uid[1] ^ self.uid[2] ^ self.uid[3]
        if tx_last_bits == 7 and data == b"\x52":  # WUPA
            return b"\x04\x00", 0
        if data == b"\x93\x20":  # anticollision
            return self.uid + bytes([bcc]), 0
        if data[:2] == b"\x93\x70":  # select
            return bytes([self.sak]) + crc_a(bytes([self.sak])), 0
        if data[:2] == b"\x50\x00":  # HALT draws no reply
            self.authed = False
            return None
        if self.write_target is not None:  # the data half of a write
            block, self.write_target = self.write_target, None
            if len(data) != 18 or crc_a(data[:16]) != data[16:]:
                return None
            self.blocks[block][:] = data[:16]
            return b"\x0a", 4
        if not self.authed or len(data) != 4:
            return None
        if data[0] == 0x30:  # READ
            block = bytes(self.blocks[data[1]])
            return block + crc_a(block), 0
        if data[0] == 0xA0:  # WRITE
            self.write_target = data[1]
            return b"\x0a", 4
        return None


class FakeI2C:
    """Enough of a WS1850S to drive the register level code"""

    def __init__(self, tag=None, present=True):
        self.regs = bytearray(0x40)
        self.fifo = bytearray()
        self.tag = tag
        self.present = present
        self.tx_last_bits = 0
        self.forced_level = None  # a reply length no real tag would send
        self._reg = None

    def writeto(self, _addr, buf):
        """One byte selects a register to read; more than one writes to it"""
        if not self.present:
            raise OSError("nack")
        buf = bytes(buf)
        if len(buf) == 1:
            self._reg = buf[0]
            return
        if buf[0] == 0x09:  # FIFODataReg does not auto increment
            self.fifo.extend(buf[1:])
            return
        for byte in buf[1:]:
            self._write_reg(buf[0], byte)

    def readfrom(self, _addr, length):
        """Reads back whatever register was selected"""
        if not self.present:
            raise OSError("nack")
        if self._reg == 0x09:  # draining the FIFO
            out, self.fifo = bytes(self.fifo[:length]), self.fifo[length:]
            return out
        if self._reg == 0x0A:  # FIFOLevelReg
            level = len(self.fifo) if self.forced_level is None else self.forced_level
            return bytes([level])
        return bytes(self.regs[self._reg : self._reg + 1]) * length

    def _write_reg(self, reg, val):
        if reg == 0x01:  # CommandReg
            self._run(val)
        elif reg == 0x0A and val & 0x80:  # flush FIFO
            self.fifo = bytearray()
        elif reg == 0x04:  # ComIrqReg, writing clears
            self.regs[0x04] = 0
        else:
            if reg == 0x0D:  # BitFramingReg
                self.tx_last_bits = val & 0x07
            self.regs[reg] = val

    def _run(self, cmd):
        self.regs[0x01] = 0 if cmd == 0x0F else cmd  # reset comes back idle
        if cmd == 0x03:  # CalcCRC
            self.regs[0x22], self.regs[0x21] = crc_a(bytes(self.fifo))
            self.regs[0x05] |= 0x04  # CRCIRq
        elif cmd == 0x0C:  # Transceive
            self._transceive()
        elif cmd == 0x0E:  # MFAuthent
            if self.tag is not None:
                self.tag.authed = True
            self.regs[0x08] |= 0x08  # Crypto1On
            self.regs[0x04] = 0x10  # IdleIRq

    def _transceive(self):
        sent, self.fifo = bytes(self.fifo), bytearray()
        reply = self.tag.frame(sent, self.tx_last_bits) if self.tag else None
        self.regs[0x06] = 0  # ErrorReg
        if reply is None:
            self.regs[0x04] = 0x01  # TimerIRq
            return
        self.fifo = bytearray(reply[0])
        self.regs[0x0C] = reply[1] & 0x07  # ControlReg
        self.regs[0x04] = 0x30  # RxIRq | IdleIRq


def make_reader(i2c):
    """A WS1850S wired to the fake bus, with nothing above it"""
    from krux.nfc_ws1850s import WS1850S

    reader = WS1850S(scl=1, sda=2)
    reader._open_bus = lambda: i2c
    return reader


def make_nfc(i2c, select=True):
    """An NFC facade on a WS1850S wired to the fake bus instead of a real one"""
    from krux.nfc import NFC
    from krux.nfc_ws1850s import WS1850S

    reader = WS1850S(scl=1, sda=2)
    reader._open_bus = lambda: i2c
    nfc = NFC(reader=reader)
    nfc.init()
    nfc.field(True)
    if select:
        nfc.poll()
    return nfc


def good_header(nfc_mod, length=16, capacity=CAPACITY):
    """A valid header for a test to then corrupt"""
    return bytearray(nfc_mod.build_header(length, capacity))


# ---------- Record header ----------


def test_round_trip(m5stickv):
    import krux.nfc as nfc

    assert nfc.parse_header(nfc.build_header(16, CAPACITY), CAPACITY) == 16
    assert (
        nfc.parse_header(nfc.build_header(nfc.MAX_PAYLOAD, CAPACITY), CAPACITY)
        == nfc.MAX_PAYLOAD
    )


def test_header_bytes_are_the_shared_on_card_format(m5stickv):
    """Locks the exact bytes a Kern reader expects.

    The format is shared with the Kern NFC branch. Without this, a refactor
    could change what lands on the card and cards would stop crossing between
    the two firmwares silently - both sides would stay self-consistent.
    """
    import krux.nfc as nfc

    assert bytes(nfc.build_header(64, CAPACITY)) == b"KRN1\x01\x00\x00\x40" + bytes(8)
    assert nfc.parse_header(b"KRN1\x01\x00\x00\x2c" + bytes(8), CAPACITY) == 44

    # The descriptor type, pinned the same way and for the same reason
    assert bytes(
        nfc.build_header(64, CAPACITY, nfc.RECORD_DESCRIPTOR)
    ) == b"KRN1\x02\x00\x00\x40" + bytes(8)
    assert (
        nfc.parse_header(
            b"KRN1\x02\x00\x00\x2c" + bytes(8), CAPACITY, nfc.RECORD_DESCRIPTOR
        )
        == 44
    )


@pytest.mark.parametrize("record_type", [1, 2, 3, 4])
def test_a_record_of_one_type_does_not_answer_as_the_other(m5stickv, record_type):
    """Asking for the wrong type reads as no record at all.

    This is what keeps a descriptor card out of the mnemonic loader and a seed
    card out of the wallet, before either payload is decrypted.
    """
    import krux.nfc as nfc

    header = nfc.build_header(44, CAPACITY, record_type)
    assert nfc.parse_header(header, CAPACITY, record_type) == 44

    for other in nfc.KNOWN_RECORD_TYPES:
        if other == record_type:
            continue
        with pytest.raises(nfc.NFCNotFound):
            nfc.parse_header(header, CAPACITY, other)


@pytest.mark.parametrize("record_type", [1, 2, 3, 4])
def test_any_krux_record_counts_as_something_to_overwrite(m5stickv, record_type):
    """has_record() takes no type, so a seed about to be replaced by a
    descriptor still raises the overwrite warning. Asking for the type being
    written would report an empty card and take the seed with it."""
    import krux.nfc as nfc

    header = nfc.build_header(44, CAPACITY, record_type)
    assert nfc.parse_header(header, CAPACITY) == 44


def test_a_type_krux_cannot_write_is_refused_at_the_source(m5stickv):
    import krux.nfc as nfc

    for record_type in range(256):
        if record_type in nfc.KNOWN_RECORD_TYPES:
            continue
        with pytest.raises(nfc.NFCError):
            nfc.build_header(44, CAPACITY, record_type)


@pytest.mark.parametrize(
    "header",
    [
        bytes(16),  # a blank card
        b"\xff" * 16,  # an erased card
        b"KRN2\x01\x00\x00\x10" + bytes(8),  # near miss magic
        b"KRN1\x00\x00\x00\x10" + bytes(8),  # record type zero
        b"KRN1\x7f\x00\x00\x10" + bytes(8),  # unknown record type
        b"KRN1\xff\x00\x00\x10" + bytes(8),  # unknown record type
        b"KRN1\x01\x01\x00\x10" + bytes(8),  # reserved byte 5 set
        b"KRN1\x01\x00\x00\x10" + b"\x01" + bytes(7),  # reserved byte 8 set
        b"KRN1\x01\x00\x00\x10" + bytes(7) + b"\x01",  # reserved byte 15 set
        b"KRN1\x01\x00\x00\x10",  # short header
        b"",
    ],
)
def test_a_card_that_is_not_ours_is_refused(m5stickv, header):
    import krux.nfc as nfc

    with pytest.raises(nfc.NFCNotFound):
        nfc.parse_header(header, CAPACITY)


@pytest.mark.parametrize(
    "length, capacity",
    [
        (0, CAPACITY),  # empty payload
        (0xFFFF, CAPACITY),  # 16 bit maximum
        (705, CAPACITY),  # one past the ceiling
        (200, SMALL_TAG),  # under the ceiling, larger than the tag
        (SMALL_TAG - 16 + 1, SMALL_TAG),  # one past a full tag
        (16, 8),  # capacity below the header
        (16, 0),
    ],
)
def test_a_length_the_tag_cannot_back_is_refused(m5stickv, length, capacity):
    """The declared length is a number a stranger picked"""
    import krux.nfc as nfc

    header = good_header(nfc)
    header[6], header[7] = length >> 8, length & 0xFF
    with pytest.raises(nfc.NFCSizeError):
        nfc.parse_header(header, capacity)
    with pytest.raises(nfc.NFCSizeError):
        nfc.build_header(length, capacity)


def test_a_payload_exactly_filling_the_tag_is_accepted(m5stickv):
    import krux.nfc as nfc

    header = nfc.build_header(SMALL_TAG - nfc.HEADER_LEN, SMALL_TAG)
    assert nfc.parse_header(header, SMALL_TAG) == SMALL_TAG - nfc.HEADER_LEN


# ---------- Reader ----------


def test_init_comes_up_with_the_antenna_dark(m5stickv):
    """Callers energize the field deliberately, inside the tap page"""
    i2c = FakeI2C()
    reader = make_reader(i2c)
    reader.init()
    assert reader.ready
    assert not i2c.regs[0x14] & 0x03

    reader.field(True)
    assert i2c.regs[0x14] & 0x03 == 0x03
    reader.field(False)
    assert not i2c.regs[0x14] & 0x03


def test_missing_reader_is_reported(m5stickv):
    from krux.nfc import NFCNotFound

    with pytest.raises(NFCNotFound):
        make_reader(FakeI2C(present=False)).init()


def test_a_bus_device_that_is_not_a_reader_is_refused(m5stickv):
    """Answers on the bus, but does not behave like a WS1850S"""
    from krux.nfc import NFCNotFound

    class Deaf(FakeI2C):
        def _write_reg(self, reg, val):
            if reg != 0x2D:
                super()._write_reg(reg, val)

    with pytest.raises(NFCNotFound):
        make_reader(Deaf()).init()


def test_deinit_drops_the_field_and_the_crypto_session(m5stickv):
    i2c = FakeI2C(FakeClassic())
    nfc = make_nfc(i2c)
    nfc.write_record(bytes(32))  # authenticates a sector

    nfc.deinit()
    assert not nfc.ready
    assert not i2c.regs[0x14] & 0x03
    assert not i2c.regs[0x08] & 0x08


def test_silent_tag_times_out(m5stickv):
    from krux.nfc import NFCError

    nfc = make_nfc(FakeI2C(FakeClassic()), select=False)
    with pytest.raises(NFCError):
        nfc.reader.transceive(b"\x99", 0, 4)


def test_oversized_reply_is_refused_not_truncated(m5stickv):
    """The classic MFRC522 overflow: the tag chooses the reply length"""
    from krux.nfc import NFCSizeError, NFCError

    nfc = make_nfc(FakeI2C(FakeClassic()), select=False)
    with pytest.raises(NFCSizeError):
        nfc.reader.transceive(b"\x52", 7, 1)  # ATQA is two bytes

    nfc.reader.i2c.forced_level = 200
    with pytest.raises(NFCError):
        nfc.reader.transceive(b"\x52", 7, 64)


def test_frame_longer_than_the_fifo_is_refused(m5stickv):
    from krux.nfc import NFCSizeError

    nfc = make_nfc(FakeI2C(FakeClassic()), select=False)
    with pytest.raises(NFCSizeError):
        nfc.reader.transceive(b"\x00" * 65, 0, 2)


def test_reader_error_bits_fail_the_exchange(m5stickv):
    """Two cards in the field"""
    from krux.nfc import NFCError

    class Colliding(FakeI2C):
        def _transceive(self):
            super()._transceive()
            self.regs[0x06] = 0x08  # CollErr

    nfc = make_nfc(Colliding(FakeClassic()), select=False)
    with pytest.raises(NFCError):
        nfc.reader.transceive(b"\x52", 7, 4)


def test_calc_crc_matches_the_reference(m5stickv):
    nfc = make_nfc(FakeI2C(), select=False)
    assert nfc.reader.calc_crc(b"\x30\x04") == crc_a(b"\x30\x04")


# ---------- Selection ----------


def test_select_reads_a_classic(m5stickv):
    nfc = make_nfc(FakeI2C(FakeClassic()))
    assert nfc.tag == (UID, CAPACITY)


@pytest.mark.parametrize(
    "tag",
    [
        None,  # an empty field
        FakeClassic(sak=0x20),  # ISO14443-4, a card Krux cannot address
        FakeClassic(sak=0x18),  # Classic 4K, a family Krux is not tested against
        FakeClassic(sak=0x00),  # Ultralight / NTAG, no longer supported
    ],
)
def test_a_card_krux_cannot_use_reads_as_an_empty_field(m5stickv, tag):
    from krux.nfc import NFCNotFound

    nfc = make_nfc(FakeI2C(tag), select=False)
    with pytest.raises(NFCNotFound):
        nfc.poll()


def test_bad_bcc_is_refused(m5stickv):
    """A malformed anticollision reply is not a UID to build on"""
    from krux.nfc import NFCNotFound

    class BadBcc(FakeClassic):
        def frame(self, data, tx_last_bits):
            if data == b"\x93\x20":
                return self.uid + b"\x00", 0
            return super().frame(data, tx_last_bits)

    nfc = make_nfc(FakeI2C(BadBcc()), select=False)
    with pytest.raises(NFCNotFound):
        nfc.poll()


def test_bad_crc_is_caught(m5stickv):
    from krux.nfc import NFCNotFound

    class Lying(FakeClassic):
        def frame(self, data, tx_last_bits):
            if data[:2] == b"\x93\x70":
                return bytes([self.sak]) + b"\x00\x00", 0
            return super().frame(data, tx_last_bits)

    nfc = make_nfc(FakeI2C(Lying()), select=False)
    with pytest.raises(NFCNotFound):
        nfc.poll()


# ---------- Linear addressing ----------


def test_block_mapping_never_touches_block_zero_or_a_trailer(m5stickv):
    """A corrupted sector trailer bricks its sector permanently"""
    from krux.nfc import NFC, MF_DATA_BLOCKS, NFCSizeError

    blocks = [NFC._block(i) for i in range(MF_DATA_BLOCKS)]
    assert 0 not in blocks
    assert not any(block % 4 == 3 for block in blocks)
    assert blocks == sorted(set(blocks)) and len(blocks) == MF_DATA_BLOCKS
    assert blocks[:4] == [1, 2, 4, 5]

    with pytest.raises(NFCSizeError):
        NFC._block(MF_DATA_BLOCKS)


def test_read_and_write_span_blocks(m5stickv):
    nfc = make_nfc(FakeI2C(FakeClassic()))

    payload = bytes(range(48))
    nfc.write(0, payload)
    assert nfc.read(0, len(payload)) == payload
    # An unaligned read still lands on the right bytes
    assert nfc.read(5, 20) == payload[5:25]


@pytest.mark.parametrize("offset, size", [(0, CAPACITY + 1), (CAPACITY - 8, 16)])
def test_a_range_outside_the_tag_is_refused(m5stickv, offset, size):
    from krux.nfc import NFCSizeError

    nfc = make_nfc(FakeI2C(FakeClassic()))
    with pytest.raises(NFCSizeError):
        nfc.read(offset, size)
    with pytest.raises(NFCSizeError):
        nfc.write(offset, bytes(size))


def test_unaligned_write_is_refused(m5stickv):
    from krux.nfc import NFCSizeError

    nfc = make_nfc(FakeI2C(FakeClassic()))
    with pytest.raises(NFCSizeError):
        nfc.write(8, bytes(16))


# ---------- Records ----------


def test_record_round_trip(m5stickv):
    nfc = make_nfc(FakeI2C(FakeClassic()))
    assert not nfc.has_record()

    envelope = bytes(range(60))
    nfc.write_record(envelope)
    assert nfc.has_record()
    assert nfc.read_record() == envelope


def test_a_descriptor_round_trips_through_a_real_card(m5stickv):
    """The whole stack, not just the header: a descriptor sized like a 2 of 3
    goes out over the same block addressing a seed uses and comes back."""
    from krux.nfc import RECORD_DESCRIPTOR, RECORD_KEF, NFCNotFound

    nfc = make_nfc(FakeI2C(FakeClassic()))
    envelope = bytes(range(256)) * 2  # 512 bytes, a sealed 2 of 3 descriptor

    nfc.write_record(envelope, RECORD_DESCRIPTOR)
    assert nfc.has_record()
    assert nfc.read_record(RECORD_DESCRIPTOR) == envelope

    # The seed loader asking the same card finds nothing to load
    with pytest.raises(NFCNotFound):
        nfc.read_record(RECORD_KEF)


def test_a_seed_card_warns_before_a_descriptor_lands_on_it(m5stickv):
    """The overwrite prompt reads has_record(), which takes no type. If it
    asked for the type being written, this card would look blank and the seed
    would go without a word."""
    from krux.nfc import RECORD_DESCRIPTOR, RECORD_KEF

    nfc = make_nfc(FakeI2C(FakeClassic()))
    nfc.write_record(bytes(range(32)), RECORD_KEF)

    assert nfc.has_record()

    nfc.write_record(bytes(range(60)), RECORD_DESCRIPTOR)
    assert nfc.read_record(RECORD_DESCRIPTOR) == bytes(range(60))


def test_blank_card_reports_no_record(m5stickv):
    from krux.nfc import NFCNotFound

    nfc = make_nfc(FakeI2C(FakeClassic()))
    assert not nfc.has_record()
    with pytest.raises(NFCNotFound):
        nfc.read_record()


def test_payload_over_the_ceiling_is_refused(m5stickv):
    from krux.nfc import MAX_PAYLOAD, NFCSizeError

    nfc = make_nfc(FakeI2C(FakeClassic()))
    with pytest.raises(NFCSizeError):
        nfc.write_record(bytes(MAX_PAYLOAD + 1))


def test_a_card_that_stops_answering_mid_read_fails(m5stickv):
    from krux.nfc import NFCError

    tag = FakeClassic()
    nfc = make_nfc(FakeI2C(tag))
    nfc.write_record(bytes(range(40)))

    tag.frame = lambda data, bits: None
    with pytest.raises(NFCError):
        nfc.read_record()


def test_erase_clears_every_data_block(m5stickv):
    """Every data block, not just the header: an envelope left behind can be
    carried off and attacked offline."""
    from krux.nfc import MF_DATA_BLOCKS, NFC

    tag = FakeClassic()
    nfc = make_nfc(FakeI2C(tag))
    nfc.write_record(bytes(range(60)))
    assert nfc.has_record()

    nfc.erase()

    assert not nfc.has_record()
    touched = [NFC._block(i) for i in range(MF_DATA_BLOCKS)]
    for block in touched:
        assert tag.blocks[block] == bytearray(16), "block %d survived" % block


def test_erase_reaches_past_the_record_ceiling(m5stickv):
    """The last two data blocks are outside any record, so write() cannot
    address them. Erase still has to, or bytes from another tool stay put."""
    from krux.nfc import MF_DATA_BLOCKS, MAX_CAPACITY, MF_BLOCK_SIZE, NFC

    tag = FakeClassic()
    nfc = make_nfc(FakeI2C(tag))

    beyond = [
        NFC._block(i) for i in range(MAX_CAPACITY // MF_BLOCK_SIZE, MF_DATA_BLOCKS)
    ]
    assert beyond, "the ceiling is supposed to leave blocks unaddressable"
    for block in beyond:
        tag.blocks[block] = bytearray(b"\xa5" * 16)

    nfc.erase()
    for block in beyond:
        assert tag.blocks[block] == bytearray(16)


def test_erase_never_touches_a_trailer_or_block_zero(m5stickv):
    tag = FakeClassic()
    for block in range(64):
        tag.blocks[block] = bytearray(b"\x5a" * 16)
    nfc = make_nfc(FakeI2C(tag))

    nfc.erase()

    assert tag.blocks[0] == bytearray(b"\x5a" * 16)
    for block in range(3, 64, 4):
        assert tag.blocks[block] == bytearray(b"\x5a" * 16), (
            "trailer %d written" % block
        )


def test_erase_without_a_tag_is_an_nfc_error(m5stickv):
    from krux.nfc import NFCError

    nfc = make_nfc(FakeI2C(), select=False)
    with pytest.raises(NFCError):
        nfc.erase()


def test_the_parametrized_type_lists_cover_every_known_type(m5stickv):
    """A new record type must not slip in with the cross-refusal tests still
    only exercising the old ones. Update the parametrize lists above when this
    fails - do not widen this assertion."""
    import krux.nfc as nfc

    assert nfc.KNOWN_RECORD_TYPES == (1, 2, 3, 4)


@pytest.mark.parametrize("record_type", [1, 2, 3, 4])
def test_a_caller_can_name_several_acceptable_types(m5stickv, record_type):
    """The datum tool asks for every type at once, so a tuple has to mean "any
    of these". Wrapping it in another tuple instead refuses every card, which is
    what shipped: the datum tool could not read a card it had just written.

    This goes through the card stack rather than a mocked facade, because the
    test that let the bug through asserted the call and not the outcome.
    """
    from krux.nfc import KNOWN_RECORD_TYPES

    nfc = make_nfc(FakeI2C(FakeClassic()))
    payload = bytes(range(40))
    nfc.write_record(payload, record_type)

    assert nfc.read_record(KNOWN_RECORD_TYPES) == payload
    assert nfc.read_record(list(KNOWN_RECORD_TYPES)) == payload
    assert nfc.read_record(record_type) == payload


def test_naming_several_types_still_refuses_the_ones_left_out(m5stickv):
    from krux.nfc import RECORD_KEF, RECORD_DESCRIPTOR, RECORD_DATUM, NFCNotFound

    nfc = make_nfc(FakeI2C(FakeClassic()))
    nfc.write_record(bytes(range(40)), RECORD_DATUM)

    with pytest.raises(NFCNotFound):
        nfc.read_record((RECORD_KEF, RECORD_DESCRIPTOR))


# ---------- The write/read matrix ----------
#
# Every form Krux writes, against every set of types a read path accepts. The
# point is not that each cell works but that the cells which must refuse do:
# a seed card has to stay out of the wallet and a descriptor card out of the
# mnemonic loader, and neither is allowed to depend on what the payload holds.

WRITE_FORMS = {
    "seed KEF (Backup > Encrypted)": 1,
    "descriptor (Wallet Descriptor)": 2,
    "datum (Datum Tool)": 3,
    "xpub (Extended Public Key)": 4,
}

READ_PATHS = {
    "Load Mnemonic > From NFC Card": (1,),
    "Wallet Descriptor > Load from NFC card": (2,),
    "Datum Tool > From NFC Card": (1, 2, 3, 4),
}


@pytest.mark.parametrize("write_name", sorted(WRITE_FORMS))
@pytest.mark.parametrize("read_name", sorted(READ_PATHS))
def test_the_write_read_matrix(m5stickv, write_name, read_name):
    from krux.nfc import NFCNotFound

    record_type = WRITE_FORMS[write_name]
    accepted = READ_PATHS[read_name]

    nfc = make_nfc(FakeI2C(FakeClassic()))
    payload = bytes(range(48))
    nfc.write_record(payload, record_type)

    # Whatever the type, the card is never mistaken for blank
    assert nfc.has_record(), "%s did not register as a record" % write_name

    if record_type in accepted:
        assert nfc.read_record(accepted) == payload, "%s should open in %s" % (
            write_name,
            read_name,
        )
    else:
        with pytest.raises(NFCNotFound):
            nfc.read_record(accepted)


def test_the_matrix_covers_every_type_krux_writes(m5stickv):
    """Fails when a record type is added without a row in the matrix above"""
    import krux.nfc as nfc

    assert sorted(WRITE_FORMS.values()) == sorted(nfc.KNOWN_RECORD_TYPES)
    assert READ_PATHS["Datum Tool > From NFC Card"] == nfc.KNOWN_RECORD_TYPES
