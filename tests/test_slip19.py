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


def test_coinjoin_policy_signs_and_rejects_low_self_transfer(m5stickv):
    from embit.networks import NETWORKS
    from krux.key import Key, P2WPKH, TYPE_SINGLESIG
    from krux.psbt import PSBTSigner

    class FakeWallet:
        def __init__(self, key):
            self.key = key
            self.policy = {"type": P2WPKH}
            self.descriptor = None

        def is_miniscript(self):
            return False

        def is_multisig(self):
            return False

        def is_loaded(self):
            return True

    key = Key(
        MNEMONIC_ABANDON,
        TYPE_SINGLESIG,
        NETWORKS["test"],
        script_type=P2WPKH,
    )
    wallet = FakeWallet(key)
    signer = PSBTSigner(wallet, _coinjoin_psbt(key).serialize(), None)
    policy = {
        "enabled": True,
        "allowed_scripts": (P2WPKH,),
        "allowed_account_prefix": "m/84h/1h/0h",
        "min_self_transfer_bps": 9500,
        "max_leak_sats": 500,
    }

    assert signer.coinjoin_amounts(policy) == {
        "own_input_value": 10000,
        "own_self_transfer_value": 9600,
        "fee_leak": 400,
    }
    signer.sign_coinjoin(policy, trim=False)
    assert signer.psbt.inputs[0].partial_sigs

    strict_policy = dict(policy)
    strict_policy["min_self_transfer_bps"] = 9900
    signer = PSBTSigner(wallet, _coinjoin_psbt(key).serialize(), None)
    with pytest.raises(ValueError, match="self-transfer below"):
        signer.sign_coinjoin(strict_policy)
