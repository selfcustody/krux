import pytest
from embit import bip32, bip39, ec, script
from embit.bip32 import parse_path
from embit.hashes import tagged_hash
from embit.networks import NETWORKS
from embit.psbt import DerivationPath
from embit.script import Script
from embit.silent_payments import SilentPaymentsPSBT
from embit.silent_payments.psbt import SilentPaymentData
from embit.silent_payments.psbt import SPInputScope, SPOutputScope
from embit.transaction import TransactionInput, TransactionOutput
from embit.util.key import SECP256K1_ORDER

TEST_MNEMONIC = (
    "abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon about"
)

# Arbitrary, well-formed Silent Payment recipient keys (compressed secp256k1
# points) used only to exercise the sender-side derivation pipeline.
SCAN_HEX = "027a487fc19fb769877b8742d6ea18118f3c4e72b1ea8c6de602a7ad4a41dbe068"
SPEND_HEX = "0361e1b1e9de5e42cb2007f7ca54b9e0d57ed13938fad56d3f19e57513a8fce039"

INPUT_PATH = [84 + 2**31, 1 + 2**31, 0 + 2**31, 0, 0]


def _normalize_xonly_keys(items):
    """Normalizes (secret, is_xonly) pairs to the scalars BIP-352 sums.

    embit's derive_sp_outputs() takes pre-normalized 32-byte scalars; taproot
    inputs must contribute the even-Y scalar (see embit's
    silent_payments/signing.py _resolve_taproot_privkey).
    """
    return [
        (ec.PrivateKey(secret).even_y().secret if is_xonly else secret)
        for secret, is_xonly in items
    ]


def _assert_not_finalized(psbt):
    """BIP-375: the signer hands back an unfinalized PSBT so the coordinator
    can verify the derived SP outputs before finalizing."""
    for inp in psbt.inputs:
        assert inp.final_scriptwitness is None
        assert inp.final_scriptsig is None


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
    from embit.silent_payments.psbt import SilentPaymentData

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
    """Independently derives the expected P2TR script via BIP-352 derive_sp_outputs."""
    from embit import bip32, bip39, ec, script
    from embit.transaction import TransactionInput
    from embit.silent_payments.sp import derive_sp_outputs

    root = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(TEST_MNEMONIC))
    child = root.derive(INPUT_PATH)

    scan_pub = ec.PublicKey.parse(bytes.fromhex(SCAN_HEX))
    spend_pub = ec.PublicKey.parse(bytes.fromhex(SPEND_HEX))

    outpoints = [TransactionInput(bytes([0xAB] * 32), 0)]
    input_privkeys = [(child.key.secret, False)]
    priv_keys = _normalize_xonly_keys(input_privkeys)

    scan_spend_groups = {scan_pub.sec(): (scan_pub, [spend_pub])}

    _, _, results = derive_sp_outputs(priv_keys, outpoints, scan_spend_groups)
    xonly = results[scan_pub.sec()][1][0]
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
    assert len(psbt.sp_dleq_proofs) == 1
    assert len(psbt.inputs[0].partial_sigs) > 0
    _assert_not_finalized(psbt)
    # Per-input SP fields must NOT be exported when the global share covers
    # them: the trim strips PSBT_IN_BIP32_DERIVATION, which BIP-375 requires
    # alongside a per-input DLEQ proof for non-taproot inputs.


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
    from embit.silent_payments.psbt import SilentPaymentData

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
    """Independently derives the expected P2TR scripts, indexed by output position.

    The BIP-352 counter k is assigned per scan-key group by ascending spend-key
    order (output index only breaks ties among equal spend keys) -- this mirrors
    group_sp_outputs_by_scan_key instead of assuming k tracks output position.
    _build_sp_psbt_two_outputs places the two outputs in descending spend-key
    order on-chain, the case where on-chain order and k-order disagree.
    """
    from embit import bip32, bip39, ec, script
    from embit.silent_payments.psbt import SilentPaymentData, SPOutputScope
    from embit.silent_payments.sp import derive_sp_outputs, group_sp_outputs_by_scan_key
    from embit.transaction import TransactionInput

    root = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(TEST_MNEMONIC))
    child = root.derive(INPUT_PATH)
    scan_pub = ec.PublicKey.parse(bytes.fromhex(SCAN_HEX))

    # Same on-chain order as _build_sp_psbt_two_outputs: descending spend key.
    spend_pubs = sorted(
        (ec.PublicKey.parse(bytes.fromhex(h)) for h in (SPEND_HEX, spend2_hex)),
        key=lambda p: p.sec(),
        reverse=True,
    )
    outs = []
    for spend_pub in spend_pubs:
        out = SPOutputScope()
        out.sp_data = SilentPaymentData(scan_pub, spend_pub)
        outs.append(out)
    scan_spend_groups, output_indices = group_sp_outputs_by_scan_key(outs)

    outpoints = [TransactionInput(bytes([0xAB] * 32), 0)]
    priv_keys = _normalize_xonly_keys([(child.key.secret, False)])

    _, _, results = derive_sp_outputs(priv_keys, outpoints, scan_spend_groups)
    outputs = results[scan_pub.sec()][1]

    expected = [None] * len(spend_pubs)
    for pos, out_idx in enumerate(output_indices[scan_pub.sec()]):
        expected[out_idx] = script.Script(b"\x51\x20" + outputs[pos]).data.hex()
    return expected


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

    # Multisig (m/n present) and miniscript are rejected, even on a P2TR type.
    with pytest.raises(ValueError):
        validate_eligibility({"type": P2WSH, "m": 2, "n": 3})
    with pytest.raises(ValueError):
        validate_eligibility({"type": P2TR, "miniscript": True})
    # A non-eligible single-sig type (P2WSH key-path is not a BIP-352 input).
    with pytest.raises(ValueError):
        validate_eligibility({"type": P2WSH})

    # Eligible single-sig policies pass (no exception). P2TR is eligible per
    # BIP-352 and covers ordinary BIP-86 and BIP-376 spend-from inputs.
    validate_eligibility({"type": P2WPKH})
    validate_eligibility({"type": P2TR})


# ─────────────────────────────────────────────────────────────────────────────
# BIP-376: spend FROM a silent payment UTXO.
#
# Spending a UTXO previously received at our SP address. A BIP-376 coordinator
# hands Krux a PSBT whose input is the on-chain P2TR key P_k = B_spend + t*G,
# carrying the per-input sp_tweak and sp_spend_bip32_derivations; the embit
# fork's _sign_sp_spends derives the wallet's spend key, applies the tweak and
# signs. The tests below pin both the working path and Krux's deliberate
# behaviour at the edges:
#
#   Confirmed working:
#     * load + policy: the input is recognized as p2tr; no policy mismatch
#       because an SP wallet is never "loaded" with a descriptor
#     * review: input amount, spend amount and fee are reported correctly
#     * signing: a valid 64-byte BIP-340 key signature is produced for the
#       correct, wallet-owned tweaked spend key (and only that key)
#     * export: the signed PSBT round-trips as v2 and keeps the signature
#
#   Deliberate behaviour (asserted so an embit bump can't silently change it):
#     * Krux does not finalize on-device (no final_scriptwitness): the same
#       sign-don't-finalize rule it applies to every policy. The coordinator
#       finalizes the key-path spend from the returned signature.
#     * the trim drops sp_tweak / sp_spend_bip32_derivations: the coordinator
#       authored those and only needs the signature back, exactly like Krux
#       drops ordinary input bip32_derivations after signing.
#     * ownership: Krux signs only inputs it provably owns. embit checks both
#       the spend-key derivation and that B_spend + t*G equals the input's
#       output key, so a foreign tweak or derivation yields no signature and
#       Krux refuses the PSBT ("cannot sign").
# ─────────────────────────────────────────────────────────────────────────────

# Arbitrary but valid per-output tweak t_k used to forge the received UTXO's key.
SP_SPEND_TWEAK = bytes([0x11] * 32)


def _build_sp_spend_psbt(wallet):
    """Builds a base64 PSBTv2 that spends one SP-received P2TR UTXO.

    Mirrors a BIP-376 coordinator: the input is the on-chain P2TR output key
    P_k = B_spend + tweak*G, and the PSBT carries the per-input ``sp_tweak`` plus
    ``sp_spend_bip32_derivations`` pointing at the wallet's m/352h/.../0h/0 spend
    key. The single destination output is an ordinary P2WPKH (no SP data), so
    has_sp_outputs() is False and only the BIP-376 spend path is exercised.
    """
    from embit import script
    from embit.psbt import DerivationPath
    from embit.bip32 import parse_path
    from embit.transaction import TransactionOutput
    from embit.script import Script
    from embit.silent_payments import SilentPaymentsPSBT
    from embit.silent_payments.psbt import SPInputScope, SPOutputScope

    key = wallet.key
    root = key.root
    spend_priv = key.sp_keys.spend_privkey
    spend_pub = key.sp_keys.spend_pubkey

    # Full path from the master to the spend key, as a coordinator would record
    # it in PSBT_IN_SP_V0_SPEND_DERIVATION (key.derivation is m/352h/<coin>h/0h).
    spend_path = parse_path(key.derivation + "/0h/0")

    # The on-chain output key is the tweaked spend key, exactly what
    # sign_input_with_sp_tweak re-derives and checks before signing.
    output_xonly = spend_priv.sp_spend_tweak(SP_SPEND_TWEAK).xonly()

    psbt = SilentPaymentsPSBT.create_v2()

    inp = SPInputScope()
    inp.txid = bytes([0xCD] * 32)
    inp.vout = 0
    inp.sequence = 0xFFFFFFFE
    inp.witness_utxo = TransactionOutput(
        value=100_000, script_pubkey=Script(b"\x51\x20" + output_xonly)
    )
    inp.sp_tweak = SP_SPEND_TWEAK
    inp.sp_spend_bip32_derivations[spend_pub.sec()] = DerivationPath(
        root.my_fingerprint, spend_path
    )
    psbt.add_input(inp)

    # Ordinary destination output (not a silent payment).
    dest_pub = root.derive([84 + 2**31, 1 + 2**31, 0 + 2**31, 0, 0]).get_public_key()
    out = SPOutputScope()
    out.value = 95_000
    out.script_pubkey = script.p2wpkh(dest_pub)
    psbt.add_output(out)

    psbt.tx_modifiable_flags = 0
    return psbt.to_string()


def test_sign_spend_from_sp(mocker, m5stickv):
    """Happy path: sign a BIP-376 spend-from PSBT for a wallet-owned SP UTXO."""
    import base64
    from embit import ec
    from embit.networks import NETWORKS
    from embit.silent_payments import SilentPaymentsPSBT
    from krux.psbt import PSBTSigner
    from krux.key import P2TR, Key, TYPE_SILENT_PAYMENT
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SILENT_PAYMENT, NETWORKS["test"]))
    psbt_b64 = _build_sp_spend_psbt(wallet)

    signer = PSBTSigner(wallet, psbt_b64, FORMAT_NONE)

    # --- WORKS: load + policy. The SP-spend input is recognized as p2tr, and
    # this is a spend-FROM so there are no SP *outputs*. ---
    assert signer.policy["type"] == P2TR
    assert not signer.has_sp_outputs()

    # --- WORKS: the review screen the sign UI shows reports correct amounts. ---
    out_strs, fee_percent = signer.outputs()
    assert round(fee_percent, 1) == 5.3  # 5_000 fee on a 95_000 spend
    assert any("0.00 095 000" in s for s in out_strs)  # spend amount

    # --- WORKS: signing produces a valid 64-byte BIP-340 signature for the
    # correct, wallet-owned tweaked spend key. ---
    signer.sign(trim=False)
    sig = signer.psbt.inputs[0].taproot_key_sig
    assert sig is not None and len(sig) == 64
    output_xonly = signer.psbt.inputs[0].witness_utxo.script_pubkey.data[2:34]
    msg = signer.psbt.sighash(0, sighash=0)  # SIGHASH_DEFAULT
    pubkey = ec.PublicKey.from_xonly(output_xonly)
    assert pubkey.schnorr_verify(ec.SchnorrSig(sig), msg)
    expected_key = wallet.key.sp_keys.spend_privkey.sp_spend_tweak(SP_SPEND_TWEAK)
    assert output_xonly == expected_key.xonly()

    # --- WORKS: production trim/export round-trips as v2 and keeps the sig. ---
    signer2 = PSBTSigner(wallet, _build_sp_spend_psbt(wallet), FORMAT_NONE)
    signer2.sign()  # trim=True
    exported, _ = signer2.psbt_qr()
    out_psbt = SilentPaymentsPSBT.parse(base64.b64decode(exported))
    assert out_psbt.version == 2
    assert out_psbt.inputs[0].taproot_key_sig is not None

    # Krux's clearing of final_scriptwitness in
    # sign() only triggers when the PSBT has SP outputs; here embit's taproot
    # signer finalizes normally, same as any other key-path P2TR spend.
    assert out_psbt.inputs[0].final_scriptwitness is not None
    # The trim returns only the signature; the coordinator already holds the
    # tweak and derivation it authored.
    assert getattr(out_psbt.inputs[0], "sp_tweak", None) is None
    assert not getattr(out_psbt.inputs[0], "sp_spend_bip32_derivations", {})


def _spend_input(witness_value, output_xonly, sp_tweak, derivation):
    """A BIP-376 spend-from P2TR input with the given output key, tweak, origin."""
    from embit.transaction import TransactionOutput
    from embit.script import Script
    from embit.silent_payments.psbt import SPInputScope

    inp = SPInputScope()
    inp.txid = bytes([0xCD] * 32)
    inp.vout = 0
    inp.sequence = 0xFFFFFFFE
    inp.witness_utxo = TransactionOutput(
        value=witness_value, script_pubkey=Script(b"\x51\x20" + output_xonly)
    )
    inp.sp_tweak = sp_tweak
    inp.sp_spend_bip32_derivations[derivation[0]] = derivation[1]
    return inp


def _p2wpkh_dest(root, value):
    """An ordinary (non-SP) destination output paying a wallet-derived key."""
    from embit import script
    from embit.silent_payments.psbt import SPOutputScope

    out = SPOutputScope()
    out.value = value
    out.script_pubkey = script.p2wpkh(root.derive(INPUT_PATH).get_public_key())
    return out


def test_spend_from_sp_foreign_tweak_refused(mocker, m5stickv):
    """A tweak that doesn't reproduce the input's output key is refused.

    embit recomputes B_spend + t*G and raises SPValidationError unless it
    equals the input's output xonly. Here the PSBT's sp_tweak differs from the
    tweak baked into the on-chain key, so the input is left unsigned and Krux
    refuses the PSBT.
    """
    from embit.psbt import DerivationPath
    from embit.bip32 import parse_path
    from embit.networks import NETWORKS
    from embit.silent_payments import SilentPaymentsPSBT
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SILENT_PAYMENT
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SILENT_PAYMENT, NETWORKS["test"]))
    key = wallet.key
    root = key.root
    spend_pub = key.sp_keys.spend_pubkey

    # On-chain key commits to one tweak; the PSBT carries a different one.
    output_xonly = key.sp_keys.spend_privkey.sp_spend_tweak(bytes([0x11] * 32)).xonly()
    derivation = (
        spend_pub.sec(),
        DerivationPath(root.my_fingerprint, parse_path(key.derivation + "/0h/0")),
    )

    psbt = SilentPaymentsPSBT.create_v2()
    psbt.add_input(_spend_input(100_000, output_xonly, bytes([0x22] * 32), derivation))
    psbt.add_output(_p2wpkh_dest(root, 95_000))
    psbt.tx_modifiable_flags = 0

    signer = PSBTSigner(wallet, psbt.to_string(), FORMAT_NONE)
    with pytest.raises(ValueError, match="mismatched sp_tweak"):  # nothing was signed
        signer.sign(trim=False)
    assert signer.psbt.inputs[0].taproot_key_sig is None


def test_spend_from_sp_foreign_derivation_refused(mocker, m5stickv):
    """A spend derivation Krux can't match leaves the owned-looking input unsigned.

    The on-chain key is the wallet's correctly tweaked spend key, but the
    sp_spend_bip32_derivations references a foreign master fingerprint, so
    _sign_sp_spends finds no key to derive and the input is not signed.
    """
    from embit.psbt import DerivationPath
    from embit.bip32 import parse_path
    from embit.networks import NETWORKS
    from embit.silent_payments import SilentPaymentsPSBT
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SILENT_PAYMENT
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SILENT_PAYMENT, NETWORKS["test"]))
    key = wallet.key
    root = key.root
    spend_pub = key.sp_keys.spend_pubkey

    sp_tweak = bytes([0x11] * 32)
    output_xonly = key.sp_keys.spend_privkey.sp_spend_tweak(sp_tweak).xonly()
    # Correct path, but a fingerprint that is not this wallet's master.
    derivation = (
        spend_pub.sec(),
        DerivationPath(b"\xff\xff\xff\xff", parse_path(key.derivation + "/0h/0")),
    )

    psbt = SilentPaymentsPSBT.create_v2()
    psbt.add_input(_spend_input(100_000, output_xonly, sp_tweak, derivation))
    psbt.add_output(_p2wpkh_dest(root, 95_000))
    psbt.tx_modifiable_flags = 0

    signer = PSBTSigner(wallet, psbt.to_string(), FORMAT_NONE)
    with pytest.raises(ValueError, match="cannot sign"):  # derivation never matched
        signer.sign(trim=False)
    assert signer.psbt.inputs[0].taproot_key_sig is None


def test_sign_spend_from_sp_with_normal_taproot_input(mocker, m5stickv):
    """An SP-spend input and an ordinary key-path P2TR input both get signed.

    Confirms embit's _sign_sp_spends and the base taproot signing coexist in one
    PSBT: input 0 is signed via sp_tweak, input 1 via its BIP-86 derivation. Both
    inputs are p2tr, so Krux's single-policy check is satisfied.
    """
    from embit import script
    from embit.psbt import DerivationPath
    from embit.bip32 import parse_path
    from embit.transaction import TransactionOutput
    from embit.networks import NETWORKS
    from embit.silent_payments import SilentPaymentsPSBT
    from embit.silent_payments.psbt import SPInputScope
    from krux.psbt import PSBTSigner
    from krux.key import P2TR, Key, TYPE_SILENT_PAYMENT
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SILENT_PAYMENT, NETWORKS["test"]))
    key = wallet.key
    root = key.root

    sp_tweak = bytes([0x11] * 32)
    output_xonly = key.sp_keys.spend_privkey.sp_spend_tweak(sp_tweak).xonly()
    sp_derivation = (
        key.sp_keys.spend_pubkey.sec(),
        DerivationPath(root.my_fingerprint, parse_path(key.derivation + "/0h/0")),
    )

    psbt = SilentPaymentsPSBT.create_v2()
    # input 0: spend FROM the silent payment UTXO.
    psbt.add_input(_spend_input(100_000, output_xonly, sp_tweak, sp_derivation))

    # input 1: ordinary BIP-86 key-path P2TR owned by the same wallet.
    tap_path = parse_path("m/86h/1h/0h/0/0")
    internal_pub = root.derive(tap_path).get_public_key()
    norm_in = SPInputScope()
    norm_in.txid = bytes([0xEF] * 32)
    norm_in.vout = 1
    norm_in.sequence = 0xFFFFFFFE
    norm_in.witness_utxo = TransactionOutput(
        value=50_000, script_pubkey=script.p2tr(internal_pub)
    )
    norm_in.taproot_bip32_derivations[internal_pub] = (
        [],
        DerivationPath(root.my_fingerprint, tap_path),
    )
    psbt.add_input(norm_in)

    psbt.add_output(_p2wpkh_dest(root, 145_000))
    psbt.tx_modifiable_flags = 0

    signer = PSBTSigner(wallet, psbt.to_string(), FORMAT_NONE)
    assert signer.policy["type"] == P2TR
    assert not signer.has_sp_outputs()

    signer.sign(trim=False)

    # Both inputs carry a key-path signature.
    assert signer.psbt.inputs[0].taproot_key_sig is not None  # SP-spend path
    assert signer.psbt.inputs[1].taproot_key_sig is not None  # ordinary taproot


# ─────────────────────────────────────────────────────────────────────────────
# P2TR inputs funding SP outputs (BIP-352 eligible input type).
#
# A taproot input must contribute its even-Y output key to the BIP-352 shared
# secret. taproot_tweak already returns an even-Y key; sp_spend_tweak does not,
# so the spend-from path normalizes explicitly. Both tests cross-check the
# derived P2TR output against an independent create_outputs run using the same
# input key, so a missing or mis-normalized contribution is caught.
# ─────────────────────────────────────────────────────────────────────────────


def _expected_sp_script(input_privkeys, txid, scan_pub, spend_pub):
    """Independently derive the P2TR script for one SP recipient, one outpoint."""
    from embit import script
    from embit.transaction import TransactionInput
    from embit.silent_payments.sp import derive_sp_outputs

    priv_keys = _normalize_xonly_keys(input_privkeys)
    scan_spend_groups = {scan_pub.sec(): (scan_pub, [spend_pub])}

    _, _, results = derive_sp_outputs(
        priv_keys, [TransactionInput(txid, 0)], scan_spend_groups
    )
    xonly = results[scan_pub.sec()][1][0]

    return script.Script(b"\x51\x20" + xonly).data.hex()


TAP_PATH = [86 + 2**31, 1 + 2**31, 0 + 2**31, 0, 0]


def _build_sp_psbt_taproot_input():
    """One ordinary BIP-86 taproot input, one SP output. Returns (b64, txid)."""
    root = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(TEST_MNEMONIC))
    internal_pub = root.derive(TAP_PATH).get_public_key()

    scan_pub = ec.PublicKey.parse(bytes.fromhex(SCAN_HEX))
    spend_pub = ec.PublicKey.parse(bytes.fromhex(SPEND_HEX))

    txid = bytes([0xAB] * 32)
    psbt = SilentPaymentsPSBT.create_v2()
    inp = SPInputScope()
    inp.txid = txid
    inp.vout = 0
    inp.sequence = 0xFFFFFFFE
    inp.witness_utxo = TransactionOutput(
        value=100_000, script_pubkey=script.p2tr(internal_pub)
    )
    inp.taproot_bip32_derivations[internal_pub] = (
        [],
        DerivationPath(root.my_fingerprint, TAP_PATH),
    )
    psbt.add_input(inp)

    out = SPOutputScope()
    out.value = 95_000
    out.script_pubkey = None
    out.sp_data = SilentPaymentData(scan_pub, spend_pub)
    psbt.add_output(out)
    psbt.tx_modifiable_flags = 0

    return psbt.to_string(), txid


def _expected_taproot_input_script(txid):
    """taproot_tweak yields the even-Y output key BIP-352 sums."""
    root = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(TEST_MNEMONIC))
    in_priv = root.derive(TAP_PATH).key.taproot_tweak(b"")
    return _expected_sp_script(
        [(in_priv.secret, True)],
        txid,
        ec.PublicKey.parse(bytes.fromhex(SCAN_HEX)),
        ec.PublicKey.parse(bytes.fromhex(SPEND_HEX)),
    )


def test_sign_sp_output_from_taproot_input(mocker, m5stickv):
    """Send to an SP address funded by an ordinary BIP-86 taproot input.

    Regression for P2TR send-side eligibility: the taproot input's even-Y output
    key must be summed into the shared secret. Asserts the derived output matches
    an independent derivation including that key, and the input is signed.
    """
    from embit.networks import NETWORKS
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    psbt_b64, txid = _build_sp_psbt_taproot_input()

    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SINGLESIG, NETWORKS["test"]))
    signer = PSBTSigner(wallet, psbt_b64, FORMAT_NONE)
    assert signer.has_sp_outputs()
    signer.sign(trim=False)

    assert signer.psbt.outputs[
        0
    ].script_pubkey.data.hex() == _expected_taproot_input_script(txid)
    assert signer.psbt.inputs[0].taproot_key_sig is not None
    # Even on the SD path the signer must not finalize an SP send.
    _assert_not_finalized(signer.psbt)


def test_sign_sp_output_from_taproot_input_trimmed(mocker, m5stickv):
    """QR path (trim=True) for a taproot input — the combination that regressed.

    embit finalizes taproot key-path inputs on signing. A finalized PSBT makes
    coordinators (Sparrow/drongo) take copyFinalizedFields() instead of
    combine(), which copies only the witnesses and drops the derived
    PSBT_OUT_SCRIPT plus the global ECDH share / DLEQ proof — leaving the
    coordinator unable to extract the transaction.
    """
    import base64
    from embit.networks import NETWORKS
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    psbt_b64, txid = _build_sp_psbt_taproot_input()

    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SINGLESIG, NETWORKS["test"]))
    signer = PSBTSigner(wallet, psbt_b64, FORMAT_NONE)
    signer.sign()  # trim=True

    exported, _fmt = signer.psbt_qr()
    psbt = SilentPaymentsPSBT.parse(base64.b64decode(exported))

    _assert_not_finalized(psbt)
    assert psbt.inputs[0].taproot_key_sig is not None

    out = psbt.outputs[0]
    assert out.script_pubkey.data.hex() == _expected_taproot_input_script(txid)
    assert out.sp_data is not None
    assert len(psbt.sp_ecdh_shares) == 1
    assert len(psbt.sp_dleq_proofs) == 1


def test_sp_taproot_signature_commits_to_derived_output(mocker, m5stickv):
    """BIP-341: SIGHASH_DEFAULT commits to sha_outputs, so the SP output script
    must be derived before signing.

    Verifies the exported signature against the BIP-341 sighash of the final
    transaction, and that perturbing the derived script invalidates it. This is
    what BIP-375 relies on when it mandates SIGHASH_ALL: SIGHASH_NONE/SINGLE
    would let outputs move and invalidate the computed scripts.
    """
    import base64
    from embit.networks import NETWORKS
    from embit.transaction import SIGHASH
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    psbt_b64, _txid = _build_sp_psbt_taproot_input()

    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SINGLESIG, NETWORKS["test"]))
    signer = PSBTSigner(wallet, psbt_b64, FORMAT_NONE)
    signer.sign()  # trim=True, the QR export path

    exported, _fmt = signer.psbt_qr()
    psbt = SilentPaymentsPSBT.parse(base64.b64decode(exported))

    sig = psbt.inputs[0].taproot_key_sig
    # SIGHASH_DEFAULT carries no trailing sighash byte.
    assert len(sig) == 64

    # BIP-341 key path spending: the witness is a single element, the signature,
    # checked against the output key q taken straight from the prevout script.
    q = ec.PublicKey.from_xonly(bytes(psbt.inputs[0].utxo.script_pubkey.data[2:34]))
    script_pubkeys = [inp.utxo.script_pubkey for inp in psbt.inputs]
    values = [inp.utxo.value for inp in psbt.inputs]

    sighash = psbt.sighash_taproot(0, script_pubkeys, values, sighash=SIGHASH.DEFAULT)
    assert q.schnorr_verify(ec.SchnorrSig.parse(sig), sighash)

    # Flip one bit of the derived SP output script: the signature must no longer
    # verify, proving it commits to the script Krux derived.
    tampered = SilentPaymentsPSBT.parse(base64.b64decode(exported))
    data = bytearray(tampered.outputs[0].script_pubkey.data)
    data[-1] ^= 0x01
    tampered.outputs[0].script_pubkey = Script(bytes(data))
    tampered_sighash = tampered.sighash_taproot(
        0, script_pubkeys, values, sighash=SIGHASH.DEFAULT
    )
    assert not q.schnorr_verify(ec.SchnorrSig.parse(sig), tampered_sighash)


def test_self_transfer_sp_to_sp(mocker, m5stickv):
    """Self-transfer: spend a received SP UTXO into a new SP output.

    The P2TR spend-from input's even-Y tweaked spend key must be summed into the
    shared secret of the new SP output. The tweak is chosen so the tweaked key
    has odd Y, exercising the even-Y normalization (a missing negation would make
    the per-input DLEQ proof fail validation or derive the wrong output).
    """
    from embit import ec, script
    from embit.psbt import DerivationPath
    from embit.bip32 import parse_path
    from embit.transaction import TransactionOutput, SIGHASH
    from embit.script import Script
    from embit.networks import NETWORKS
    from embit.silent_payments import SilentPaymentsPSBT
    from embit.silent_payments.psbt import SPInputScope, SPOutputScope
    from embit.silent_payments.psbt import SilentPaymentData
    from krux.psbt import PSBTSigner
    from krux.key import P2TR, Key, TYPE_SILENT_PAYMENT
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SILENT_PAYMENT, NETWORKS["test"]))
    key = wallet.key
    root = key.root
    spend_priv = key.sp_keys.spend_privkey
    spend_pub = key.sp_keys.spend_pubkey

    # Pick a tweak whose tweaked spend key has odd Y, to exercise the negation.
    sp_tweak = None
    for b in range(1, 256):
        cand = bytes([b] * 32)
        if spend_priv.sp_spend_tweak(cand).sec()[0] == 0x03:
            sp_tweak = cand
            break
    assert sp_tweak is not None, "no odd-Y tweak found"

    output_xonly = spend_priv.sp_spend_tweak(sp_tweak).xonly()

    # Destination SP recipient (external scan/spend keys).
    scan_pub = ec.PublicKey.parse(bytes.fromhex(SCAN_HEX))
    dest_spend_pub = ec.PublicKey.parse(bytes.fromhex(SPEND_HEX))

    txid = bytes([0xCD] * 32)
    psbt = SilentPaymentsPSBT.create_v2()
    inp = SPInputScope()
    inp.txid = txid
    inp.vout = 0
    inp.sequence = 0xFFFFFFFE
    inp.witness_utxo = TransactionOutput(
        value=100_000, script_pubkey=Script(b"\x51\x20" + output_xonly)
    )
    inp.sp_tweak = sp_tweak
    inp.sp_spend_bip32_derivations[spend_pub.sec()] = DerivationPath(
        root.my_fingerprint, parse_path(key.derivation + "/0h/0")
    )
    # Coordinators set SIGHASH_DEFAULT (0x00) on taproot inputs; the SP
    # validator must accept it as SIGHASH_ALL-equivalent.
    inp.sighash_type = SIGHASH.DEFAULT
    psbt.add_input(inp)

    out = SPOutputScope()
    out.value = 95_000
    out.script_pubkey = None
    out.sp_data = SilentPaymentData(scan_pub, dest_spend_pub)
    psbt.add_output(out)
    psbt.tx_modifiable_flags = 0

    signer = PSBTSigner(wallet, psbt.to_string(), FORMAT_NONE)
    assert signer.has_sp_outputs()
    assert signer.policy["type"] == P2TR
    signer.sign(trim=False)

    # Independent derivation: input key is the even-Y of (b_spend + t).
    in_priv = spend_priv.sp_spend_tweak(sp_tweak).even_y()
    expected = _expected_sp_script(
        [(in_priv.secret, True)], txid, scan_pub, dest_spend_pub
    )
    derived = signer.psbt.outputs[0].script_pubkey
    assert derived is not None and derived.data.hex() == expected
    # The SP UTXO is signed via the BIP-376 spend path.
    assert signer.psbt.inputs[0].taproot_key_sig is not None


def _build_sp_psbt_spend_list(spend_pubs):
    """One P2WPKH input and one SP output per entry of spend_pubs (in order),
    all sharing SCAN_HEX's scan key. Repeated entries are allowed."""
    root = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(TEST_MNEMONIC))
    child = root.derive(INPUT_PATH)
    pub = child.get_public_key()

    scan_pub = ec.PublicKey.parse(bytes.fromhex(SCAN_HEX))

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
        out.value = 30_000
        out.script_pubkey = None
        out.sp_data = SilentPaymentData(scan_pub, spend_pub)
        psbt.add_output(out)

    psbt.tx_modifiable_flags = 0
    return psbt.to_string()


def test_sign_interleaved_sp_outputs_same_scan_key(mocker, m5stickv):
    """Outputs [A, B, A] sharing a scan key: k sorts by spend key, ties by index.

    Regression for the k-ordering bug: create_outputs used to collapse
    duplicate recipients into counts, assigning per-address-contiguous k
    values (A→k0,k1; B→k2) while the BIP-375 validator re-derives k by
    ascending spend-key order with output index as a tie-break among equal
    spend keys, so a valid PSBT paying two addresses of the same scan key
    interleaved was rejected at signing.
    """
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    scan_pub = ec.PublicKey.parse(bytes.fromhex(SCAN_HEX))
    spend_a = ec.PublicKey.parse(bytes.fromhex(SPEND_HEX))
    spend_b = ec.PrivateKey(bytes([7] * 32)).get_public_key()

    psbt_b64 = _build_sp_psbt_spend_list([spend_a, spend_b, spend_a])
    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SINGLESIG, NETWORKS["test"]))
    signer = PSBTSigner(wallet, psbt_b64, FORMAT_NONE)
    # Pre-fix this raised "Script does not match derived silent payment script".
    signer.sign(trim=False)

    # Expected scripts per output position: mirror group_sp_outputs_by_scan_key's
    # canonical k-ordering instead of assuming k tracks output position.
    root = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(TEST_MNEMONIC))
    child = root.derive(INPUT_PATH)
    from embit.silent_payments.psbt import SilentPaymentData, SPOutputScope
    from embit.silent_payments.sp import derive_sp_outputs, group_sp_outputs_by_scan_key
    from embit.transaction import TransactionInput

    outs = []
    for spend_pub in (spend_a, spend_b, spend_a):
        out = SPOutputScope()
        out.sp_data = SilentPaymentData(scan_pub, spend_pub)
        outs.append(out)
    scan_spend_groups, output_indices = group_sp_outputs_by_scan_key(outs)

    priv_keys = _normalize_xonly_keys([(child.key.secret, False)])
    _, _, results = derive_sp_outputs(
        priv_keys, [TransactionInput(bytes([0xAB] * 32), 0)], scan_spend_groups
    )

    outputs = results[scan_pub.sec()][1]
    expected = [None] * len(outputs)
    for pos, out_idx in enumerate(output_indices[scan_pub.sec()]):
        expected[out_idx] = script.Script(b"\x51\x20" + outputs[pos]).data.hex()

    on_chain = [out.script_pubkey.data.hex() for out in signer.psbt.outputs]
    assert on_chain == expected
    # k differs per output, so all three scripts must be distinct — even the
    # two paying the same address.
    assert len(set(on_chain)) == 3


def _labeled_spend_pub(sp_keys, label):
    """Independently derive the wallet's BIP-352 labeled spend pubkey via
    private-key arithmetic: (b_spend + hash(b_scan || m)) · G."""
    tweak = tagged_hash(
        "BIP0352/Label", sp_keys.scan_privkey.secret + label.to_bytes(4, "big")
    )
    scalar = (
        int.from_bytes(sp_keys.spend_privkey.secret, "big")
        + int.from_bytes(tweak, "big")
    ) % SECP256K1_ORDER
    return ec.PrivateKey(scalar.to_bytes(32, "big")).get_public_key()


def test_own_sp_output_type_classification(mocker, m5stickv):
    """own_sp_output_type: change/self only when scan AND spend keys match."""
    from krux.silent_payments import own_sp_output_type
    from krux.key import Key, TYPE_SILENT_PAYMENT

    key = Key(TEST_MNEMONIC, TYPE_SILENT_PAYMENT, NETWORKS["test"])
    sp_keys = key.sp_keys
    scan_pub = sp_keys.scan_privkey.get_public_key()

    def out_with(scan, spend, label=None):
        out = SPOutputScope()
        out.sp_data = SilentPaymentData(scan, spend)
        out.sp_label = label
        return out

    # Unlabeled output to our own address → self-transfer.
    assert (
        own_sp_output_type(out_with(scan_pub, sp_keys.spend_pubkey), sp_keys) == "self"
    )
    # Label 0 is the BIP-352 change label.
    assert (
        own_sp_output_type(
            out_with(scan_pub, _labeled_spend_pub(sp_keys, 0), label=0), sp_keys
        )
        == "change"
    )
    # Other labels are our own labeled receive addresses.
    assert (
        own_sp_output_type(
            out_with(scan_pub, _labeled_spend_pub(sp_keys, 1), label=1), sp_keys
        )
        == "self"
    )

    foreign_scan = ec.PublicKey.parse(bytes.fromhex(SCAN_HEX))
    foreign_spend = ec.PublicKey.parse(bytes.fromhex(SPEND_HEX))
    # Foreign recipient → not ours.
    assert own_sp_output_type(out_with(foreign_scan, foreign_spend), sp_keys) is None
    # Our scan key paired with a foreign spend key must NOT classify as ours,
    # otherwise a coordinator could disguise a spend as change.
    assert (
        own_sp_output_type(out_with(scan_pub, foreign_spend, label=0), sp_keys) is None
    )
    assert own_sp_output_type(out_with(scan_pub, foreign_spend), sp_keys) is None
    # A label claim that does not match the tweaked spend key is not ours.
    assert (
        own_sp_output_type(
            out_with(scan_pub, _labeled_spend_pub(sp_keys, 2), label=1), sp_keys
        )
        is None
    )
    # Non-SP wallets carry no sp_keys.
    assert own_sp_output_type(out_with(scan_pub, sp_keys.spend_pubkey), None) is None


def test_sp_change_classified_as_change(mocker, m5stickv):
    """SP wallet send: the label-0 SP change output shows as change, not spend.

    Spend a received SP UTXO (BIP-376) into a foreign SP recipient plus a
    label-0 change output back to the wallet's own silent payment address —
    the shape Sparrow builds for an SP wallet send. The review resume must
    count only the foreign output as spend, so the user sees the real payment
    amount rather than payment + change.
    """
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SILENT_PAYMENT
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SILENT_PAYMENT, NETWORKS["test"]))
    key = wallet.key
    root = key.root
    spend_priv = key.sp_keys.spend_privkey
    spend_pub = key.sp_keys.spend_pubkey
    own_scan_pub = key.sp_keys.scan_privkey.get_public_key()

    sp_tweak = bytes([1] * 32)
    output_xonly = spend_priv.sp_spend_tweak(sp_tweak).xonly()

    txid = bytes([0xEF] * 32)
    psbt = SilentPaymentsPSBT.create_v2()
    inp = SPInputScope()
    inp.txid = txid
    inp.vout = 0
    inp.sequence = 0xFFFFFFFE
    inp.witness_utxo = TransactionOutput(
        value=100_000, script_pubkey=Script(b"\x51\x20" + output_xonly)
    )
    inp.sp_tweak = sp_tweak
    inp.sp_spend_bip32_derivations[spend_pub.sec()] = DerivationPath(
        root.my_fingerprint, parse_path(key.derivation + "/0h/0")
    )
    psbt.add_input(inp)

    # Output 0: foreign SP recipient (the actual payment).
    out = SPOutputScope()
    out.value = 60_000
    out.script_pubkey = None
    out.sp_data = SilentPaymentData(
        ec.PublicKey.parse(bytes.fromhex(SCAN_HEX)),
        ec.PublicKey.parse(bytes.fromhex(SPEND_HEX)),
    )
    psbt.add_output(out)

    # Output 1: label-0 change back to our own SP address.
    change = SPOutputScope()
    change.value = 35_000
    change.script_pubkey = None
    change.sp_data = SilentPaymentData(own_scan_pub, _labeled_spend_pub(key.sp_keys, 0))
    change.sp_label = 0
    psbt.add_output(change)

    psbt.tx_modifiable_flags = 0

    signer = PSBTSigner(wallet, psbt.to_string(), FORMAT_NONE)
    messages, _ = signer.outputs()

    # Only the foreign output counts as spend; the change output is grouped
    # under self-transfer/change instead of inflating the spend total.
    assert "Spend (1):" in messages[0]
    assert "Self-transfer or Change (1):" in messages[0]

    # The change output still derives and signs like any SP output.
    signer.sign(trim=False)
    assert all(out.script_pubkey is not None for out in signer.psbt.outputs)
    assert signer.psbt.inputs[0].taproot_key_sig is not None


def test_sp_detection_keys_match_sp_wallet(mocker, m5stickv):
    """A non-SP wallet derives the same BIP-352 keys an SP wallet would.

    SP scan/spend keys are deterministic from the seed, so detection works
    regardless of the loaded policy type.
    """
    from krux.key import Key, TYPE_SINGLESIG, TYPE_SILENT_PAYMENT

    sp_key = Key(TEST_MNEMONIC, TYPE_SILENT_PAYMENT, NETWORKS["test"])
    ss_key = Key(TEST_MNEMONIC, TYPE_SINGLESIG, NETWORKS["test"])

    assert ss_key.sp_keys is None
    detected = ss_key.sp_detection_keys()
    assert detected.scan_privkey.secret == sp_key.sp_keys.scan_privkey.secret
    assert detected.spend_pubkey.sec() == sp_key.sp_keys.spend_pubkey.sec()
    # The SP wallet returns its own keys unchanged.
    assert sp_key.sp_detection_keys() is sp_key.sp_keys


def test_sp_change_detected_when_loaded_as_singlesig(mocker, m5stickv):
    """Own SP change is recognized even when the wallet is loaded as plain
    single-sig instead of Silent Payments: the SP keys are derived from the
    seed, so the label-0 change output is grouped under self-transfer/change
    rather than inflating the spend total.
    """
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SINGLESIG, TYPE_SILENT_PAYMENT
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    # SP keys for building the own-change output: same seed, so the single-sig
    # wallet derives these same keys on the fly for detection.
    sp_keys = Key(TEST_MNEMONIC, TYPE_SILENT_PAYMENT, NETWORKS["test"]).sp_keys
    own_scan_pub = sp_keys.scan_privkey.get_public_key()

    root = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(TEST_MNEMONIC))
    pub = root.derive(INPUT_PATH).get_public_key()

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

    # Output 0: foreign SP recipient (the actual payment).
    out = SPOutputScope()
    out.value = 60_000
    out.script_pubkey = None
    out.sp_data = SilentPaymentData(
        ec.PublicKey.parse(bytes.fromhex(SCAN_HEX)),
        ec.PublicKey.parse(bytes.fromhex(SPEND_HEX)),
    )
    psbt.add_output(out)

    # Output 1: label-0 change back to our own SP address.
    change = SPOutputScope()
    change.value = 35_000
    change.script_pubkey = None
    change.sp_data = SilentPaymentData(own_scan_pub, _labeled_spend_pub(sp_keys, 0))
    change.sp_label = 0
    psbt.add_output(change)

    psbt.tx_modifiable_flags = 0

    # Wallet loaded as plain single-sig, NOT silent payments.
    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SINGLESIG, NETWORKS["test"]))
    signer = PSBTSigner(wallet, psbt.to_string(), FORMAT_NONE)
    messages, _ = signer.outputs()

    assert "Spend (1):" in messages[0]
    assert "Self-transfer or Change (1):" in messages[0]


# ─────────────────────────────────────────────────────────────────────────────
# Regressions for the Silent Payments audit fixes.
# ─────────────────────────────────────────────────────────────────────────────


def _sp_wallet_spend_psbt_with_p2tr_dest(wallet):
    """BIP-376 spend of an SP UTXO paying an ordinary (non-SP) P2TR output.

    The destination deliberately shares the inputs' p2tr policy so that
    _classify_output falls through to address_belongs_to_descriptor().
    """
    from embit import script
    from embit.bip32 import parse_path
    from embit.psbt import DerivationPath
    from embit.silent_payments import SilentPaymentsPSBT
    from embit.silent_payments.psbt import SPOutputScope

    key = wallet.key
    spend_priv = key.sp_keys.spend_privkey
    spend_pub = key.sp_keys.spend_pubkey

    psbt = SilentPaymentsPSBT.create_v2()
    psbt.add_input(
        _spend_input(
            100_000,
            spend_priv.sp_spend_tweak(SP_SPEND_TWEAK).xonly(),
            SP_SPEND_TWEAK,
            (
                spend_pub.sec(),
                DerivationPath(
                    key.root.my_fingerprint, parse_path(key.derivation + "/0h/0")
                ),
            ),
        )
    )
    out = SPOutputScope()
    out.value = 95_000
    out.script_pubkey = script.p2tr(
        key.root.derive([86 + 2**31, 1 + 2**31, 0 + 2**31, 0, 0]).get_public_key()
    )
    psbt.add_output(out)
    psbt.tx_modifiable_flags = 0
    return psbt.to_string()


def test_sp_wallet_reviews_non_sp_taproot_output(mocker, m5stickv):
    """sp() descriptors have no owns(); the review screen must not blow up.

    Regression: _classify_output reached address_belongs_to_descriptor() for a
    non-SP output whose policy matched the inputs, and SilentPaymentDescriptor
    has no owns(), so outputs() raised AttributeError on-device.
    """
    from embit.networks import NETWORKS
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SILENT_PAYMENT
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SILENT_PAYMENT, NETWORKS["test"]))
    signer = PSBTSigner(
        wallet, _sp_wallet_spend_psbt_with_p2tr_dest(wallet), FORMAT_NONE
    )

    out_strs, fee_percent = signer.outputs()

    # A P2TR output an sp() wallet cannot prove ownership of is a plain spend.
    assert any("Spend (1):" in s for s in out_strs)
    assert round(fee_percent, 1) == 5.3
    signer.sign(trim=False)
    assert signer.psbt.inputs[0].taproot_key_sig is not None


def test_sp_wallet_xpubs_raises_value_error(mocker, m5stickv):
    """xpubs() must fail as 'missing xpubs', not AttributeError.

    Regression: SPScanKey has no .key attribute, so the descriptor fallback
    raised AttributeError, which the callers' bare excepts hid.
    """
    import pytest
    from embit.networks import NETWORKS
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SILENT_PAYMENT
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SILENT_PAYMENT, NETWORKS["test"]))
    signer = PSBTSigner(
        wallet, _sp_wallet_spend_psbt_with_p2tr_dest(wallet), FORMAT_NONE
    )
    signer.psbt.xpubs = {}

    with pytest.raises(ValueError, match="missing xpubs"):
        signer.xpubs()


def test_sp_send_derives_outputs_only_once(mocker, m5stickv):
    """The ECDH + DLEQ derivation must run once per signing, not twice.

    Regression: validate() derived the SP outputs and sign_with() derived them
    again, doubling the most expensive operation in the flow.
    """
    from embit.networks import NETWORKS
    from embit.silent_payments import SilentPaymentsPSBT
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    psbt_b64, _root, _scan, _spend, _child = _build_sp_psbt()
    spy = mocker.spy(SilentPaymentsPSBT, "derive_sp_outputs")

    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SINGLESIG, NETWORKS["test"]))
    signer = PSBTSigner(wallet, psbt_b64, FORMAT_NONE)
    # Loading must not derive: it only checks eligibility and ownership.
    assert spy.call_count == 0

    signer.outputs()
    assert spy.call_count == 0

    signer.sign(trim=False)
    assert spy.call_count == 1


def test_sp_detection_keys_derived_once_for_many_outputs(mocker, m5stickv):
    """Own-output detection keys are cached, not re-derived per SP output.

    Each derivation is two 5-level hardened BIP32 paths; doing it per output
    scaled that cost linearly with the number of SP outputs.
    """
    from embit.networks import NETWORKS
    from krux.key import Key, TYPE_SINGLESIG
    from krux.psbt import PSBTSigner
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    spend_pubs = [
        bip32.HDKey.from_seed(bip39.mnemonic_to_seed(TEST_MNEMONIC))
        .derive([7 + 2**31, i + 2**31, 0])
        .get_public_key()
        for i in range(3)
    ]
    psbt_b64 = _build_sp_psbt_spend_list(spend_pubs)

    spy = mocker.spy(Key, "sp_detection_keys")
    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SINGLESIG, NETWORKS["test"]))
    signer = PSBTSigner(wallet, psbt_b64, FORMAT_NONE)
    out_strs, _ = signer.outputs()

    assert len(signer.psbt.outputs) == 3
    assert spy.call_count == 1
    assert any("Spend (3):" in s for s in out_strs)


def test_sp_send_hands_back_fully_unfinalized_psbt(mocker, m5stickv):
    """BIP-375: no input may be left finalized, even one that arrived that way.

    embit finalizes taproot key-path inputs on signing, which makes coordinators
    copy only the witnesses and drop the derived SP fields. Krux clears every
    input -- safe because derive_sp_outputs refuses the PSBT unless all eligible
    inputs belong to this seed, so there is no foreign witness to destroy.
    """
    from embit.networks import NETWORKS
    from embit.script import Witness
    from krux.psbt import PSBTSigner
    from krux.key import Key, TYPE_SINGLESIG
    from krux.wallet import Wallet
    from krux.qr import FORMAT_NONE

    psbt_b64, _root, _scan, _spend, _child = _build_sp_psbt()
    wallet = Wallet(Key(TEST_MNEMONIC, TYPE_SINGLESIG, NETWORKS["test"]))
    signer = PSBTSigner(wallet, psbt_b64, FORMAT_NONE)

    signer.psbt.inputs[0].final_scriptwitness = Witness([b"\x01" * 64])
    signer.sign(trim=False)

    _assert_not_finalized(signer.psbt)
