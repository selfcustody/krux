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
"""WS1850S reader over I2C.

Register compatible with the MFRC522, but it does not report the VersionReg
values the MFRC522 does, so presence is probed by writing a register and
reading it back.

Only this module knows the chip. Everything above it - selection, MIFARE
addressing, records - talks through the Reader interface in nfc_reader.py.
"""

import time
import board
from .nfc_reader import (
    Reader,
    NFCError,
    NFCNotFound,
    NFCSizeError,
    FIFO_SIZE,
    EXCHANGE_TIMEOUT_MS,
    CRC_TIMEOUT_MS,
    MAX_POLLS,
    MF_DEFAULT_KEY,
)

WS1850S_ADDR = 0x28
I2C_FREQ = 400000

CMD_AUTH_KEY_A = 0x60

# Registers (MFRC522 compatible)
REG_COMMAND = 0x01
REG_COM_IRQ = 0x04
REG_DIV_IRQ = 0x05
REG_ERROR = 0x06
REG_STATUS2 = 0x08
REG_FIFO_DATA = 0x09
REG_FIFO_LEVEL = 0x0A
REG_CONTROL = 0x0C
REG_BIT_FRAMING = 0x0D
REG_MODE = 0x11
REG_TX_CONTROL = 0x14
REG_TX_ASK = 0x15
REG_CRC_RESULT_H = 0x21
REG_CRC_RESULT_L = 0x22
REG_T_MODE = 0x2A
REG_T_PRESCALER = 0x2B
REG_T_RELOAD_H = 0x2C
REG_T_RELOAD_L = 0x2D

# Reader commands
PCD_IDLE = 0x00
PCD_CALC_CRC = 0x03
PCD_TRANSCEIVE = 0x0C
PCD_AUTHENT = 0x0E
PCD_RESET = 0x0F

# Any fatal ErrorReg bit means the frame is garbage. CRCErr is excluded because
# framing without a CRC legitimately leaves it set.
ERR_FATAL_MASK = 0x1B  # BufferOvfl | Coll | Parity | Protocol

IRQ_TIMER = 0x01
IRQ_IDLE = 0x10
IRQ_RX = 0x20


class WS1850S(Reader):
    """MFRC522 compatible reader on I2C"""

    def __init__(self, scl, sda, addr=WS1850S_ADDR):
        self.scl = scl
        self.sda = sda
        self.addr = addr
        self.i2c = None
        self.ready = False
        self.crypto_on = False

    # ---------- Register access ----------

    def _write(self, reg, val):
        """Writes one register"""
        self._raw(bytes([reg, val]))

    def _raw(self, payload):
        """Writes a register byte followed by data.

        Both must travel in one transaction: the MFRC522 does not auto
        increment, so every byte after the address lands in the same register.
        """
        try:
            self.i2c.writeto(self.addr, payload)
        except Exception as exc:
            raise NFCError("I2C write failed") from exc

    def _read(self, reg, length=1):
        """Reads from a register. Reading FIFODataReg repeatedly drains it."""
        try:
            self.i2c.writeto(self.addr, bytes([reg]))
            data = self.i2c.readfrom(self.addr, length)
        except Exception as exc:
            raise NFCError("I2C read failed") from exc
        if data is None or len(data) != length:
            raise NFCError("I2C short read")
        return data

    def _byte(self, reg):
        """Reads a single register"""
        return self._read(reg)[0]

    def _mask(self, reg, mask, on):
        """Sets or clears the masked bits of a register"""
        val = self._byte(reg)
        self._write(reg, val | mask if on else val & (~mask & 0xFF))

    # ---------- Lifecycle ----------

    def _open_bus(self):
        """Opens, or borrows, the I2C bus the reader sits on.

        Wired to the board's own I2C pins the reader shares the existing bus
        with the touch controller and PMU. Wired anywhere else - the UART
        header, where an external module usually ends up - it gets a controller
        of its own.
        """
        pins = board.config["krux"]["pins"]
        if pins.get("I2C_SCL") == self.scl and pins.get("I2C_SDA") == self.sda:
            from .i2c import i2c_bus

            if i2c_bus is None:
                raise NFCNotFound("No I2C bus")
            return i2c_bus

        from machine import I2C

        try:
            return I2C(I2C.I2C1, freq=I2C_FREQ, scl=self.scl, sda=self.sda)
        except Exception as exc:
            raise NFCNotFound("No I2C bus") from exc

    def init(self):
        """Brings the reader up with the field off. Idempotent."""
        if self.ready:
            return
        self.i2c = self._open_bus()

        # VersionReg is useless here, so write two patterns to a harmless
        # register and read them back. A missing module fails the transfer.
        for pattern in (0x55, 0xAA):
            try:
                self._write(REG_T_RELOAD_L, pattern)
                if self._byte(REG_T_RELOAD_L) != pattern:
                    raise NFCNotFound("No NFC reader")
            except NFCError as exc:
                raise NFCNotFound("No NFC reader") from exc

        self._write(REG_COMMAND, PCD_RESET)
        for _ in range(10):
            time.sleep_ms(5)
            try:
                if not self._byte(REG_COMMAND) & 0x10:
                    break
            except NFCError:
                pass
        else:
            raise NFCError("Reader reset timed out")

        # Timer: TAuto, prescaler 0xA9 -> 40 kHz, reload 1000 -> 25 ms per
        # exchange. This is what stops a silent tag from hanging a read.
        for reg, val in (
            (REG_T_MODE, 0x80),
            (REG_T_PRESCALER, 0xA9),
            (REG_T_RELOAD_H, 0x03),
            (REG_T_RELOAD_L, 0xE8),
            (REG_TX_ASK, 0x40),  # force 100% ASK
            (REG_MODE, 0x3D),  # CRC preset 0x6363
        ):
            self._write(reg, val)

        self.ready = True
        self.crypto_on = False
        self.field(False)  # callers energize the antenna deliberately

    def deinit(self):
        """Drops the field and forgets the bus"""
        if self.ready:
            try:
                self._mask(REG_TX_CONTROL, 0x03, False)
            except NFCError:
                pass
        self.ready = False
        self.crypto_on = False
        self.i2c = None

    def field(self, on):
        """Energizes or drops the RF antenna"""
        if not self.ready:
            raise NFCError("Reader not ready")
        self._mask(REG_TX_CONTROL, 0x03, on)

    def clear_crypto(self):
        """Drops a crypto1 session if one is open. Never raises."""
        if self.crypto_on:
            try:
                self._mask(REG_STATUS2, 0x08, False)
            except NFCError:
                pass
            self.crypto_on = False

    # ---------- Frame exchange ----------

    def _wait_irq(self, mask, timeout_ms):
        """Waits for a masked IRQ bit, the reader's timer, or the deadline"""
        deadline = time.ticks_ms() + timeout_ms
        for _ in range(MAX_POLLS):
            irq = self._byte(REG_COM_IRQ)
            if irq & mask:
                return
            if irq & IRQ_TIMER or time.ticks_ms() > deadline:
                break
        raise NFCError("No answer from tag")

    def transceive(self, send, tx_last_bits=0, recv_size=0):
        """Exchanges one frame, returning (reply, rx_last_bits).

        recv_size is the largest reply accepted; a longer one is refused rather
        than truncated, because truncating it would let the tag desynchronize
        us. 0 means no reply is expected.
        """
        if not self.ready or not send or len(send) > FIFO_SIZE or tx_last_bits > 7:
            raise NFCSizeError("Bad frame")

        self._write(REG_COMMAND, PCD_IDLE)
        self._write(REG_COM_IRQ, 0x7F)  # clear IRQs
        self._write(REG_FIFO_LEVEL, 0x80)  # flush FIFO
        self._raw(bytes([REG_FIFO_DATA]) + bytes(send))
        self._write(REG_BIT_FRAMING, tx_last_bits)
        self._write(REG_COMMAND, PCD_TRANSCEIVE)
        self._mask(REG_BIT_FRAMING, 0x80, True)  # StartSend
        try:
            self._wait_irq(IRQ_RX | IRQ_IDLE, EXCHANGE_TIMEOUT_MS)
        finally:
            self._mask(REG_BIT_FRAMING, 0x80, False)

        # A collision only happens with more than one card in the field; Krux
        # asks for a single card rather than resolving it.
        if self._byte(REG_ERROR) & ERR_FATAL_MASK:
            raise NFCError("Reader error")

        if not recv_size:
            self._write(REG_COMMAND, PCD_IDLE)
            return b"", 0

        # The tag decides this number. Copying it into a smaller buffer is the
        # classic MFRC522 overflow, so refuse rather than truncate.
        level = self._byte(REG_FIFO_LEVEL)
        if level > FIFO_SIZE:
            raise NFCError("Oversized reply")
        if level > recv_size:
            raise NFCSizeError("Reply does not fit")

        data = self._read(REG_FIFO_DATA, level) if level else b""
        # RxLastBits is three bits wide; mask before it becomes shift arithmetic
        return bytes(data), self._byte(REG_CONTROL) & 0x07

    def calc_crc(self, data):
        """Computes a CRC_A with the reader's own coprocessor"""
        if not self.ready or not data or len(data) > FIFO_SIZE:
            raise NFCSizeError("Bad CRC input")

        self._write(REG_COMMAND, PCD_IDLE)
        self._write(REG_DIV_IRQ, 0x04)  # clear CRCIRq
        self._write(REG_FIFO_LEVEL, 0x80)
        self._raw(bytes([REG_FIFO_DATA]) + bytes(data))
        self._write(REG_COMMAND, PCD_CALC_CRC)

        deadline = time.ticks_ms() + CRC_TIMEOUT_MS
        for _ in range(MAX_POLLS):
            if self._byte(REG_DIV_IRQ) & 0x04:
                self._write(REG_COMMAND, PCD_IDLE)
                return bytes(
                    [self._byte(REG_CRC_RESULT_L), self._byte(REG_CRC_RESULT_H)]
                )
            if time.ticks_ms() > deadline:
                break
        self._write(REG_COMMAND, PCD_IDLE)
        raise NFCError("CRC timed out")

    # ---------- MIFARE ----------

    def authenticate(self, uid, block):
        """Opens a crypto1 session on a sector with the factory key A.

        The protection is the KEF password, not the sector key: the card stays
        readable by any reader, and what a reader finds is ciphertext.
        """
        self._write(REG_COMMAND, PCD_IDLE)
        self._write(REG_COM_IRQ, 0x7F)
        self._write(REG_FIFO_LEVEL, 0x80)
        # Classic authenticates on the last four UID bytes, the whole UID for
        # single size tags and the tail for double size ones.
        self._raw(
            bytes([REG_FIFO_DATA, CMD_AUTH_KEY_A, block])
            + MF_DEFAULT_KEY
            + bytes(uid[-4:])
        )
        self._write(REG_COMMAND, PCD_AUTHENT)
        try:
            self._wait_irq(IRQ_IDLE, EXCHANGE_TIMEOUT_MS)
        except NFCError:
            self._write(REG_COMMAND, PCD_IDLE)
            self.crypto_on = False
            raise

        # Crypto1On is the only reliable success signal
        if not self._byte(REG_STATUS2) & 0x08:
            self.crypto_on = False
            raise NFCError("Authentication failed")
        self.crypto_on = True
