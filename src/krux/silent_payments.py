# The MIT License (MIT)

# Copyright (c) 2026 Krux contributors

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
from .key import P2PKH, P2SH_P2WPKH, P2TR, P2WPKH


def has_sp_outputs(psbt):
    """Returns True if any output on the PSBT carries BIP-375 sp_data."""
    return any(getattr(out, "sp_data", None) is not None for out in psbt.outputs)


def address_from_output(out, network):
    """Returns the BIP-352 sp1/tsp1 bech32m address for an output's sp_data."""
    from embit import bech32

    sp_data = out.sp_data
    payload = sp_data.scan_key.sec() + sp_data.spend_key.sec()
    data = bech32.convertbits(payload, 8, 5)
    hrp = "sp" if network.get("bech32") == "bc" else "tsp"
    return bech32.bech32_encode(bech32.Encoding.BECH32M, hrp, [0] + data)


def own_sp_output_type(out, sp_keys):
    """Returns "change", "self", or None for an SP output vs the wallet's keys."""
    if sp_keys is None:
        return None

    sp_data = out.sp_data
    if sp_data.scan_key != sp_keys.scan_privkey.get_public_key():
        return None

    label = out.sp_label
    if label is None:
        expected_spend = sp_keys.spend_pubkey
    else:
        from embit import ec
        from embit.hashes import tagged_hash
        from embit.util import secp256k1

        tweak = tagged_hash(
            "BIP0352/Label",
            sp_keys.scan_privkey.secret + label.to_bytes(4, "big"),
        )
        expected_spend = ec.PublicKey(
            secp256k1.ec_pubkey_add(
                secp256k1.ec_pubkey_parse(sp_keys.spend_pubkey.sec()), tweak
            )
        )

    if sp_data.spend_key != expected_spend:
        return None
    return "change" if label == 0 else "self"


def output_address(psbt, index, out, network):
    """Returns the human-readable destination address for a PSBT output."""
    if getattr(out, "sp_data", None) is not None:
        return address_from_output(out, network)
    return psbt.tx.vout[index].script_pubkey.address(network=network)


def validate(psbt, skip_output_scripts=True):
    """Runs the BIP-375 validator, remapping SPValidationError to ValueError."""
    from embit.silent_payments import BIP375Validator, SPValidationError

    try:
        BIP375Validator(psbt).validate(skip_output_scripts=skip_output_scripts)
    except SPValidationError as e:
        raise ValueError("Silent Payment validation failed: %s" % e)


def validate_eligibility(policy):
    """Raises ValueError if the policy is not BIP-352 eligible for SP-sending."""
    if policy and ("m" in policy or "miniscript" in policy):
        raise ValueError(
            "Silent Payments are not supported with multisig or miniscript"
        )
    policy_type = policy.get("type") if policy else None
    if policy_type not in (P2PKH, P2WPKH, P2SH_P2WPKH, P2TR):
        raise ValueError(
            "Silent Payments require P2PKH, P2WPKH, P2SH-P2WPKH, or P2TR inputs"
        )
