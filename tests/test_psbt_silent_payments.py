import pytest

# Standard BIP-39 test mnemonic (fingerprint 73c5da0a / root 0x...).
TEST_MNEMONIC = (
    "abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon about"
)

# Arbitrary, well-formed Silent Payment recipient keys (compressed secp256k1
# points) used only to exercise the sender-side derivation pipeline.
SCAN_HEX = "027a487fc19fb769877b8742d6ea18118f3c4e72b1ea8c6de602a7ad4a41dbe068"
SPEND_HEX = "0361e1b1e9de5e42cb2007f7ca54b9e0d57ed13938fad56d3f19e57513a8fce039"

INPUT_PATH = [84 + 2**31, 1 + 2**31, 0 + 2**31, 0, 0]


def _build_sp_psbt():
    """Builds a base64 PSBTv2 with one wallet-owned P2WPKH input and one SP output.

    Mirrors what a coordinator (e.g. Sparrow) hands to the signer: the SP output
    carries PSBT_OUT_SP_V0_INFO but no script_pubkey, which the signer must
    derive before signing.
    """
    from embit import bip32, bip39, ec, script
    from embit.psbt import DerivationPath
    from embit.transaction import TransactionOutput
    from embit.silent_payments import SilentPaymentsPSBT
    from embit.silent_payments.psbt import SPInputScope, SPOutputScope
    from embit.silent_payments.fields import SilentPaymentData

    root = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(TEST_MNEMONIC))
    child = root.derive(INPUT_PATH)
    pub = child.get_public_key()

    scan_pub = ec.PublicKey.parse(bytes.fromhex(SCAN_HEX))
    spend_pub = ec.PublicKey.parse(bytes.fromhex(SPEND_HEX))

    psbt = SilentPaymentsPSBT.create_v2()

    inp = SPInputScope()
    inp.txid = bytes([0xAB] * 32)
    inp.vout = 0
    inp.sequence = 0xFFFFFFFE
    inp.witness_utxo = TransactionOutput(
        value=100_000, script_pubkey=script.p2wpkh(pub)
    )
    inp.bip32_derivations[pub] = DerivationPath(root.my_fingerprint, INPUT_PATH)
    psbt.add_input(inp)

    out = SPOutputScope()
    out.value = 95_000
    out.script_pubkey = None  # coordinator omits the script for SP outputs
    out.sp_data = SilentPaymentData(scan_pub, spend_pub)
    psbt.add_output(out)

    psbt.tx_modifiable_flags = 0

    return psbt.to_string(), root, scan_pub, spend_pub, child


def _expected_output_script():
    """Independently derives the expected P2TR script via BIP-352 create_outputs."""
    from embit import bip32, bip39, ec, script, bech32
    from embit.transaction import COutPoint
    from embit.silent_payments import create_outputs

    root = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(TEST_MNEMONIC))
    child = root.derive(INPUT_PATH)

    scan_pub = ec.PublicKey.parse(bytes.fromhex(SCAN_HEX))
    spend_pub = ec.PublicKey.parse(bytes.fromhex(SPEND_HEX))

    # Encode the sp recipient address the same way Krux does.

    payload = scan_pub.sec() + spend_pub.sec()
    data = bech32.convertbits(payload, 8, 5)
    address = bech32.bech32_encode(bech32.Encoding.BECH32M, "tsp", [0] + data)

    outpoints = [COutPoint(bytes([0xAB] * 32), 0)]
    input_privkeys = [(child.key.secret, False)]
    outputs_map = create_outputs(input_privkeys, outpoints, [address])
    xonly = bytes.fromhex(outputs_map[address][0])
    # BIP-352 P_k is the final taproot output key: raw "OP_1 <x-only>", no tweak.
    return script.Script(b"\x51\x20" + xonly).data.hex()


def test_sign_silent_payment_output(mocker, m5stickv):
    """End-to-end: Krux derives the SP P2TR script and signs the input."""
    from embit.networks import NETWORKS
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    psbt_b64, _root, _scan, _spend, _child = _build_sp_psbt()

    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SINGLESIG, NETWORKS["test"]))
    signer = PSBTSigner(wallet, psbt_b64, FORMAT_NONE)

    assert signer.has_sp_outputs()

    signer.sign(trim=False)

    out = signer.psbt.outputs[0]
    # The SP output script must have been derived to the expected P2TR.
    assert out.script_pubkey is not None
    assert out.script_pubkey.data.hex() == _expected_output_script()

    # The input must carry a partial signature.
    assert len(signer.psbt.inputs[0].partial_sigs) > 0

    # BIP-375 per-input ECDH share + DLEQ proof must be present.
    assert len(signer.psbt.inputs[0].sp_ecdh_shares) == 1
    assert len(signer.psbt.inputs[0].sp_dleq_proofs) == 1


def test_sign_silent_payment_output_trimmed(mocker, m5stickv):
    """Production path (trim=True): the exported PSBT keeps SP metadata + signature."""
    import base64
    from embit.networks import NETWORKS
    from embit.silent_payments import SilentPaymentsPSBT
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    psbt_b64, _root, _scan, _spend, _child = _build_sp_psbt()

    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SINGLESIG, NETWORKS["test"]))
    signer = PSBTSigner(wallet, psbt_b64, FORMAT_NONE)
    signer.sign()  # trim=True

    exported, _fmt = signer.psbt_qr()
    psbt = SilentPaymentsPSBT.parse(base64.b64decode(exported))
    out = psbt.outputs[0]

    # Derived P2TR script and SP recipient metadata must survive the trim/export.
    assert out.script_pubkey.data.hex() == _expected_output_script()
    assert out.sp_data is not None
    # BIP-375 global ECDH share + the input signature must be exported.
    assert len(psbt.sp_ecdh_shares) == 1
    assert len(psbt.inputs[0].partial_sigs) > 0
    assert len(psbt.inputs[0].sp_ecdh_shares) == 1


def _build_sp_psbt_two_outputs(spend2_hex):
    """One P2WPKH input, two SP outputs sharing a scan key, different spend keys.

    The two outputs are placed in the PSBT in descending spend-key order, so a
    derivation that (incorrectly) sorted recipients by spend key would assign
    the BIP-352 counter k in the opposite order to the validator and be
    rejected — this exercises that the derivation uses output-index order.
    """
    from embit import bip32, bip39, ec, script
    from embit.psbt import DerivationPath
    from embit.transaction import TransactionOutput
    from embit.silent_payments import SilentPaymentsPSBT
    from embit.silent_payments.psbt import SPInputScope, SPOutputScope
    from embit.silent_payments.fields import SilentPaymentData

    root = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(TEST_MNEMONIC))
    child = root.derive(INPUT_PATH)
    pub = child.get_public_key()

    scan_pub = ec.PublicKey.parse(bytes.fromhex(SCAN_HEX))
    spend_pubs = [
        ec.PublicKey.parse(bytes.fromhex(SPEND_HEX)),
        ec.PublicKey.parse(bytes.fromhex(spend2_hex)),
    ]
    # Descending spend-key order → reverse of the validator's ascending sort.
    spend_pubs.sort(key=lambda p: p.sec(), reverse=True)

    psbt = SilentPaymentsPSBT.create_v2()

    inp = SPInputScope()
    inp.txid = bytes([0xAB] * 32)
    inp.vout = 0
    inp.sequence = 0xFFFFFFFE
    inp.witness_utxo = TransactionOutput(
        value=100_000, script_pubkey=script.p2wpkh(pub)
    )
    inp.bip32_derivations[pub] = DerivationPath(root.my_fingerprint, INPUT_PATH)
    psbt.add_input(inp)

    for spend_pub in spend_pubs:
        out = SPOutputScope()
        out.value = 40_000
        out.script_pubkey = None
        out.sp_data = SilentPaymentData(scan_pub, spend_pub)
        psbt.add_output(out)

    psbt.tx_modifiable_flags = 0
    return psbt.to_string()


def _expected_scripts_two(spend2_hex):
    """Independently derives the expected P2TR scripts, in output-index order.

    The BIP-352 counter k is assigned per scan-key group in the order the
    outputs appear in the transaction, which is the order the BIP-375 validator
    re-derives in. _build_sp_psbt_two_outputs places the two outputs in
    descending spend-key order, so we derive in that same order and return the
    scripts as a list indexed by output position.
    """
    from embit import bip32, bip39, ec, script, bech32
    from embit.transaction import COutPoint
    from embit.silent_payments import create_outputs

    root = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(TEST_MNEMONIC))
    child = root.derive(INPUT_PATH)
    scan_pub = ec.PublicKey.parse(bytes.fromhex(SCAN_HEX))

    # Match the on-chain output order built by _build_sp_psbt_two_outputs
    # (descending spend key) so the BIP-352 counter k lines up with the value
    # the validator re-derives — k depends on output-index position, not on the
    # spend keys' sort order.
    spend_pubs = sorted(
        (ec.PublicKey.parse(bytes.fromhex(h)) for h in (SPEND_HEX, spend2_hex)),
        key=lambda p: p.sec(),
        reverse=True,
    )
    addresses = []
    for spend_pub in spend_pubs:
        payload = scan_pub.sec() + spend_pub.sec()
        data = bech32.convertbits(payload, 8, 5)
        addresses.append(
            bech32.bech32_encode(bech32.Encoding.BECH32M, "tsp", [0] + data)
        )

    outpoints = [COutPoint(bytes([0xAB] * 32), 0)]
    outputs_map = create_outputs([(child.key.secret, False)], outpoints, addresses)
    # addresses are distinct (different spend keys), so each maps to one script;
    # keep them in output-index order.
    return [
        script.Script(b"\x51\x20" + bytes.fromhex(outputs_map[addr][0])).data.hex()
        for addr in addresses
    ]


def test_sign_two_sp_outputs_same_scan_key(mocker, m5stickv):
    """Two SP outputs sharing a scan key derive to the correct per-output scripts.

    Regression for the k-ordering bug: create_outputs assigns the BIP-352
    counter k in recipient-list order while the validator re-derives k in
    output-index order, so the derivation must feed recipients in output-index
    order (not sorted by spend key) for the two to agree. Asserts each output's
    script position-by-position so a wrong k assignment is caught even when the
    set of scripts would otherwise match.
    """
    from embit import ec
    from embit.networks import NETWORKS
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    spend2_hex = ec.PrivateKey(bytes([7] * 32)).get_public_key().sec().hex()

    psbt_b64 = _build_sp_psbt_two_outputs(spend2_hex)
    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SINGLESIG, NETWORKS["test"]))
    signer = PSBTSigner(wallet, psbt_b64, FORMAT_NONE)
    signer.sign(trim=False)

    on_chain = [out.script_pubkey.data.hex() for out in signer.psbt.outputs]
    assert on_chain == _expected_scripts_two(spend2_hex)


def test_silent_payment_eligibility_rejections(mocker, m5stickv):
    """validate_eligibility rejects multisig, miniscript, and non-eligible scripts."""
    from krux.silent_payments import validate_eligibility
    from krux.key import P2WPKH, P2TR, P2WSH

    # Multisig (m/n present) and miniscript are rejected.
    with pytest.raises(ValueError):
        validate_eligibility({"type": P2WSH, "m": 2, "n": 3})
    with pytest.raises(ValueError):
        validate_eligibility({"type": P2WSH, "miniscript": True})
    # Non-eligible single-sig script types (BIP-375 forbids Segwit v>1).
    with pytest.raises(ValueError):
        validate_eligibility({"type": P2TR})

    # An eligible single-sig policy passes (no exception).
    validate_eligibility({"type": P2WPKH})
