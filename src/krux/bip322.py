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

PSBT_GLOBAL_GENERIC_SIGNED_MESSAGE = b"\x09"
OP_RETURN = b"\x6a"


def build_bip322_txs(message, spk):
    """BIP-322 to_spend and to_sign txs per spec"""
    # keep version=0 and sequence=0 — embit's `or`-fallbacks at
    # psbt.py:200/:667 substitute defaults.
    from embit import hashes
    from embit.script import Script
    from embit.transaction import (
        Transaction,
        TransactionInput,
        TransactionOutput,
    )

    msg_hash = hashes.tagged_hash("BIP0322-signed-message", message)
    to_spend = Transaction(
        version=0,
        vin=[
            TransactionInput(
                txid=b"\x00" * 32,
                vout=0xFFFFFFFF,
                script_sig=Script(b"\x00\x20" + msg_hash),
                sequence=0,
            )
        ],
        vout=[TransactionOutput(value=0, script_pubkey=spk)],
        locktime=0,
    )
    to_sign = Transaction(
        version=0,
        vin=[
            TransactionInput(
                txid=to_spend.txid(),
                vout=0,
                script_sig=Script(b""),
                sequence=0,
            )
        ],
        vout=[TransactionOutput(value=0, script_pubkey=Script(OP_RETURN))],
        locktime=0,
    )
    return to_spend, to_sign


def check_bip322_psbt(psbt):
    """Detect BIP-322 PSBT fake tx"""
    if PSBT_GLOBAL_GENERIC_SIGNED_MESSAGE not in psbt.unknown:
        return False
    message = psbt.unknown[PSBT_GLOBAL_GENERIC_SIGNED_MESSAGE]

    tx = psbt.tx
    if len(tx.vin) != 1 or len(tx.vout) != 1:
        return False
    if tx.vin[0].vout != 0:
        return False
    if tx.vout[0].value != 0:
        return False
    if tx.vout[0].script_pubkey.data != OP_RETURN:
        return False

    # prevout scriptpubkey from witness or legacy utxo (embit/psbt.py L214);
    spk = psbt.inputs[0].script_pubkey
    if spk is None:
        return False

    to_spend, _ = build_bip322_txs(message, spk)
    return tx.vin[0].txid == to_spend.txid()


def sign(psbt, key):
    """Sign and finalize a BIP-322 `smp` PSBT"""
    if not check_bip322_psbt(psbt):
        raise ValueError("Not a BIP-322 PSBT")

    from embit import script
    from embit.script import Witness
    from embit.transaction import SIGHASH

    message = psbt.unknown[PSBT_GLOBAL_GENERIC_SIGNED_MESSAGE]
    inp = psbt.inputs[0]
    spk = inp.script_pubkey
    script_type = spk.script_type()

    if script_type == "p2sh":
        # Sparrow resolves P2SH_P2WPKH via PSBTInput.getScriptType()
        # when redeem is P2WPKH (drongo psbt/PSBTInput.java ~L1041)
        script_type = "p2sh-p2wpkh"

    _, to_sign = build_bip322_txs(message, spk)

    fingerprint = key.root.my_fingerprint
    derivations = (
        inp.taproot_bip32_derivations
        if script_type == "p2tr"
        else inp.bip32_derivations
    )

    # check for some wrong deriv path with same-fingerprint
    pub = None
    prv = None
    for _pub, _deriv in derivations.items():
        _built = None
        _d = _deriv[1] if isinstance(_deriv, tuple) else _deriv
        if _d.fingerprint == fingerprint:
            _derived = key.root.derive(_d.derivation)
            _derived_pub = _derived.get_public_key()
            if script_type == "p2tr":
                if _derived_pub.xonly() == _pub.xonly():
                    _built = script.p2tr(_pub)

            if _derived_pub == _pub:
                if script_type == "p2pkh":
                    _built = script.p2pkh(_pub)
                if script_type == "p2wpkh":
                    _built = script.p2wpkh(_pub)
                if script_type == "p2sh-p2wpkh":
                    _built = script.p2sh(script.p2wpkh(_pub))

            if _built is not None and _built.data == spk.data:
                pub = _pub
                prv = _derived.key
                break

    if prv is None:
        raise ValueError("Key not match PSBT")

    # Sparrow uses BIP-137 for legacy and our sign_message_ui routes those
    # PSBTs to bip137 (i.e., they even allow in UI). We kept the suggested
    # impl from spec (maybe another watch-wallet could impl full spec)
    if script_type == "p2pkh":
        h = to_sign.sighash_legacy(
            input_index=0,
            script_pubkey=spk,
            sighash=SIGHASH.ALL,
        )
        sig = prv.sign(h).serialize() + bytes([SIGHASH.ALL])
        inp.partial_sigs[pub] = sig

    if script_type in ("p2wpkh", "p2sh-p2wpkh"):
        _script = script.p2pkh_from_p2wpkh(script.p2wpkh(pub))
        h = to_sign.sighash_segwit(
            input_index=0,
            script_pubkey=_script,
            value=0,
            sighash=SIGHASH.ALL,
        )
        sig = prv.sign(h).serialize() + bytes([SIGHASH.ALL])
        inp.partial_sigs[pub] = sig

    if script_type == "p2tr":
        h = to_sign.sighash_taproot(
            input_index=0,
            script_pubkeys=[spk],
            values=[0],
            sighash=SIGHASH.ALL,
        )
        sig = prv.taproot_tweak(b"").schnorr_sign(h).serialize() + bytes([SIGHASH.ALL])
        inp.taproot_key_sig = sig
        inp.final_scriptwitness = Witness([sig])

    finalize_simple(psbt, pub)
    return psbt


def serialize_bip322(psbt):
    """Serialize a BIP-322 fake PSBT"""
    # embit's `or` fallback properties at psbt.py:667/:200 rewrite version
    # and sequence during serialize, breaking Sparrow's
    # `PSBTInput.verifySignatures`. We need first rewrite them back to zero
    # in-place:
    #
    # - fail unless the bytes still match embit's defaults (refuse to zeroize version)
    # - `smp` prefix PSBT is fixed (0x3D) -- one input, one output, OP_RETURN, ...
    # - no need to check, until we need to update, with varint checks on bit
    #   flag tx size (will never be >= 0xFD)
    raw = psbt.serialize()
    pos = 8

    # Guard against (version=2)
    ver = int.from_bytes(raw[pos : pos + 4], "little")
    if ver != 2:
        raise ValueError("PSBT mismatch version: %s" % ver)
    raw = raw[:pos] + b"\x00\x00\x00\x00" + raw[pos + 4 :]

    # Guards against silent corruption on (sequence=0xFFFFFFFF)
    # if embit's PSBT shifts upstream
    seq_pos = pos + 4 + 1 + 32 + 4 + 1
    if raw[seq_pos : seq_pos + 4] != b"\xff\xff\xff\xff":
        raise ValueError("PSBT mismatch seq: on 0xFFFFFFFF")

    # Apply sequence=0x00000000
    return raw[:seq_pos] + b"\x00\x00\x00\x00" + raw[seq_pos + 4 :]


def finalize_simple(psbt, pub):
    """finalize BIP-322 simple-form for the partial_sig matching `pub`"""
    from embit import script
    from embit.script import Script, Witness

    inp = psbt.inputs[0]

    # Taproot key-path signature is already populated
    # in `inp.final_scriptwitness`. Nothing more to do.
    if inp.final_scriptwitness is None:
        if not inp.partial_sigs:
            raise ValueError("PSBT no signatures")

        # The caller has already matched `pub` to the wallet fingerprint via
        # `bip32_derivations` in `sign()`. Other partial_sigs (e.g. from
        # co-signers or stray entries) are ignored.
        sig = inp.partial_sigs.get(pub)
        if sig is None:
            raise ValueError("Key not match")
        spk = inp.script_pubkey.data

        # P2WPKH: OP_0 PUSH20 <pkh>
        if len(spk) == 22 and spk[:2] == b"\x00\x14":
            inp.final_scriptwitness = Witness([sig, pub.sec()])

        # P2SH-P2WPKH: OP_HASH160 PUSH20 <sh> OP_EQUAL.
        elif len(spk) == 23 and spk[:2] == b"\xa9\x14" and spk[-1] == 0x87:
            inp.final_scriptwitness = Witness([sig, pub.sec()])
            redeem = script.p2wpkh(pub).data
            inp.final_scriptsig = Script(bytes([len(redeem)]) + redeem)

        # P2PKH: OP_DUP OP_HASH160 PUSH20 <pkh> OP_EQUALVERIFY OP_CHECKSIG.
        elif len(spk) == 25 and spk[:3] == b"\x76\xa9\x14" and spk[-2:] == b"\x88\xac":
            sec = pub.sec()
            inp.final_scriptsig = Script(
                bytes([len(sig)]) + sig + bytes([len(sec)]) + sec
            )

        else:
            raise ValueError("Unsupported script")

    return inp.final_scriptsig, inp.final_scriptwitness
