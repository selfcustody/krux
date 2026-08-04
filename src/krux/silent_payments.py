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


def output_address(psbt, index, out, network):
    """Returns the human-readable destination address for a PSBT output."""
    if out.sp_data is not None:
        from embit.silent_payments.sp import encode_silent_payment_address

        # encode_silent_payment_address only distinguishes "main" from the rest
        net_name = "main" if network.get("bech32") == "bc" else "test"
        return encode_silent_payment_address(
            out.sp_data.scan_key, out.sp_data.spend_key, network=net_name
        )
    return psbt.tx.vout[index].script_pubkey.address(network=network)


def validate(psbt):
    """Raises ValueError if the signed PSBT is not a valid BIP-375 hand-off.

    Krux acts as the BIP-375 Signer: it hands back an unfinalized PSBT carrying
    the derived Taproot output scripts plus the global ECDH shares and DLEQ
    proofs, so the coordinator can verify the outputs before finalizing.
    """
    for i, inp in enumerate(psbt.inputs):
        if inp.final_scriptwitness is not None or inp.final_scriptsig is not None:
            raise ValueError("input %d must not be finalized" % i)

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


def check_inputs_owned(psbt, root):
    """Raises ValueError unless every BIP-352 eligible input belongs to root.

    This is the BIP32-only half of embit's derive_sp_outputs() ownership check,
    so a PSBT this seed cannot sign is rejected while loading instead of after
    the user has reviewed and approved it. No ECDH share or DLEQ proof is
    computed here -- that happens once, inside sign_with().

    validate_sp() runs here too (e.g. BIP-375's Segwit v>1 input ban), so
    those checks also reject at load instead of surfacing later, mid-sign.
    """
    from embit.psbt import derive_hdkey, resolve_signing_root
    from embit.silent_payments.psbt import SPValidationError
    from embit.silent_payments.signing import resolve_input_privkey
    from embit.silent_payments.sp import get_eligible_inputs

    try:
        psbt.validate_sp()
        eligible = get_eligible_inputs(psbt.inputs)
    except SPValidationError as e:
        raise ValueError(str(e))
    if not eligible:
        raise ValueError(
            "Silent Payment send requires at least one eligible input "
            "(P2PKH, P2SH-P2WPKH, P2WPKH, or P2TR)"
        )

    fingerprint, _, root = resolve_signing_root(root)
    for i in eligible:
        if (
            resolve_input_privkey(psbt.inputs[i], root, fingerprint, derive_hdkey)
            is None
        ):
            raise ValueError(
                "Silent Payment signing failed: input %d is not controlled by "
                "this seed; multi-party sends are not supported" % i
            )
