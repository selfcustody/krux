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
"""Silent Payments (BIP-352 / BIP-375) helpers for Krux.

This module centralizes the sender-side Silent Payment logic that the rest of
the firmware needs: detection, address rendering for review screens, and
BIP-375 validation. Keeping it isolated means src/krux/psbt.py stays focused
on the existing v0/v2 signing pipeline, and a future receive-side module (if
ever) does not need to disentangle send-only assumptions from shared code.

Imports from the SP-aware Embit fork are lazy so SP-naive PSBT flows do not
pay the module-load cost on K210.
"""

from .key import P2PKH, P2SH_P2WPKH, P2TR, P2WPKH


def has_sp_outputs(psbt):
    """Returns True if any output on the PSBT carries BIP-375 sp_data."""
    return any(getattr(out, "sp_data", None) is not None for out in psbt.outputs)


def address_from_output(out, network):
    """Encodes the sp1/tsp1 address (BIP-352) for an output's sp_data.

    Used during review so the user verifies the human-readable recipient
    address, not the derived P2TR script that lands in script_pubkey at
    signing time.
    """
    from embit import bech32

    sp_data = out.sp_data
    payload = sp_data.scan_key.sec() + sp_data.spend_key.sec()
    data = bech32.convertbits(payload, 8, 5)
    hrp = "sp" if network.get("bech32") == "bc" else "tsp"
    return bech32.bech32_encode(bech32.Encoding.BECH32M, hrp, [0] + data)


def output_address(psbt, index, out, network):
    """Returns the human-readable destination address for a PSBT output.

    For Silent Payment outputs (sp_data set), always returns the sp1/tsp1
    address — even after derivation has populated script_pubkey — so the user
    never verifies against a derived P2TR they cannot independently recognize.
    """
    if getattr(out, "sp_data", None) is not None:
        return address_from_output(out, network)
    return psbt.tx.vout[index].script_pubkey.address(network=network)


def validate(psbt, skip_output_scripts=True):
    """Runs the BIP-375 validator and remaps SPValidationError to ValueError.

    skip_output_scripts is True at load time because received SP PSBTs
    typically have empty script_pubkeys until the sender derives them. The
    sender re-runs full validation after derivation while signing.
    """
    from embit.silent_payments import BIP375Validator, SPValidationError

    try:
        BIP375Validator(psbt).validate(skip_output_scripts=skip_output_scripts)
    except SPValidationError as e:
        raise ValueError("Silent Payment validation failed: %s" % e)


def validate_eligibility(policy):
    """Rejects policies that are not BIP-352 eligible for SP-sending.

    BIP-352 eligible single-key input types are P2PKH, P2WPKH, P2SH-P2WPKH and
    P2TR. P2TR covers both ordinary BIP-86 inputs and BIP-376 spend-from inputs
    (a previously received SP UTXO funding a new SP output); per-input NUMS and
    Segwit>v1 exclusions are enforced downstream by get_eligible_inputs.

    Multisig and miniscript are rejected: SP derives the recipient script from
    the sum of input private keys, which requires a single signer with access to
    every contributing key. They are detected structurally (presence of ``m`` or
    ``miniscript`` keys in the policy dict) to avoid importing the predicate
    helpers from psbt.py, which would create a circular import.
    """
    if policy and ("m" in policy or "miniscript" in policy):
        raise ValueError(
            "Silent Payments are not supported with multisig or miniscript"
        )
    policy_type = policy.get("type") if policy else None
    if policy_type not in (P2PKH, P2WPKH, P2SH_P2WPKH, P2TR):
        raise ValueError(
            "Silent Payments require P2PKH, P2WPKH, P2SH-P2WPKH, or P2TR inputs"
        )
