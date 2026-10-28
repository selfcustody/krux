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


def own_sp_output_type(out, sp_keys):
    """Returns "change", "self", or None for an SP output vs the wallet's keys.

    Only the unlabeled address and the BIP-352 change label 0 count as ours.
    A scanning wallet checks just the labels it handed out, so an output with
    any other label may never be found and is reviewed as a spend instead.
    """
    if sp_keys is None:
        return None

    sp_data = out.sp_data
    if sp_data.scan_key != sp_keys.scan_pubkey:
        return None

    label = out.sp_label
    if label is None:
        expected_spend = sp_keys.spend_pubkey
    elif label == 0:
        from embit.silent_payments.sp import apply_label

        expected_spend = apply_label(sp_keys.spend_pubkey, sp_keys.scan_privkey, 0)
    else:
        return None

    if sp_data.spend_key != expected_spend:
        return None
    return "self" if label is None else "change"


def output_address(out, script_pubkey, wallet):
    """Returns the human-readable destination address for a PSBT output."""
    if out.sp_data is not None:
        from embit.silent_payments.sp import encode_silent_payment_address

        return encode_silent_payment_address(
            out.sp_data.scan_key, out.sp_data.spend_key, wallet.which_network()
        )
    return script_pubkey.address(network=wallet.key.network)


def validate(psbt):
    """Raises ValueError if the signed PSBT is not a valid BIP-375 hand-off.

    Krux acts as the BIP-375 Signer: it hands back an unfinalized PSBT carrying
    the derived Taproot output scripts plus the global ECDH shares and DLEQ
    proofs, so the coordinator can verify the outputs before finalizing.
    Inputs are not checked here: sign() clears the ones this seed owns, and
    an input another signer finalized is left as it came.
    """
    for i, out in enumerate(psbt.outputs):
        if out.sp_data is None:
            continue
        script = out.script_pubkey
        if script is None or len(script.data) != 34 or script.data[:2] != b"\x51\x20":
            raise ValueError("output %d missing Taproot script" % i)
        scan_key = out.sp_data.scan_key.sec()
        if scan_key not in psbt.sp_ecdh_shares:
            raise ValueError("output %d missing ECDH share" % i)
        if scan_key not in psbt.sp_dleq_proofs:
            raise ValueError("output %d missing DLEQ proof" % i)


def validate_eligibility(policy):
    """Raises ValueError if the policy is not BIP-352 eligible for SP-sending.

    Krux only supports single-party SP sends, so any script policy is refused.
    The "m" and "miniscript" keys are the same markers psbt.is_multisig() and
    psbt.is_miniscript() test for; they are checked inline rather than by
    importing those helpers, which would create a psbt <-> silent_payments
    import cycle.
    """
    policy = policy or {}
    if "m" in policy or "miniscript" in policy:
        raise ValueError(
            "Silent Payments are not supported with multisig or miniscript"
        )
    if policy.get("type") not in (P2PKH, P2WPKH, P2SH_P2WPKH, P2TR):
        raise ValueError(
            "Silent Payments require P2PKH, P2WPKH, P2SH-P2WPKH, or P2TR inputs"
        )


def derive_scripts(psbt, root):
    """Returns {output index: Script} for the PSBT's Silent Payment outputs.

    Runs while loading, so the review screen can show the Taproot address each
    SP output lands on and a PSBT this seed cannot sign is rejected before the
    user reviews it: embit refuses it unless every BIP-352 eligible input
    belongs to root and the BIP-375 checks pass (e.g. the Segwit v>1 input ban).

    Only the scripts are derived here. The DLEQ proofs, the expensive part,
    are still computed once, inside sign_with().
    """
    from embit.silent_payments.psbt import SPFieldError, SPValidationError

    try:
        return psbt.sp_output_scripts(root)
    except (SPValidationError, SPFieldError) as e:
        raise ValueError(str(e))
