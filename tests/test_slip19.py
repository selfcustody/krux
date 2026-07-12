import pytest

MNEMONIC_ALL = "all all all all all all all all all all all all"
MNEMONIC_ABANDON = (
    "abandon abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon about"
)


def test_slip21_and_p2wpkh_vector(m5stickv):
    from embit import script
    from embit.networks import NETWORKS
    from krux.key import Key, P2WPKH, TYPE_SINGLESIG
    from krux.slip19 import create_proof, proof_digest, verify_proof

    key = Key(
        MNEMONIC_ALL,
        TYPE_SINGLESIG,
        NETWORKS["main"],
        script_type=P2WPKH,
    )
    script_pubkey = script.Script(
        bytes.fromhex("0014b2f771c370ccf219cd3059cda92bdf7f00cf2103")
    )
    proof = create_proof(
        key,
        P2WPKH,
        script_pubkey,
        "m/84h/0h/0h/1/0",
        b"",
    )

    assert key.slip21_key(["SLIP-0019", "Ownership identification key"]).hex() == (
        "0a115a171e30f8a740bae6c4144bec5dc1099ffa79b83dfb8aa3501d094de585"
    )
    assert proof[:38].hex() == (
        "534c00190001"
        "a122407efc198211c81af4450f40b235d54775efd934d16b9e31c6ce9bad5707"
    )
    assert proof_digest(proof[:38], script_pubkey, b"").hex() == (
        "850dd556283b49d80fa5501035b4775e62f0c80bf36f62d1adf2f2f9f108c884"
    )
    assert verify_proof(proof, script_pubkey, b"")


def test_p2tr_proof_uses_tweaked_key(m5stickv):
    from embit import script
    from embit.networks import NETWORKS
    from krux.key import Key, P2TR, TYPE_SINGLESIG
    from krux.slip19 import create_proof, proof_body, proof_digest, verify_proof

    key = Key(
        MNEMONIC_ALL,
        TYPE_SINGLESIG,
        NETWORKS["main"],
        script_type=P2TR,
    )
    path = "m/86h/0h/0h/1/0"
    pubkey = key.root.derive(path).key.get_public_key()
    script_pubkey = script.p2tr(pubkey)
    commitment = b"coldcard-spike-commitment"

    proof = create_proof(key, P2TR, script_pubkey, path, commitment, flags=1)
    assert verify_proof(proof, script_pubkey, commitment, require_confirmation=True)

    body = proof_body(1, [key.slip19_ownership_id(script_pubkey)])
    digest = proof_digest(body, script_pubkey, commitment)
    untweaked_sig = key.root.derive(path).schnorr_sign(digest)
    bad_proof = (
        body
        + script.Script().serialize()
        + script.Witness([untweaked_sig.serialize()]).serialize()
    )
    with pytest.raises(ValueError, match="invalid P2TR"):
        verify_proof(bad_proof, script_pubkey, commitment)


def test_slip19_rejects_malformed_proofs(m5stickv):
    from embit import script
    from krux.slip19 import MAGIC, parse_proof, proof_body, proof_digest

    with pytest.raises(ValueError, match="reserved"):
        proof_body(0xFE, [])
    with pytest.raises(ValueError, match="missing commitment"):
        proof_digest(proof_body(0, []), b"", None)
    with pytest.raises(ValueError, match="magic"):
        parse_proof(b"bad")
    with pytest.raises(ValueError, match="reserved"):
        parse_proof(MAGIC + b"\xfe\x00")
    with pytest.raises(ValueError, match="non-minimal"):
        parse_proof(MAGIC + b"\x00\xfd\x00\x00")
    with pytest.raises(ValueError, match="ownership id"):
        parse_proof(MAGIC + b"\x00\x01" + b"\x00" * 31)

    proof = proof_body(0, []) + script.Script().serialize()
    proof += script.Witness([]).serialize() + b"\x00"
    with pytest.raises(ValueError, match="signature proof"):
        parse_proof(proof)


def test_slip19_rejects_invalid_create_requests(m5stickv):
    from embit import script
    from embit.networks import NETWORKS
    from krux.key import Key, P2WPKH, TYPE_SINGLESIG
    from krux.slip19 import create_proof

    key = Key(
        MNEMONIC_ALL,
        TYPE_SINGLESIG,
        NETWORKS["main"],
        script_type=P2WPKH,
    )
    path = "m/84h/0h/0h/1/0"
    pubkey = key.root.derive("m/84h/0h/0h/1/1").key.get_public_key()

    with pytest.raises(ValueError, match="unsupported"):
        create_proof(key, "p2sh", script.p2wpkh(pubkey), path, b"")
    with pytest.raises(ValueError, match="missing commitment"):
        create_proof(key, P2WPKH, script.p2wpkh(pubkey), path, None)
    with pytest.raises(ValueError, match="derivation"):
        create_proof(key, P2WPKH, script.p2wpkh(pubkey), path, b"")


def test_slip19_rejects_invalid_p2wpkh_verification(m5stickv):
    from embit import script
    from embit.networks import NETWORKS
    from krux.key import Key, P2WPKH, TYPE_SINGLESIG
    from krux.slip19 import create_proof, parse_proof, verify_proof

    key = Key(
        MNEMONIC_ALL,
        TYPE_SINGLESIG,
        NETWORKS["main"],
        script_type=P2WPKH,
    )
    path = "m/84h/0h/0h/1/0"
    pubkey = key.root.derive(path).key.get_public_key()
    script_pubkey = script.p2wpkh(pubkey)
    proof = create_proof(key, P2WPKH, script_pubkey, path, b"")
    body, _, _, _, witness = parse_proof(proof)

    with pytest.raises(ValueError, match="lacks user confirmation"):
        verify_proof(proof, script_pubkey, b"", require_confirmation=True)

    bad_script_sig = script.Script(b"\x51").serialize()
    bad_proof = body + bad_script_sig + witness.serialize()
    with pytest.raises(ValueError, match="scriptSig"):
        verify_proof(bad_proof, script_pubkey, b"")

    bad_proof = body + script.Script().serialize() + script.Witness([]).serialize()
    with pytest.raises(ValueError, match="P2WPKH.*witness"):
        verify_proof(bad_proof, script_pubkey, b"")

    bad_sig = bytearray(witness.items[0])
    bad_sig[-1] = 2
    bad_witness = script.Witness([bytes(bad_sig), witness.items[1]])
    bad_proof = body + script.Script().serialize() + bad_witness.serialize()
    with pytest.raises(ValueError, match="sighash"):
        verify_proof(bad_proof, script_pubkey, b"")

    other_pubkey = key.root.derive("m/84h/0h/0h/1/1").key.get_public_key()
    with pytest.raises(ValueError, match="does not match"):
        verify_proof(proof, script.p2wpkh(other_pubkey), b"")

    with pytest.raises(ValueError, match="invalid P2WPKH"):
        verify_proof(proof, script_pubkey, b"wrong")

    with pytest.raises(ValueError, match="unsupported"):
        verify_proof(
            body + script.Script().serialize() + witness.serialize(), b"\x6a", b""
        )


def test_slip19_rejects_invalid_p2tr_witness(m5stickv):
    from embit import script
    from embit.networks import NETWORKS
    from krux.key import Key, P2TR, TYPE_SINGLESIG
    from krux.slip19 import create_proof, parse_proof, verify_proof

    key = Key(
        MNEMONIC_ALL,
        TYPE_SINGLESIG,
        NETWORKS["main"],
        script_type=P2TR,
    )
    path = "m/86h/0h/0h/1/0"
    pubkey = key.root.derive(path).key.get_public_key()
    script_pubkey = script.p2tr(pubkey)
    proof = create_proof(key, P2TR, script_pubkey, path, b"")
    body, _, _, _, _ = parse_proof(proof)

    bad_proof = body + script.Script().serialize() + script.Witness([]).serialize()
    with pytest.raises(ValueError, match="P2TR.*witness"):
        verify_proof(bad_proof, script_pubkey, b"")


def _coinjoin_psbt(key):
    from embit import bip32, script
    from embit.psbt import DerivationPath, PSBT
    from embit.transaction import Transaction, TransactionInput, TransactionOutput

    input_path = bip32.parse_path("m/84h/1h/0h/0/0")
    output_path = bip32.parse_path("m/84h/1h/0h/1/0")
    input_pub = key.root.derive(input_path).key.get_public_key()
    output_pub = key.root.derive(output_path).key.get_public_key()
    external_pub = key.root.derive("m/84h/1h/1h/0/0").key.get_public_key()

    tx = Transaction(
        vin=[TransactionInput(b"\x01" * 32, 0)],
        vout=[
            TransactionOutput(9600, script.p2wpkh(output_pub)),
            TransactionOutput(300, script.p2wpkh(external_pub)),
        ],
    )
    psbt = PSBT(tx)
    psbt.inputs[0].witness_utxo = TransactionOutput(10000, script.p2wpkh(input_pub))
    psbt.inputs[0].bip32_derivations[input_pub] = DerivationPath(
        key.fingerprint, input_path
    )
    psbt.outputs[0].bip32_derivations[output_pub] = DerivationPath(
        key.fingerprint, output_path
    )
    return psbt


def _coinjoin_p2tr_psbt(key):
    from embit import bip32, script
    from embit.psbt import DerivationPath, PSBT
    from embit.transaction import Transaction, TransactionInput, TransactionOutput

    input_path = bip32.parse_path("m/86h/1h/0h/0/0")
    output_path = bip32.parse_path("m/86h/1h/0h/1/0")
    input_pub = key.root.derive(input_path).key.get_public_key()
    output_pub = key.root.derive(output_path).key.get_public_key()
    external_pub = key.root.derive("m/86h/1h/1h/0/0").key.get_public_key()

    tx = Transaction(
        vin=[TransactionInput(b"\x01" * 32, 0)],
        vout=[
            TransactionOutput(9600, script.p2tr(output_pub)),
            TransactionOutput(300, script.p2tr(external_pub)),
        ],
    )
    psbt = PSBT(tx)
    psbt.inputs[0].witness_utxo = TransactionOutput(10000, script.p2tr(input_pub))
    psbt.inputs[0].taproot_bip32_derivations[input_pub] = (
        [],
        DerivationPath(key.fingerprint, input_path),
    )
    psbt.outputs[0].taproot_bip32_derivations[output_pub] = (
        [],
        DerivationPath(key.fingerprint, output_path),
    )
    return psbt


class FakeWallet:
    def __init__(self, key, policy_type):
        self.key = key
        self.policy = {"type": policy_type}
        self.descriptor = None

    def is_miniscript(self):
        return False

    def is_multisig(self):
        return False

    def is_loaded(self):
        return True


def test_coinjoin_policy_signs_and_rejects_low_self_transfer(m5stickv):
    from embit.networks import NETWORKS
    from krux.key import Key, P2WPKH, TYPE_SINGLESIG
    from krux.psbt import PSBTSigner

    key = Key(
        MNEMONIC_ABANDON,
        TYPE_SINGLESIG,
        NETWORKS["test"],
        script_type=P2WPKH,
    )
    wallet = FakeWallet(key, P2WPKH)
    signer = PSBTSigner(wallet, _coinjoin_psbt(key).serialize(), None)
    policy = {
        "enabled": True,
        "allowed_scripts": (P2WPKH,),
        "allowed_account_prefix": "m/84h/1h/0h",
        "min_self_transfer_pct": 95,
        "max_fee_rate_sat_vb": 6,
    }

    assert signer.coinjoin_amounts(policy) == {
        "own_input_value": 10000,
        "own_self_transfer_value": 9600,
        "fee_leak": 400,
    }
    signer.sign_coinjoin(policy, trim=False)
    assert signer.psbt.inputs[0].partial_sigs

    strict_policy = dict(policy)
    strict_policy["max_fee_rate_sat_vb"] = 5
    signer = PSBTSigner(wallet, _coinjoin_psbt(key).serialize(), None)
    with pytest.raises(ValueError, match="fee rate above"):
        signer.sign_coinjoin(strict_policy)

    strict_policy = dict(policy)
    strict_policy["min_self_transfer_pct"] = 99
    signer = PSBTSigner(wallet, _coinjoin_psbt(key).serialize(), None)
    with pytest.raises(ValueError, match="self-transfer below"):
        signer.sign_coinjoin(strict_policy)

    invalid_policy = dict(policy)
    invalid_policy["min_self_transfer_pct"] = -1
    signer = PSBTSigner(wallet, _coinjoin_psbt(key).serialize(), None)
    with pytest.raises(ValueError, match="policy out of range"):
        signer.sign_coinjoin(invalid_policy)

    invalid_policy = dict(policy)
    invalid_policy["max_fee_rate_sat_vb"] = -1
    signer = PSBTSigner(wallet, _coinjoin_psbt(key).serialize(), None)
    with pytest.raises(ValueError, match="fee rate policy out of range"):
        signer.sign_coinjoin(invalid_policy)


def test_coinjoin_policy_rejects_invalid_psbts(m5stickv):
    from embit import script
    from embit.networks import NETWORKS
    from embit.psbt import DerivationPath
    from embit.transaction import SIGHASH
    from krux.key import Key, P2WPKH, TYPE_SINGLESIG
    from krux.psbt import PSBTSigner

    key = Key(
        MNEMONIC_ABANDON,
        TYPE_SINGLESIG,
        NETWORKS["test"],
        script_type=P2WPKH,
    )
    wallet = FakeWallet(key, P2WPKH)
    policy = {
        "enabled": True,
        "allowed_scripts": (P2WPKH,),
        "allowed_account_prefix": "m/84h/1h/0h",
        "min_self_transfer_pct": 95,
        "max_fee_rate_sat_vb": 6,
    }

    signer = PSBTSigner(wallet, _coinjoin_psbt(key).serialize(), None)
    assert signer._coinjoin_policy(None)["allowed_account_prefix"] == key.derivation
    with pytest.raises(ValueError, match="policy disabled"):
        signer.coinjoin_amounts({"enabled": False})
    with pytest.raises(ValueError, match="wallet fingerprint mismatch"):
        signer.coinjoin_amounts(dict(policy, wallet_fingerprint=b"\x00" * 4))

    signer = PSBTSigner(wallet, _coinjoin_psbt(key).serialize(), None)
    signer.psbt.inputs[0].witness_utxo = None
    with pytest.raises(ValueError, match="missing witness UTXO"):
        signer.coinjoin_amounts(policy)

    signer = PSBTSigner(wallet, _coinjoin_psbt(key).serialize(), None)
    with pytest.raises(ValueError, match="unsupported coinjoin input script"):
        signer.coinjoin_amounts(dict(policy, allowed_scripts=()))

    psbt = _coinjoin_psbt(key)
    psbt.outputs[0].script_pubkey = script.Script(b"\x51")
    signer = PSBTSigner(wallet, psbt.serialize(), None)
    with pytest.raises(ValueError, match="unsupported coinjoin output script"):
        signer.coinjoin_amounts(policy)

    signer = PSBTSigner(wallet, _coinjoin_psbt(key).serialize(), None)
    with pytest.raises(ValueError, match="has no own inputs"):
        signer.coinjoin_amounts(dict(policy, allowed_account_prefix="m/84h/1h/1h"))

    signer = PSBTSigner(wallet, _coinjoin_psbt(key).serialize(), None)
    pub = next(iter(signer.psbt.inputs[0].bip32_derivations))
    signer.psbt.inputs[0].bip32_derivations[pub] = DerivationPath(
        b"\x00" * 4, signer.psbt.inputs[0].bip32_derivations[pub].derivation
    )
    with pytest.raises(ValueError, match="has no own inputs"):
        signer.coinjoin_amounts(policy)

    signer = PSBTSigner(wallet, _coinjoin_psbt(key).serialize(), None)
    signer.psbt.inputs[0].sighash_type = SIGHASH.NONE
    with pytest.raises(ValueError, match="SIGHASH_ALL"):
        signer.coinjoin_amounts(policy)

    with pytest.raises(ValueError, match="unsupported coinjoin input script"):
        signer._coinjoin_input_vbytes_x100("bad")


def test_coinjoin_policy_supports_taproot_and_legacy_bps(m5stickv):
    from embit.networks import NETWORKS
    from embit.transaction import SIGHASH
    from krux.key import Key, P2TR, P2WPKH, TYPE_SINGLESIG
    from krux.psbt import PSBTSigner

    p2wpkh_key = Key(
        MNEMONIC_ABANDON,
        TYPE_SINGLESIG,
        NETWORKS["test"],
        script_type=P2WPKH,
    )
    p2wpkh_signer = PSBTSigner(
        FakeWallet(p2wpkh_key, P2WPKH), _coinjoin_psbt(p2wpkh_key).serialize(), None
    )
    assert (
        p2wpkh_signer.coinjoin_amounts(
            {
                "enabled": True,
                "allowed_scripts": (P2WPKH,),
                "allowed_account_prefix": "m/84h/1h/0h",
                "min_self_transfer_bps": 9500,
                "max_fee_rate_sat_vb": 6,
            }
        )["own_self_transfer_value"]
        == 9600
    )

    p2tr_key = Key(
        MNEMONIC_ABANDON,
        TYPE_SINGLESIG,
        NETWORKS["test"],
        script_type=P2TR,
    )
    p2tr_policy = {
        "enabled": True,
        "allowed_scripts": (P2TR,),
        "allowed_account_prefix": "m/86h/1h/0h",
        "min_self_transfer_pct": 95,
        "max_fee_rate_sat_vb": 7,
    }
    p2tr_signer = PSBTSigner(
        FakeWallet(p2tr_key, P2TR), _coinjoin_p2tr_psbt(p2tr_key).serialize(), None
    )
    assert p2tr_signer.coinjoin_amounts(p2tr_policy)["fee_leak"] == 400

    p2tr_signer = PSBTSigner(
        FakeWallet(p2tr_key, P2TR), _coinjoin_p2tr_psbt(p2tr_key).serialize(), None
    )
    p2tr_signer.psbt.inputs[0].sighash_type = SIGHASH.ALL
    with pytest.raises(ValueError, match="SIGHASH_DEFAULT"):
        p2tr_signer.coinjoin_amounts(p2tr_policy)
