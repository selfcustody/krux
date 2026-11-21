"""Regression coverage for PSBT input amount verification.

The amount shown on the review screen must be the same amount the signer
commits to, and any previous transaction attached to an input must really
hash to the outpoint being spent.
"""

import pytest
from .shared_mocks import MockFile, mock_open

TEST_MNEMONIC = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"


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


def _force_compressed_fallback(mocker):
    """Makes the uncompressed SD card parse run out of memory.

    That is what the CompressMode.CLEAR_ALL fallback exists for on device, so
    the PSBT under test can reach compressed mode without being malformed.
    """
    import krux.psbt
    from embit.psbt import CompressMode

    read_from = krux.psbt.PSBT.read_from

    def low_memory_read_from(stream, compress=CompressMode.KEEP_ALL):
        if compress == CompressMode.KEEP_ALL:
            raise MemoryError
        return read_from(stream, compress=compress)

    mocker.patch("krux.psbt.PSBT.read_from", side_effect=low_memory_read_from)


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
    from embit.psbt import PSBT
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
    psbt = PSBT(tx)
    psbt.inputs[0].non_witness_utxo = fake_prev
    psbt.inputs[0].bip32_derivations[pubkey] = derivation

    mocker.patch("builtins.open", mock_open(MockFile(psbt.serialize())))
    _force_compressed_fallback(mocker)
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


@pytest.mark.parametrize("version", [None, 2])
@pytest.mark.parametrize("output_values", [[], [1000]])
def test_rejects_psbt_without_inputs(m5stickv, version, output_values):
    """Embit parses a PSBT with no inputs, but there is nothing to sign in it"""
    from embit import script
    from embit.psbt import PSBT
    from embit.transaction import Transaction, TransactionOutput
    from krux.psbt import PSBTSigner
    from krux.qr import FORMAT_NONE

    tx = Transaction(
        vin=[],
        vout=[
            TransactionOutput(value, script.Script(b"\x6a")) for value in output_values
        ],
    )
    with pytest.raises(ValueError, match="Invalid PSBT: no inputs"):
        PSBTSigner(_wallet(), PSBT(tx, version=version).serialize(), FORMAT_NONE)


def _psbt_with_contradicting_amounts(root, real_value, declared_value):
    """Builds a PSBT whose witness_utxo lies about the previous tx output"""
    from embit import script
    from embit.psbt import PSBT
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
    psbt = PSBT(tx)
    psbt.inputs[0].non_witness_utxo = prev_tx
    psbt.inputs[0].witness_utxo = TransactionOutput(declared_value, script_pubkey)
    psbt.inputs[0].bip32_derivations[pubkey] = derivation
    return psbt.serialize()


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


@pytest.mark.parametrize("from_sdcard", [False, True])
def test_rejects_witness_utxo_contradicting_previous_tx(mocker, m5stickv, from_sdcard):
    """A witness_utxo that contradicts the previous tx must be refused.

    The full parse reads the amount from witness_utxo and compressed mode from
    the previous tx, so accepting both would make the displayed and signed
    amount depend on how the PSBT was loaded.
    """
    from krux.psbt import PSBTSigner
    from krux.qr import FORMAT_NONE

    raw = _psbt_with_contradicting_amounts(_root(), 1000000000, 101000)
    if from_sdcard:
        mocker.patch("builtins.open", mock_open(MockFile(raw)))
        _force_compressed_fallback(mocker)
        args = (None, FORMAT_NONE, "dummy.psbt")
    else:
        args = (raw, FORMAT_NONE)

    with pytest.raises(ValueError, match="Witness utxo doesn't match"):
        PSBTSigner(_wallet(), *args)


def test_compressed_parse_keeps_legacy_psbt_usable(mocker, m5stickv):
    """Compressed mode stores the previous output in _utxo, not non_witness_utxo"""
    from embit import script
    from embit.psbt import PSBT
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
    psbt = PSBT(tx)
    psbt.inputs[0].non_witness_utxo = prev_tx
    psbt.inputs[0].bip32_derivations[pubkey] = derivation

    mocker.patch("builtins.open", mock_open(MockFile(psbt.serialize())))
    _force_compressed_fallback(mocker)
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
