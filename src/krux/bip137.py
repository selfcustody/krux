# The MIT License (MIT)

# Copyright (c) 2021-2024 Krux contributors

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


def message_commitment(message):
    """Double-SHA256 commitment over the BIP-137 magic"""
    from embit import compact

    try:
        import uhashlib as hashlib
    except:
        import hashlib

    return hashlib.sha256(
        hashlib.sha256(
            b"\x18Bitcoin Signed Message:\n" + compact.to_bytes(len(message)) + message
        ).digest()
    ).digest()


def build_header(raw_sig, script_type):
    """Build header byte from raw signature and script_type"""
    # grab the 2 least significant bits as recId
    # and normalize with a minimum p2pkh flag
    recid = (raw_sig[0] - 27) & 3

    if script_type == "p2sh-p2wpkh":
        return P2SH_P2WPKH_HEADER + recid
    if script_type == "p2wpkh":
        return P2WPKH_HEADER + recid

    return P2PKH_HEADER + recid


def sign(message, key, derivation, script_type="p2pkh"):
    """Sign a BIP137 message` with `key` at `derivation` for some `script_type`"""
    commitment = message_commitment(message)
    raw_sig = key.sign_at(derivation, commitment)
    header = build_header(raw_sig, script_type)
    sig = bytes([header]) + raw_sig[1:]
    return (commitment, sig)
