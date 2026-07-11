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
import hashlib
import hmac
from io import BytesIO

from embit import compact, ec, script

MAGIC = b"\x53\x4c\x00\x19"
USER_CONFIRMATION = 1
RESERVED_FLAGS = 0xFE
P2WPKH = "p2wpkh"
P2TR = "p2tr"


def _script_bytes(script_pubkey):
    return script_pubkey.data if hasattr(script_pubkey, "data") else script_pubkey


def _ser_string(data):
    return compact.to_bytes(len(data)) + data


def slip21_key(seed, labels):
    """Returns SLIP-21 Key(m/label/...) from a binary seed."""
    node = hmac.new(b"Symmetric key seed", seed, digestmod="sha512").digest()
    for label in labels:
        if isinstance(label, str):
            label = label.encode()
        node = hmac.new(node[:32], b"\x00" + label, digestmod="sha512").digest()
    return node[32:]


def ownership_id(ownership_key, script_pubkey):
    """Returns the SLIP-19 ownership id for a scriptPubKey."""
    return hmac.new(
        ownership_key, _script_bytes(script_pubkey), digestmod="sha256"
    ).digest()


def proof_body(flags, ownership_ids):
    """Builds a single SLIP-19 proof body."""
    if flags & RESERVED_FLAGS:
        raise ValueError("reserved SLIP-19 flags set")
    return (
        MAGIC
        + bytes([flags])
        + compact.to_bytes(len(ownership_ids))
        + b"".join(ownership_ids)
    )


def proof_digest(body, script_pubkey, commitment_data):
    """Returns SHA256(proofBody || proofFooter)."""
    if commitment_data is None:
        raise ValueError("missing commitment data")
    script_data = _script_bytes(script_pubkey)
    return hashlib.sha256(
        body + _ser_string(script_data) + _ser_string(commitment_data)
    ).digest()


def _parse_body(proof):
    if len(proof) < 6 or proof[:4] != MAGIC:
        raise ValueError("invalid SLIP-19 proof magic")
    flags = proof[4]
    if flags & RESERVED_FLAGS:
        raise ValueError("reserved SLIP-19 flags set")

    stream = BytesIO(proof[5:])
    count = compact.read_from(stream)
    encoded_count = compact.to_bytes(count)
    if proof[5 : 5 + len(encoded_count)] != encoded_count:
        raise ValueError("non-minimal SLIP-19 ownership count")

    ids = []
    for _ in range(count):
        item = stream.read(32)
        if len(item) != 32:
            raise ValueError("invalid SLIP-19 ownership id")
        ids.append(item)
    body_len = 5 + len(encoded_count) + 32 * count
    return proof[:body_len], flags, ids, proof[body_len:]


def _parse_signature_proof(signature_proof):
    stream = BytesIO(signature_proof)
    script_sig = script.Script.read_from(stream)
    witness = script.Witness.read_from(stream)
    if stream.read(1):
        raise ValueError("invalid SLIP-19 signature proof")
    return script_sig, witness


def create_proof(key, script_type, script_pubkey, derivation, commitment_data, flags=0):
    """Builds a SLIP-19 proof for P2WPKH or P2TR."""
    if script_type not in (P2WPKH, P2TR):
        raise ValueError("unsupported SLIP-19 script type")
    if commitment_data is None:
        raise ValueError("missing commitment data")

    script_data = _script_bytes(script_pubkey)
    own_id = key.slip19_ownership_id(script_data)
    body = proof_body(flags, [own_id])
    digest = proof_digest(body, script_data, commitment_data)

    if script_type == P2WPKH:
        sig, pubkey = key.sign_slip19_p2wpkh(derivation, digest)
        expected = script.p2wpkh(pubkey)
        witness = script.witness_p2wpkh(sig, pubkey)
    else:
        sig, pubkey = key.sign_slip19_p2tr(derivation, digest)
        expected = script.p2tr(pubkey)
        witness = script.Witness([sig.serialize()])

    if expected.data != script_data:
        raise ValueError("derivation does not match scriptPubKey")
    return body + script.Script().serialize() + witness.serialize()


def parse_proof(proof):
    """Returns proof components without verifying the signature."""
    body, flags, ids, signature_proof = _parse_body(proof)
    script_sig, witness = _parse_signature_proof(signature_proof)
    return body, flags, ids, script_sig, witness


def verify_proof(proof, script_pubkey, commitment_data, require_confirmation=False):
    """Verifies a SLIP-19 P2WPKH/P2TR proof signature."""
    body, flags, _, script_sig, witness = parse_proof(proof)
    if require_confirmation and not flags & USER_CONFIRMATION:
        raise ValueError("SLIP-19 proof lacks user confirmation")
    if len(script_sig.data) != 0:
        raise ValueError("unsupported SLIP-19 scriptSig")

    script_data = _script_bytes(script_pubkey)
    script_type = script.Script(script_data).script_type()
    digest = proof_digest(body, script_data, commitment_data)

    if script_type == P2WPKH:
        if len(witness.items) != 2 or len(witness.items[0]) < 2:
            raise ValueError("invalid P2WPKH SLIP-19 witness")
        sig_data, pub_data = witness.items
        if sig_data[-1] != 1:
            raise ValueError("invalid P2WPKH SLIP-19 sighash")
        pubkey = ec.PublicKey.parse(pub_data)
        if script.p2wpkh(pubkey).data != script_data:
            raise ValueError("P2WPKH witness does not match scriptPubKey")
        if not pubkey.verify(ec.Signature.parse(sig_data[:-1]), digest):
            raise ValueError("invalid P2WPKH SLIP-19 signature")
        return True

    if script_type == P2TR:
        if len(witness.items) != 1 or len(witness.items[0]) != 64:
            raise ValueError("invalid P2TR SLIP-19 witness")
        pubkey = ec.PublicKey.from_xonly(script_data[2:])
        if not pubkey.schnorr_verify(ec.SchnorrSig(witness.items[0]), digest):
            raise ValueError("invalid P2TR SLIP-19 signature")
        return True

    raise ValueError("unsupported SLIP-19 script type")
