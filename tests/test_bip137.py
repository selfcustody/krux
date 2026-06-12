import pytest

from .pages.home_pages.test_home import tdata

P2PKH_DERIV = "m/44h/0h/0h/0/3"
P2SH_P2WPKH_DERIV = "m/49h/0h/0h/0/3"
P2WPKH_DERIV = "m/84h/0h/0h/0/3"
P2TR_DERIV = "m/86h/0h/0h/0/3"

MESSAGE = b"krux+bip137"


@pytest.fixture
def address_for():
    def _addr(pub, script_type, network):
        from embit import script

        if script_type == "p2pkh":
            return script.p2pkh(pub).address(network=network)
        if script_type == "p2sh-p2wpkh":
            return script.p2sh(script.p2wpkh(pub)).address(network=network)
        if script_type == "p2wpkh":
            return script.p2wpkh(pub).address(network=network)
        if script_type == "p2tr":
            return script.p2tr(pub).address(network=network)
        return None

    return _addr


@pytest.fixture
def fake_raw_sig():
    def _sig(recid):
        from krux.bip137 import P2PKH_HEADER

        return bytes([P2PKH_HEADER + recid]) + b"\x00" * 64

    return _sig


@pytest.fixture
def raw_sign():
    def _sign(key, derivation, message):
        from krux.bip137 import message_commitment

        commitment = message_commitment(message)
        sig = key.sign_at(derivation, commitment)
        return (commitment, sig)

    return _sign


@pytest.fixture
def old_raw_sign():
    def _sign(key, derivation, message):
        import hashlib
        from embit import compact

        commitment = hashlib.sha256(
            hashlib.sha256(
                b"\x18Bitcoin Signed Message:\n"
                + compact.to_bytes(len(message))
                + message
            ).digest()
        ).digest()
        sig = key.sign_at(derivation, commitment)
        return (commitment, sig)

    return _sign


@pytest.fixture
def old_like_sign():
    # origin/develop (src/krux/pages/home_pages/sign_message_ui.py)
    #
    #     def _sign_at_address(self, message, derivation_str, address=""):
    #         """Signs a message at a derived Bitcoin address"""
    #
    #         derivation = bip32.parse_path(derivation_str)
    #         self._display_message_sign_prompt(
    #             message, self.fit_to_line(address, str(derivation[4]) + ". ", fixed_chars=3)
    #         )
    #
    #         if not self.prompt(t("Sign?"), BOTTOM_PROMPT_LINE):
    #             return None
    #
    #         message_hash = hashlib.sha256(
    #             hashlib.sha256(
    #                 b"\x18Bitcoin Signed Message:\n"
    #                 + compact.to_bytes(len(message))
    #                 + message
    #             ).digest()
    #         ).digest()
    #
    #         sig = self.ctx.wallet.key.sign_at(derivation, message_hash)
    #         self._display_signature(base_encode(sig, 64))
    #         return sig
    def _sign(key, derivation, message):
        import hashlib
        from embit import compact

        commitment = hashlib.sha256(
            hashlib.sha256(
                b"\x18Bitcoin Signed Message:\n"
                + compact.to_bytes(len(message))
                + message
            ).digest()
        ).digest()
        sig = key.sign_at(derivation, commitment)
        return (commitment, sig)

    return _sign


# Universally extract (@jdlcdl suggestion) all recids of sigs
@pytest.fixture
def bip137_verify(address_for):
    def _verify(sig, commitment, expected_address, network):
        from embit import ec
        from embit.util import secp256k1

        header = sig[0]
        if not 27 <= header <= 42:
            return False

        recid = (header - 27) & 3
        if 27 <= header <= 34:
            script_type = "p2pkh"
        elif 35 <= header <= 38:
            script_type = "p2sh-p2wpkh"
        else:
            script_type = "p2wpkh"

        parsed = secp256k1.ecdsa_recoverable_signature_parse_compact(sig[1:], recid)
        raw = secp256k1.ecdsa_recover(parsed, commitment)
        pub = ec.PublicKey.parse(secp256k1.ec_pubkey_serialize(raw))
        addr = address_for(pub, script_type, network)
        return addr is not None and addr == expected_address

    return _verify


# This not model Sparrow neither Electrum, instead a idealized lenient verifier
@pytest.fixture
def lenient_bip137_verify(address_for):
    def _verify(sig, commitment, expected_address, network, script_type):
        from embit import ec
        from embit.util import secp256k1

        header = sig[0]
        if not 27 <= header <= 42:
            return False
        recid = (header - 27) & 3

        parsed = secp256k1.ecdsa_recoverable_signature_parse_compact(sig[1:], recid)
        raw = secp256k1.ecdsa_recover(parsed, commitment)
        pub = ec.PublicKey.parse(secp256k1.ec_pubkey_serialize(raw))
        addr = address_for(pub, script_type, network)
        return addr is not None and addr == expected_address

    return _verify


def test_message_commitment(mocker, m5stickv, tdata):
    import binascii
    from krux.bip137 import message_commitment

    assert binascii.hexlify(message_commitment(MESSAGE)) == (
        b"6f47a0896ff0eb30d36d73ef8783f9796abc01328807835eb258ee042094df22"
    )


def test_build_header(mocker, m5stickv, fake_raw_sig):
    from krux.bip137 import (
        build_header,
        P2PKH_HEADER,
        P2SH_P2WPKH_HEADER,
        P2WPKH_HEADER,
    )

    # (script_type, expected_header_base)
    cases = [
        ("p2pkh", P2PKH_HEADER),
        ("p2sh-p2wpkh", P2SH_P2WPKH_HEADER),
        ("p2wpkh", P2WPKH_HEADER),
        ("p2tr", P2PKH_HEADER),
        ("p2wsh", P2PKH_HEADER),
    ]
    num = 0
    for case in cases:
        print("test_build_header case: ", num)
        num += 1
        script_type, header_base = case
        for recid in range(4):
            assert build_header(fake_raw_sig(recid), script_type) == header_base + recid


def test_develop_current_signatures(mocker, m5stickv, tdata, old_like_sign):
    from embit import bip32
    from krux.bip137 import (
        sign,
        P2PKH_HEADER,
        P2SH_P2WPKH_HEADER,
        P2WPKH_HEADER,
    )

    # (derivation, script_type, current_header_base)
    cases = [
        (P2PKH_DERIV, "p2pkh", P2PKH_HEADER),
        (P2SH_P2WPKH_DERIV, "p2sh-p2wpkh", P2SH_P2WPKH_HEADER),
        (P2WPKH_DERIV, "p2wpkh", P2WPKH_HEADER),
        (P2TR_DERIV, "p2tr", P2PKH_HEADER),
    ]
    key = tdata.SINGLESIG_SIGNING_KEY
    num = 0
    for case in cases:
        print("test_develop_vs_current_signatures case: ", num)
        num += 1
        derivation_str, script_type, current_header_base = case
        derivation = bip32.parse_path(derivation_str)

        develop_commitment, develop_sig = old_like_sign(key, derivation, MESSAGE)
        current_commitment, current_sig = sign(MESSAGE, key, derivation, script_type)

        assert develop_commitment == current_commitment
        assert 31 <= develop_sig[0] <= 34

        develop_recid = develop_sig[0] - P2PKH_HEADER
        current_recid = current_sig[0] - current_header_base
        assert develop_recid == current_recid
        assert current_sig[0] == current_header_base + current_recid

        assert develop_sig[1:] == current_sig[1:]


def test_bip137_verify(
    mocker,
    m5stickv,
    tdata,
    address_for,
    old_like_sign,
    bip137_verify,
    lenient_bip137_verify,
):
    from embit import bip32
    from embit.networks import NETWORKS
    from krux.bip137 import sign

    # (derivation, script_type, old_passes_strict, new_passes_strict)
    cases = [
        (P2PKH_DERIV, "p2pkh"),
        (P2SH_P2WPKH_DERIV, "p2sh-p2wpkh"),
        (P2WPKH_DERIV, "p2wpkh"),
        (P2TR_DERIV, "p2tr"),
    ]
    key = tdata.SINGLESIG_SIGNING_KEY
    network = NETWORKS["main"]
    for i, case in enumerate(cases):
        print("case %d, script=%s" % (i, case[1]))
        derivation = bip32.parse_path(case[0])
        pub = key.root.derive(derivation).to_public().key
        addr = address_for(pub, case[1], network)

        old_commitment, old_sig = old_like_sign(key, derivation, MESSAGE)
        new_commitment, new_sig = sign(MESSAGE, key, derivation, case[1])

        if case[1] == "p2pkh":
            # strict and lenient pass -> header -> p2pkh,
            assert bip137_verify(old_sig, old_commitment, addr, network)
            assert bip137_verify(new_sig, new_commitment, addr, network)
            assert lenient_bip137_verify(
                old_sig, old_commitment, addr, network, case[1]
            )
            assert lenient_bip137_verify(
                new_sig, new_commitment, addr, network, case[1]
            )
        elif case[1] == "p2tr":
            # strict: header -> check recid -> address not match -> fail
            # lenient: supplied "p2tr"; embit applies tweak on reconstruction
            assert not bip137_verify(old_sig, old_commitment, addr, network)
            assert not bip137_verify(new_sig, new_commitment, addr, network)
            assert lenient_bip137_verify(
                old_sig, old_commitment, addr, network, case[1]
            )
            assert lenient_bip137_verify(
                new_sig, new_commitment, addr, network, case[1]
            )
        else:
            # p2sh-p2wpkh / p2wpkh
            # strict: magic now in the script-type range, not by a provided one
            # lenient: both pass because not check against recid, but by a
            # supplied for address reconstruction
            assert not bip137_verify(old_sig, old_commitment, addr, network)
            assert bip137_verify(new_sig, new_commitment, addr, network)
            assert lenient_bip137_verify(
                old_sig, old_commitment, addr, network, case[1]
            )
            assert lenient_bip137_verify(
                new_sig, new_commitment, addr, network, case[1]
            )
