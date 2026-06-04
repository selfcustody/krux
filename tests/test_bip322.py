import pytest

from .pages.home_pages.test_home import tdata

P2PKH_DERIV = "m/44h/0h/0h/0/0"
P2SH_P2WPKH_DERIV = "m/49h/0h/0h/0/0"
P2WPKH_DERIV = "m/84h/0h/0h/0/0"
P2TR_DERIV = "m/86h/0h/0h/0/0"

MESSAGE = b"krux+bip322"


@pytest.fixture
def scriptpubkey_for():
    def _spk(pub, script_type):
        from embit import script

        if script_type == "p2pkh":
            return script.p2pkh(pub)
        if script_type == "p2sh-p2wpkh":
            return script.p2sh(script.p2wpkh(pub))
        if script_type == "p2wpkh":
            return script.p2wpkh(pub)
        if script_type == "p2tr":
            return script.p2tr(pub)
        return None

    return _spk


@pytest.fixture
def unsigned_non_bip322_psbt(scriptpubkey_for):
    def _build(key, derivation_str, script_type, message):
        from embit.psbt import PSBT
        from embit.script import Script
        from embit.transaction import (
            Transaction,
            TransactionInput,
            TransactionOutput,
        )

        tx = Transaction(
            version=2,
            vin=[
                TransactionInput(
                    txid=b"\x11" * 32,
                    vout=0,
                    script_sig=Script(b""),
                    sequence=0xFFFFFFFF,
                )
            ],
            vout=[
                TransactionOutput(
                    value=100_000,
                    script_pubkey=Script(b"\x00\x14" + b"\x00" * 20),
                )
            ],
            locktime=0,
        )
        return PSBT(tx)

    return _build


@pytest.fixture
def unsigned_bip322_psbt(scriptpubkey_for):
    # Accepts either:
    #   - a krux Key
    #   - a raw `ec.PrivateKey`
    def _build(key, derivation_str, script_type, message):
        from embit import bip32
        from embit.psbt import PSBT, DerivationPath
        from krux.bip322 import (
            PSBT_GLOBAL_GENERIC_SIGNED_MESSAGE,
            build_bip322_txs,
        )

        if hasattr(key, "root"):
            derivation = bip32.parse_path(derivation_str)
            pub = key.root.derive(derivation).to_public().key
            fingerprint = key.root.my_fingerprint
        else:
            pub = key.get_public_key()
            derivation = None
            fingerprint = None
        spk = scriptpubkey_for(pub, script_type)

        to_spend, to_sign = build_bip322_txs(message, spk)

        # embit's PSBT.__init__ uses a `unknown={}` — mutating
        # `psbt.unknown`. It leaks the entry into every later test suite
        psbt = PSBT(to_sign, unknown={PSBT_GLOBAL_GENERIC_SIGNED_MESSAGE: message})
        psbt.inputs[0].witness_utxo = to_spend.vout[0]

        if fingerprint is not None:
            derivation_path = DerivationPath(fingerprint, derivation)
            if script_type == "p2tr":
                psbt.inputs[0].taproot_bip32_derivations[pub] = ([], derivation_path)
            else:
                psbt.inputs[0].bip32_derivations[pub] = derivation_path

        return psbt

    return _build


def test_check_bip322_psbt(mocker, m5stickv, tdata, unsigned_bip322_psbt):
    from krux.bip322 import check_bip322_psbt

    # (derivation, script_type)
    cases = [
        (P2PKH_DERIV, "p2pkh"),
        (P2SH_P2WPKH_DERIV, "p2sh-p2wpkh"),
        (P2WPKH_DERIV, "p2wpkh"),
        (P2TR_DERIV, "p2tr"),
    ]
    key = tdata.SINGLESIG_SIGNING_KEY
    for i, case in enumerate(cases):
        print("test_check_bip322_psbt: case %d, script=%s" % (i, case[1]))
        psbt = unsigned_bip322_psbt(key, case[0], case[1], MESSAGE)
        assert check_bip322_psbt(psbt)


def test_check_bip322_fail(mocker, m5stickv, tdata, unsigned_non_bip322_psbt):
    from krux.bip322 import check_bip322_psbt

    cases = [
        (P2PKH_DERIV, "p2pkh"),
        (P2SH_P2WPKH_DERIV, "p2sh-p2wpkh"),
        (P2WPKH_DERIV, "p2wpkh"),
        (P2TR_DERIV, "p2tr"),
    ]
    key = tdata.SINGLESIG_SIGNING_KEY
    for i, case in enumerate(cases):
        print("test_check_bip322_psbt: case %d, script=%s" % (i, case[1]))
        psbt = unsigned_non_bip322_psbt(key, case[0], case[1], MESSAGE)
        assert not check_bip322_psbt(psbt)


def test_bip322_vectors(mocker, m5stickv, unsigned_bip322_psbt):
    from embit import ec, script
    from embit.script import Witness
    from embit.transaction import SIGHASH
    from krux.bip322 import finalize_simple

    # Spec raw WIFs
    # (wif, script_type, expected_address, messages)
    cases = [
        (
            "L3VFeEujGtevx9w18HD1fhRbCH67Az2dpCymeRE1SoPK6XQtaN2k",
            "p2wpkh",
            "bc1q9vza2e8x573nczrlzms0wvx3gsqjx7vavgkx0l",
            [b"", b"Hello World"],
        ),
        (
            "KyrSGCFPhqZMjCe5fNTYddiLMp4tMj4gLKuJ26TsB2rvr1VJGPbt",
            "p2tr",
            "bc1pss0zhytly75awhm6x2hhvd5lnzv3vssgrf9axfheq8ldyzn88ges79fler",
            [b"No prefix fallback"],
        ),
    ]

    for i, case in enumerate(cases):
        wif, script_type, expected_addr, messages = case
        prv = ec.PrivateKey.from_wif(wif)
        pub = prv.get_public_key()
        if script_type == "p2wpkh":
            spk = script.p2wpkh(pub)
        if script_type == "p2tr":
            spk = script.p2tr(pub)
        assert spk.address() == expected_addr

        for j, message in enumerate(messages):
            print("Case %d (%s): message=%s" % (i, script_type, message))

            psbt = unsigned_bip322_psbt(prv, None, script_type, message)
            to_sign = psbt.tx

            if script_type == "p2wpkh":
                code_script = script.p2pkh_from_p2wpkh(spk)
                sighash = to_sign.sighash_segwit(
                    input_index=0,
                    script_pubkey=code_script,
                    value=0,
                    sighash=SIGHASH.ALL,
                )
                sig = prv.sign(sighash).serialize() + bytes([SIGHASH.ALL])
                psbt.inputs[0].partial_sigs[pub] = sig
            if script_type == "p2tr":
                sighash = to_sign.sighash_taproot(
                    input_index=0,
                    script_pubkeys=[spk],
                    values=[0],
                    sighash=SIGHASH.ALL,
                )
                tweaked_prv = prv.taproot_tweak(b"")
                sig = tweaked_prv.schnorr_sign(sighash).serialize() + bytes(
                    [SIGHASH.ALL]
                )
                psbt.inputs[0].taproot_key_sig = sig
                psbt.inputs[0].final_scriptwitness = Witness([sig])

            finalize_simple(psbt)

            witness = psbt.inputs[0].final_scriptwitness
            if script_type == "p2wpkh":
                assert len(witness.items) == 2
                sig_with_sighash, pub_bytes = witness.items
                assert sig_with_sighash[-1] == SIGHASH.ALL
                assert pub_bytes == pub.sec()
                sig_obj = ec.Signature.parse(sig_with_sighash[:-1])
                assert pub.verify(sig_obj, sighash)
            if script_type == "p2tr":
                assert len(witness.items) == 1
                assert len(witness.items[0]) == 65
                assert witness.items[0][-1] == SIGHASH.ALL
                tweaked_pub = pub.taproot_tweak(b"")
                assert tweaked_pub.schnorr_verify(
                    ec.SchnorrSig(witness.items[0][:-1]), sighash
                )


def test_sign_finalizes(mocker, m5stickv, tdata, unsigned_bip322_psbt):
    from krux import bip322

    # (derivation, script_type, has_scriptsig, has_witness)
    cases = [
        (P2PKH_DERIV, "p2pkh"),
        (P2SH_P2WPKH_DERIV, "p2sh-p2wpkh"),
        (P2WPKH_DERIV, "p2wpkh"),
        (P2TR_DERIV, "p2tr"),
    ]
    key = tdata.SINGLESIG_SIGNING_KEY
    for i, case in enumerate(cases):
        print("Case %d, script=%s" % (i, case[1]))
        psbt = unsigned_bip322_psbt(key, case[0], case[1], MESSAGE)
        bip322.sign(psbt, key)

        inp = psbt.inputs[0]
        if case[1] in ("p2pkh", "p2sh-p2wpkh"):
            assert inp.final_scriptsig is not None
            assert len(inp.final_scriptsig.data) > 0
        else:
            assert inp.final_scriptsig is None or len(inp.final_scriptsig.data) == 0

        if case[1] in ("p2sh-p2wpkh", "p2wpkh", "p2tr"):
            assert inp.final_scriptwitness is not None
            assert len(inp.final_scriptwitness.items) >= 1
        else:
            assert (
                inp.final_scriptwitness is None
                or len(inp.final_scriptwitness.items) == 0
            )


def test_sign_rejects_non_bip322_psbt(
    mocker, m5stickv, tdata, unsigned_non_bip322_psbt
):
    from krux.bip322 import sign

    psbt = unsigned_non_bip322_psbt(None, None, None, MESSAGE)
    with pytest.raises(ValueError, match="Not a BIP-322 PSBT"):
        sign(psbt, tdata.SINGLESIG_SIGNING_KEY)


def test_sign_raises_when_no_matching_derivation(
    mocker, m5stickv, tdata, unsigned_bip322_psbt
):
    from collections import OrderedDict
    from krux.bip322 import sign

    key = tdata.SINGLESIG_SIGNING_KEY
    psbt = unsigned_bip322_psbt(key, P2WPKH_DERIV, "p2wpkh", MESSAGE)
    pub, deriv = next(iter(psbt.inputs[0].bip32_derivations.items()))
    fake = type(deriv)(b"\xff" * 4, deriv.derivation)
    psbt.inputs[0].bip32_derivations = OrderedDict([(pub, fake)])
    with pytest.raises(ValueError, match="no derivation matching"):
        sign(psbt, key)


def test_finalize_simple_raises_without_partial_sigs(
    mocker, m5stickv, tdata, unsigned_bip322_psbt
):
    from krux.bip322 import finalize_simple

    key = tdata.SINGLESIG_SIGNING_KEY
    psbt = unsigned_bip322_psbt(key, P2WPKH_DERIV, "p2wpkh", MESSAGE)
    assert not psbt.inputs[0].partial_sigs
    assert psbt.inputs[0].final_scriptwitness is None
    with pytest.raises(ValueError, match="no signatures to finalize"):
        finalize_simple(psbt)


def test_check_bip322_psbt_rejects_wrong_vin_count(
    mocker, m5stickv, tdata, unsigned_bip322_psbt
):
    from krux.bip322 import check_bip322_psbt

    key = tdata.SINGLESIG_SIGNING_KEY
    psbt = unsigned_bip322_psbt(key, P2WPKH_DERIV, "p2wpkh", MESSAGE)
    psbt.inputs.append(psbt.inputs[0])
    assert not check_bip322_psbt(psbt)


def test_check_bip322_psbt_rejects_wrong_input_vout(
    mocker, m5stickv, tdata, unsigned_bip322_psbt
):
    from krux.bip322 import check_bip322_psbt

    key = tdata.SINGLESIG_SIGNING_KEY
    psbt = unsigned_bip322_psbt(key, P2WPKH_DERIV, "p2wpkh", MESSAGE)
    psbt.inputs[0].vout = 1
    assert not check_bip322_psbt(psbt)


def test_check_bip322_psbt_rejects_nonzero_output_value(
    mocker, m5stickv, tdata, unsigned_bip322_psbt
):
    from krux.bip322 import check_bip322_psbt

    key = tdata.SINGLESIG_SIGNING_KEY
    psbt = unsigned_bip322_psbt(key, P2WPKH_DERIV, "p2wpkh", MESSAGE)
    psbt.outputs[0].value = 1
    assert not check_bip322_psbt(psbt)


def test_check_bip322_psbt_rejects_non_op_return_output(
    mocker, m5stickv, tdata, unsigned_bip322_psbt
):
    from embit.script import Script
    from krux.bip322 import check_bip322_psbt

    key = tdata.SINGLESIG_SIGNING_KEY
    psbt = unsigned_bip322_psbt(key, P2WPKH_DERIV, "p2wpkh", MESSAGE)
    psbt.outputs[0].script_pubkey = Script(b"\x00\x14" + b"\x00" * 20)
    assert not check_bip322_psbt(psbt)


def test_check_bip322_psbt_rejects_missing_utxo(
    mocker, m5stickv, tdata, unsigned_bip322_psbt
):
    from krux.bip322 import check_bip322_psbt

    key = tdata.SINGLESIG_SIGNING_KEY
    psbt = unsigned_bip322_psbt(key, P2WPKH_DERIV, "p2wpkh", MESSAGE)
    psbt.inputs[0].witness_utxo = None
    assert not check_bip322_psbt(psbt)


def test_check_bip322_psbt_accepts_non_witness_utxo(
    mocker, m5stickv, tdata, unsigned_bip322_psbt
):
    from krux.bip322 import build_bip322_txs, check_bip322_psbt

    key = tdata.SINGLESIG_SIGNING_KEY
    psbt = unsigned_bip322_psbt(key, P2PKH_DERIV, "p2pkh", MESSAGE)
    spk = psbt.inputs[0].witness_utxo.script_pubkey
    to_message, _ = build_bip322_txs(MESSAGE, spk)
    psbt.inputs[0].witness_utxo = None
    psbt.inputs[0].non_witness_utxo = to_message
    assert check_bip322_psbt(psbt)


def test_serialize_bip322_zeros_version_and_sequence(
    mocker, m5stickv, tdata, unsigned_bip322_psbt
):
    from krux import bip322

    key = tdata.SINGLESIG_SIGNING_KEY
    psbt = unsigned_bip322_psbt(key, P2WPKH_DERIV, "p2wpkh", MESSAGE)
    bip322.sign(psbt, key)
    raw = bip322.serialize_bip322(psbt)
    assert raw[8:12] == b"\x00\x00\x00\x00"
    seq_pos = 8 + 4 + 1 + 32 + 4 + 1
    assert raw[seq_pos : seq_pos + 4] == b"\x00\x00\x00\x00"


def test_finalize_simple_raises_on_unsupported_script(
    mocker, m5stickv, tdata, unsigned_bip322_psbt
):
    from embit.script import Script
    from embit.transaction import TransactionOutput
    from krux.bip322 import finalize_simple

    key = tdata.SINGLESIG_SIGNING_KEY
    psbt = unsigned_bip322_psbt(key, P2WPKH_DERIV, "p2wpkh", MESSAGE)
    real_pub = next(iter(psbt.inputs[0].bip32_derivations))
    psbt.inputs[0].partial_sigs[real_pub] = b"\xaa" * 71
    psbt.inputs[0].witness_utxo = TransactionOutput(
        value=0,
        script_pubkey=Script(b"\x51\x20" + b"\x00" * 32),
    )
    with pytest.raises(ValueError, match="Unsupported script"):
        finalize_simple(psbt)
