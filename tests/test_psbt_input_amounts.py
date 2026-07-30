"""Regression coverage for PSBT input amount verification.

The amount shown on the review screen must be the same amount the signer
commits to, and any previous transaction attached to an input must really
hash to the outpoint being spent.
"""

import pytest
from tests.shared_mocks import MockFile, mock_open

TEST_MNEMONIC = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"


def _kv(key, value):
    """Serializes a PSBT key/value pair"""
    from embit import compact

    return compact.to_bytes(len(key)) + key + compact.to_bytes(len(value)) + value


def _root():
    from embit import bip32, bip39
    from embit.networks import NETWORKS

    seed = bip39.mnemonic_to_seed(TEST_MNEMONIC)
    return bip32.HDKey.from_seed(seed, version=NETWORKS["test"]["xprv"])


def _key_at(root, path):
    """Returns the public key and its derivation path record"""
    from embit.bip32 import parse_path
    from embit.psbt import DerivationPath

    derivation = parse_path(path)
    pubkey = root.derive(derivation).to_public().key
    return pubkey, DerivationPath(root.my_fingerprint, derivation)


def _wallet():
    from embit.networks import NETWORKS
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet

    return Wallet(Key(TEST_MNEMONIC, TYPE_SINGLESIG, NETWORKS["test"]))


def test_rejects_fabricated_non_witness_utxo(m5stickv):
    """A previous tx that does not hash to the outpoint must be refused.

    Legacy sighashes do not commit to the input amount, so without this check
    a fabricated previous tx yields a signature that is valid against the real
    UTXO while the device displays an understated fee.
    """
    from embit import script
    from embit.psbt import PSBT
    from embit.transaction import Transaction, TransactionInput, TransactionOutput
    from krux.psbt import PSBTSigner
    from krux.qr import FORMAT_NONE

    root = _root()
    pubkey, derivation = _key_at(root, "m/44h/1h/0h/0/0")
    script_pubkey = script.p2pkh(pubkey)

    real_prev = Transaction(
        vin=[TransactionInput(b"\x22" * 32, 0)],
        vout=[TransactionOutput(100000000, script_pubkey)],
    )
    # Same scriptPubKey, understated value, so a different txid
    fake_prev = Transaction(
        vin=[TransactionInput(b"\x33" * 32, 0)],
        vout=[TransactionOutput(20200, script_pubkey)],
    )
    assert fake_prev.txid() != real_prev.txid()

    tx = Transaction(
        vin=[TransactionInput(real_prev.txid(), 0)],
        vout=[
            TransactionOutput(20000, script.p2pkh(_key_at(root, "m/44h/1h/0h/0/7")[0]))
        ],
    )
    psbt = PSBT(tx)
    psbt.inputs[0].non_witness_utxo = fake_prev
    psbt.inputs[0].bip32_derivations[pubkey] = derivation

    with pytest.raises(ValueError, match="Previous txid"):
        PSBTSigner(_wallet(), psbt.serialize(), FORMAT_NONE)


def test_rejects_fabricated_non_witness_utxo_from_sdcard(mocker, m5stickv):
    """The SD card fallback into compressed mode must not bypass the check"""
    from embit import script
    from embit.transaction import Transaction, TransactionInput, TransactionOutput
    from krux.psbt import PSBTSigner
    from krux.qr import FORMAT_NONE

    root = _root()
    pubkey, derivation = _key_at(root, "m/44h/1h/0h/0/0")
    script_pubkey = script.p2pkh(pubkey)

    fake_prev = Transaction(
        vin=[TransactionInput(b"\x33" * 32, 0)],
        vout=[TransactionOutput(20200, script_pubkey)],
    )
    tx = Transaction(
        vin=[TransactionInput(b"\x66" * 32, 0)],
        vout=[TransactionOutput(20000, script_pubkey)],
    )
    partial_sig = _kv(b"\x02" + pubkey.sec(), b"\x30" * 71)
    input_map = (
        _kv(b"\x00", fake_prev.serialize())
        + _kv(b"\x06" + pubkey.sec(), derivation.serialize())
        + partial_sig
        + partial_sig
        + b"\x00"
    )
    raw = b"psbt\xff" + _kv(b"\x00", tx.serialize()) + b"\x00" + input_map + b"\x00"

    mocker.patch("builtins.open", mock_open(MockFile(raw)))
    with pytest.raises(ValueError, match="Previous txid"):
        PSBTSigner(_wallet(), None, FORMAT_NONE, "dummy.psbt")


def test_rejects_legacy_input_without_previous_tx(m5stickv):
    """A legacy input carrying only a witness_utxo has an unverifiable amount"""
    from embit import script
    from embit.psbt import PSBT
    from embit.transaction import Transaction, TransactionInput, TransactionOutput
    from krux.psbt import PSBTSigner
    from krux.qr import FORMAT_NONE

    root = _root()
    pubkey, derivation = _key_at(root, "m/44h/1h/0h/0/0")
    script_pubkey = script.p2pkh(pubkey)

    tx = Transaction(
        vin=[TransactionInput(b"\x44" * 32, 0)],
        vout=[TransactionOutput(20000, script_pubkey)],
    )
    psbt = PSBT(tx)
    psbt.inputs[0].witness_utxo = TransactionOutput(20200, script_pubkey)
    psbt.inputs[0].bip32_derivations[pubkey] = derivation

    with pytest.raises(ValueError):
        PSBTSigner(_wallet(), psbt.serialize(), FORMAT_NONE)


def _segwit_psbt(root, input_value, output_value):
    """Single input p2wpkh PSBT with the given declared amounts"""
    from embit import script
    from embit.psbt import PSBT
    from embit.transaction import Transaction, TransactionInput, TransactionOutput

    pubkey, derivation = _key_at(root, "m/84h/1h/0h/0/0")
    tx = Transaction(
        vin=[TransactionInput(b"\x99" * 32, 0)],
        vout=[
            TransactionOutput(
                output_value, script.p2wpkh(_key_at(root, "m/84h/1h/0h/0/7")[0])
            )
        ],
    )
    psbt = PSBT(tx)
    psbt.inputs[0].witness_utxo = TransactionOutput(input_value, script.p2wpkh(pubkey))
    psbt.inputs[0].bip32_derivations[pubkey] = derivation
    return psbt.serialize()


def test_rejects_outputs_exceeding_inputs(m5stickv):
    """A negative fee is impossible on chain and must not reach the review screen.

    It would render as a small negative amount and fee_percent clamps to 0.1,
    so the high fee warning would not fire either.
    """
    from krux.psbt import PSBTSigner
    from krux.qr import FORMAT_NONE

    root = _root()
    with pytest.raises(ValueError, match="outputs exceed inputs"):
        PSBTSigner(_wallet(), _segwit_psbt(root, 99000, 100000), FORMAT_NONE)


def test_accepts_zero_fee(m5stickv):
    """A zero fee is unusual but valid, only a negative one is impossible"""
    from krux.psbt import PSBTSigner
    from krux.qr import FORMAT_NONE

    root = _root()
    signer = PSBTSigner(_wallet(), _segwit_psbt(root, 100000, 100000), FORMAT_NONE)
    assert isinstance(signer, PSBTSigner)


def _compressed_psbt_with_contradicting_amounts(root, real_value, declared_value):
    """Builds a PSBT that forces the compressed parse and lies in witness_utxo.

    A duplicated PSBT_IN_PARTIAL_SIG key makes the uncompressed parse raise,
    so PSBTSigner falls back to CompressMode.CLEAR_ALL. That mode streams the
    previous transaction into _utxo, which is what the signer reads, while
    witness_utxo carries the attacker's value.
    """
    from embit import script
    from embit.transaction import Transaction, TransactionInput, TransactionOutput

    pubkey, derivation = _key_at(root, "m/84h/1h/0h/0/0")
    script_pubkey = script.p2wpkh(pubkey)

    prev_tx = Transaction(
        vin=[TransactionInput(b"\x11" * 32, 0)],
        vout=[TransactionOutput(real_value, script_pubkey)],
    )
    tx = Transaction(
        vin=[TransactionInput(prev_tx.txid(), 0)],
        vout=[
            TransactionOutput(
                100000, script.p2wpkh(_key_at(root, "m/84h/1h/0h/0/7")[0])
            )
        ],
    )
    lying_utxo = TransactionOutput(declared_value, script_pubkey)
    partial_sig = _kv(b"\x02" + pubkey.sec(), b"\x30" * 71)
    input_map = (
        _kv(b"\x00", prev_tx.serialize())
        + _kv(b"\x01", lying_utxo.serialize())
        + _kv(b"\x06" + pubkey.sec(), derivation.serialize())
        + partial_sig
        + partial_sig
        + b"\x00"
    )
    raw = b"psbt\xff" + _kv(b"\x00", tx.serialize()) + b"\x00" + input_map + b"\x00"
    return raw, tx, pubkey, script_pubkey


def _two_input_psbt(root, taproot=False, with_prev_txs=False):
    """Two input PSBT, optionally taproot, optionally carrying previous txs"""
    from embit import script
    from embit.psbt import PSBT
    from embit.transaction import Transaction, TransactionInput, TransactionOutput

    base = "m/86h/1h/0h" if taproot else "m/84h/1h/0h"
    make = script.p2tr if taproot else script.p2wpkh

    keys, prevs = [], []
    for i in (0, 1):
        pubkey, derivation = _key_at(root, "%s/0/%d" % (base, i))
        keys.append((pubkey, derivation))
        prevs.append(
            Transaction(
                vin=[TransactionInput(bytes([0xA0 + i]) * 32, 0)],
                vout=[TransactionOutput(100000000, make(pubkey))],
            )
        )

    tx = Transaction(
        vin=[TransactionInput(prev.txid(), 0) for prev in prevs],
        vout=[TransactionOutput(199990000, make(_key_at(root, "%s/0/7" % base)[0]))],
    )
    psbt = PSBT(tx)
    for i, (pubkey, derivation) in enumerate(keys):
        psbt.inputs[i].witness_utxo = prevs[i].vout[0]
        if with_prev_txs:
            psbt.inputs[i].non_witness_utxo = prevs[i]
        if taproot:
            psbt.inputs[i].taproot_bip32_derivations[pubkey] = ([], derivation)
            psbt.inputs[i].taproot_internal_key = pubkey
        else:
            psbt.inputs[i].bip32_derivations[pubkey] = derivation
    return psbt.serialize()


def _taproot_wallet():
    from embit.networks import NETWORKS
    from krux.key import Key, TYPE_SINGLESIG, P2TR
    from krux.wallet import Wallet

    return Wallet(Key(TEST_MNEMONIC, TYPE_SINGLESIG, NETWORKS["test"], "", 0, P2TR))


def test_warns_when_amounts_are_unverifiable(m5stickv):
    """Two segwit v0 inputs with no previous transactions is the Path C setup"""
    from krux.psbt import PSBTSigner
    from krux.qr import FORMAT_NONE

    signer = PSBTSigner(_wallet(), _two_input_psbt(_root()), FORMAT_NONE)
    assert signer.unverified_input_amounts() is True


def test_no_warning_with_previous_transactions(m5stickv):
    """Verified amounts cannot be understated, so there is nothing to warn about"""
    from krux.psbt import PSBTSigner
    from krux.qr import FORMAT_NONE

    raw = _two_input_psbt(_root(), with_prev_txs=True)
    signer = PSBTSigner(_wallet(), raw, FORMAT_NONE)
    assert signer.unverified_input_amounts() is False


def test_no_warning_for_taproot(m5stickv):
    """BIP341 hashes every input amount, so the two session trick cannot work"""
    from krux.psbt import PSBTSigner
    from krux.qr import FORMAT_NONE

    raw = _two_input_psbt(_root(), taproot=True)
    signer = PSBTSigner(_taproot_wallet(), raw, FORMAT_NONE)
    assert signer.unverified_input_amounts() is False


def test_no_warning_for_single_input(m5stickv):
    """A lie about the only input goes into its own sighash and breaks it"""
    from krux.psbt import PSBTSigner
    from krux.qr import FORMAT_NONE

    signer = PSBTSigner(_wallet(), _segwit_psbt(_root(), 100000, 90000), FORMAT_NONE)
    assert signer.unverified_input_amounts() is False


def test_displayed_amount_is_the_signed_amount(mocker, m5stickv):
    """Display and sighash must read the same UTXO, even in compressed mode"""
    from embit import ec, script
    from embit.transaction import SIGHASH
    from krux.format import format_btc
    from krux.psbt import PSBTSigner
    from krux.qr import FORMAT_NONE

    root = _root()
    real_value = 1000000000
    raw, tx, pubkey, script_pubkey = _compressed_psbt_with_contradicting_amounts(
        root, real_value, 101000
    )

    mocker.patch("builtins.open", mock_open(MockFile(raw)))
    signer = PSBTSigner(_wallet(), None, FORMAT_NONE, "dummy.psbt")

    tx_input = signer.psbt.inputs[0]
    # The lie is still in the PSBT, it just is not what gets displayed
    assert tx_input.witness_utxo.value == 101000
    assert tx_input.utxo.value == real_value

    messages, fee_percent = signer.outputs()
    assert format_btc(real_value) in messages[0]
    # 9.999 BTC of a 0.001 BTC spend, the high fee warning must fire
    assert fee_percent >= 10.0

    signer.sign(trim=False)
    signature = list(signer.psbt.inputs[0].partial_sigs.values())[0]
    parsed = ec.Signature.parse(signature[:-1])
    signed_over = tx.sighash_segwit(
        0,
        script.p2pkh_from_p2wpkh(script_pubkey),
        real_value,
        sighash=SIGHASH.ALL,
    )
    assert pubkey.verify(parsed, signed_over)


def test_compressed_parse_keeps_legacy_psbt_usable(mocker, m5stickv):
    """Compressed mode stores the previous output in _utxo, not non_witness_utxo"""
    from embit import script
    from embit.transaction import Transaction, TransactionInput, TransactionOutput
    from krux.format import format_btc
    from krux.psbt import PSBTSigner
    from krux.qr import FORMAT_NONE

    root = _root()
    pubkey, derivation = _key_at(root, "m/44h/1h/0h/0/0")
    script_pubkey = script.p2pkh(pubkey)

    prev_tx = Transaction(
        vin=[TransactionInput(b"\x77" * 32, 0)],
        vout=[TransactionOutput(100000000, script_pubkey)],
    )
    tx = Transaction(
        vin=[TransactionInput(prev_tx.txid(), 0)],
        vout=[TransactionOutput(20000, script_pubkey)],
    )
    partial_sig = _kv(b"\x02" + pubkey.sec(), b"\x30" * 71)
    input_map = (
        _kv(b"\x00", prev_tx.serialize())
        + _kv(b"\x06" + pubkey.sec(), derivation.serialize())
        + partial_sig
        + partial_sig
        + b"\x00"
    )
    raw = b"psbt\xff" + _kv(b"\x00", tx.serialize()) + b"\x00" + input_map + b"\x00"

    mocker.patch("builtins.open", mock_open(MockFile(raw)))
    signer = PSBTSigner(_wallet(), None, FORMAT_NONE, "dummy.psbt")

    assert signer.psbt.inputs[0].non_witness_utxo is None
    assert signer.psbt.inputs[0].utxo.value == 100000000
    messages, _ = signer.outputs()
    assert format_btc(100000000) in messages[0]


@pytest.mark.xfail(
    strict=True,
    reason="Segwit inputs are not required to carry a previous transaction, so "
    "their amounts stay unverified. Signing the same transaction twice, each "
    "session declaring a different input truthfully, yields one valid signature "
    "per input. Krux warns about this through unverified_input_amounts() but "
    "still signs if the user proceeds. Rejecting instead would need previous "
    "transactions on segwit inputs, which Sparrow deliberately omits for Krux "
    "and the other airgapped signers in WalletModel.alwaysIncludeNonWitnessUtxo.",
)
def test_segwit_input_amounts_are_verified(m5stickv):
    """Documents the residual exposure on multi input segwit transactions"""
    from embit import script
    from embit.psbt import PSBT
    from embit.transaction import Transaction, TransactionInput, TransactionOutput
    from krux.psbt import PSBTSigner
    from krux.qr import FORMAT_NONE

    root = _root()
    pubkey_0, derivation_0 = _key_at(root, "m/84h/1h/0h/0/0")
    pubkey_1, derivation_1 = _key_at(root, "m/84h/1h/0h/0/1")

    tx = Transaction(
        vin=[TransactionInput(b"\x44" * 32, 0), TransactionInput(b"\x55" * 32, 1)],
        vout=[
            TransactionOutput(
                99990000, script.p2wpkh(_key_at(root, "m/84h/1h/0h/0/7")[0])
            )
        ],
    )

    def build(value_0, value_1):
        psbt = PSBT(tx)
        psbt.inputs[0].witness_utxo = TransactionOutput(
            value_0, script.p2wpkh(pubkey_0)
        )
        psbt.inputs[0].bip32_derivations[pubkey_0] = derivation_0
        psbt.inputs[1].witness_utxo = TransactionOutput(
            value_1, script.p2wpkh(pubkey_1)
        )
        psbt.inputs[1].bip32_derivations[pubkey_1] = derivation_1
        return psbt.serialize()

    def signatures(raw):
        signer = PSBTSigner(_wallet(), raw, FORMAT_NONE)
        signer.sign(trim=False)
        return [list(inp.partial_sigs.values())[0] for inp in signer.psbt.inputs]

    try:
        truthful = signatures(build(100000000, 100000000))
        session_a = signatures(build(100000000, 1000))
        session_b = signatures(build(1000, 100000000))
    except ValueError:
        # Rejected at load, which is the outcome this test wants
        return

    # A device that verified segwit amounts would never produce these
    assert session_a[0] != truthful[0]
    assert session_b[1] != truthful[1]
