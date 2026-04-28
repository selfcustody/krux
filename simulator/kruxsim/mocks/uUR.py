# The MIT License (MIT)

# Copyright (c) 2021-2025 Krux contributors

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

"""CPython shim that mirrors the firmware's uUR C module by re-exporting
the pure-Python `urtypes` and `foundation-ur-py` packages under the same
public surface (UR, URDecoder, UREncoder, Types).
"""

import sys

from ur.ur import UR
from ur.ur_decoder import URDecoder as _URDecoder
from ur.ur_encoder import UREncoder as _UREncoder

from urtypes.bytes import Bytes as _Bytes
from urtypes.crypto.account import Account as _Account
from urtypes.crypto.bip39 import BIP39 as _BIP39
from urtypes.crypto.output import Output as _Output
from urtypes.crypto.psbt import PSBT as _PSBT


class UREncoder(_UREncoder):
    """uUR's encoder emits uppercase Bytewords; the Python encoder emits
    lowercase. Match firmware behaviour by uppercasing here."""

    def next_part(self):
        return super().next_part().upper()


class URDecoder(_URDecoder):
    """uUR exposes expected_part_count and processed_parts_count as plain
    int attributes (zero for single-part URs). Mirror that here so the same
    qr.py logic works against both decoders."""

    @property
    def expected_part_count(self):
        if self.fountain_decoder.expected_part_indexes is None:
            return 0
        return len(self.fountain_decoder.expected_part_indexes)

    @property
    def processed_parts_count(self):
        return self.fountain_decoder.processed_parts_count


class Types:
    CRYPTO_PSBT_TYPE = "crypto-psbt"
    CRYPTO_BIP39_TYPE = "crypto-bip39"
    CRYPTO_OUTPUT_TYPE = "crypto-output"
    CRYPTO_ACCOUNT_TYPE = "crypto-account"

    @staticmethod
    def psbt_from_cbor(cbor):
        return _PSBT.from_cbor(cbor).data

    @staticmethod
    def psbt_to_cbor(data):
        return _PSBT(data).to_cbor()

    @staticmethod
    def bytes_from_cbor(cbor):
        return _Bytes.from_cbor(cbor).data

    @staticmethod
    def bytes_to_cbor(data):
        return _Bytes(data).to_cbor()

    @staticmethod
    def bip39_words_from_cbor(cbor):
        return _BIP39.from_cbor(cbor).words

    @staticmethod
    def output_from_cbor(cbor):
        return _Output.from_cbor(cbor).descriptor()

    @staticmethod
    def output_from_cbor_account(cbor):
        return _Account.from_cbor(cbor).output_descriptors[0].descriptor()


if "uUR" not in sys.modules:
    sys.modules["uUR"] = sys.modules[__name__]
