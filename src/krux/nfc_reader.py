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
"""What the tag layer needs from a reader chip, and nothing else.

One chip implements this today, the WS1850S on I2C. The boundary is drawn at
frames rather than at anything electrical, so above this line nothing knows
which chip is present and below it nothing knows what a record is. That is
worth keeping with a single driver: it is what a second one would plug into,
and it is why the tag layer has no registers in it.

A reader is responsible for: bringing the chip up, energizing the antenna,
putting one frame on the air and handing back what came off it, computing a
CRC_A, and opening a MIFARE crypto1 session. Everything else - who to talk to,
what to say, what the bytes mean - belongs above.
"""


class NFCError(Exception):
    """Any NFC failure. The pages turn it into one short message, because the
    exact reason a hostile card was refused is not for the screen."""


class NFCNotFound(NFCError):
    """No reader on the bus, no acceptable tag, or no record on the tag"""


class NFCSizeError(NFCError):
    """A reply did not fit its buffer, or a payload does not fit the tag"""


# No frame may exceed the reader FIFO. A CRC_A is two bytes, and receive
# buffers must have room for it, because the CRC arrives with the frame.
FIFO_SIZE = 64
CRC_LEN = 2

# An exchange is bounded three times over: the chip's own timer, a wall clock
# deadline in case the chip stops answering, and a poll cap so a clock that
# never advances still cannot spin forever.
EXCHANGE_TIMEOUT_MS = 60
CRC_TIMEOUT_MS = 20
MAX_POLLS = 4000

MF_DEFAULT_KEY = b"\xff\xff\xff\xff\xff\xff"


class Reader:
    """The interface the tag layer calls.

    Subclasses implement init, deinit, field, transceive, calc_crc,
    authenticate and clear_crypto. transceive_crc is shared, because framing a
    CRC_A onto a frame and checking the one that comes back is the same work
    whatever computed it.
    """

    def init(self):
        """Brings the chip up with the field off. Idempotent."""
        raise NotImplementedError

    def deinit(self):
        """Drops the field and releases the bus"""
        raise NotImplementedError

    def field(self, on):
        """Energizes or drops the RF antenna"""
        raise NotImplementedError

    def transceive(self, send, tx_last_bits=0, recv_size=0):
        """Exchanges one frame, returning (reply, rx_last_bits)"""
        raise NotImplementedError

    def calc_crc(self, data):
        """Computes a CRC_A over data"""
        raise NotImplementedError

    def authenticate(self, uid, block):
        """Opens a crypto1 session on the sector holding block"""
        raise NotImplementedError

    def clear_crypto(self):
        """Drops an open crypto1 session. Never raises."""
        raise NotImplementedError

    def transceive_crc(self, send, recv_size):
        """Appends a CRC_A and verifies the one on the reply, stripping it.

        recv_size must cover the payload plus CRC_LEN - the CRC arrives as part
        of the frame, and an undersized buffer reads as an oversized reply.
        """
        if not send or len(send) + CRC_LEN > FIFO_SIZE or recv_size < CRC_LEN:
            raise NFCSizeError("Bad frame")

        reply, _ = self.transceive(bytes(send) + self.calc_crc(send), 0, recv_size)
        # A reply carrying a CRC_A is at least three bytes
        if len(reply) < 3:
            raise NFCError("Malformed reply")
        if self.calc_crc(reply[:-2]) != reply[-2:]:
            raise NFCError("Bad CRC")
        return reply[:-2]
