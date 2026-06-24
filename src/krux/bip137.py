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

P2PKH_UNCOMPRESSED_HEADER = 27
P2PKH_HEADER = 31
P2SH_P2WPKH_HEADER = 35
P2WPKH_HEADER = 39
MESSAGE_MAGIC = b"\x18Bitcoin Signed Message:\n"
RECID_OFFSET = P2PKH_HEADER - P2PKH_UNCOMPRESSED_HEADER


def message_commitment(message):
    """Double-SHA256 commitment over the BIP-137 magic"""
    from embit import compact

    try:
        import uhashlib as hashlib
    except ImportError:
        import hashlib

    # BIP137 commitment message:
    # `SHA256(SHA256(MAGIC // varint // message))`
    varint = compact.to_bytes(len(message))
    _message = MESSAGE_MAGIC + varint + message
    return hashlib.sha256(hashlib.sha256(_message).digest()).digest()


def build_header(raw_sig, script_type, compressed=True):
    """Build header byte from raw signature and script_type"""
    # Avoid some unexpected header
    rsig = raw_sig[0]
    if not P2PKH_UNCOMPRESSED_HEADER <= rsig <= P2PKH_HEADER + 3:
        raise ValueError("Invalid sig header: %d" % rsig)

    # grab the 2 least significant bits as recId
    # and normalize with a minimum p2pkh (uncompressed) flag
    recid = (raw_sig[0] - P2PKH_UNCOMPRESSED_HEADER) & 3

    if script_type == "p2sh-p2wpkh":
        return P2SH_P2WPKH_HEADER + recid
    if script_type == "p2wpkh":
        return P2WPKH_HEADER + recid

    # compressed=False is only meaningful for p2pkh
    return (
        P2PKH_UNCOMPRESSED_HEADER
        + recid
        + (0 if not compressed and script_type == "p2pkh" else RECID_OFFSET)
    )


def sign(message, key, derivation, script_type="p2pkh", compressed=True):
    """Sign a BIP137 `message` with `key` at `derivation` for some `script_type`"""
    commitment = message_commitment(message)
    raw_sig = key.sign_at(derivation, commitment)
    header = build_header(raw_sig, script_type, compressed)
    sig = bytes([header]) + raw_sig[1:]
    return (commitment, sig)
