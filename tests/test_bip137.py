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
        import secrets
        from krux.bip137 import P2PKH_HEADER

        return bytes([P2PKH_HEADER + recid]) + secrets.token_bytes(64)

    return _sig


@pytest.fixture
def lenient_sign():
    def _sign(key, derivation, message):
        import hashlib
        from embit import compact
        from krux.bip137 import MESSAGE_MAGIC

        commitment = hashlib.sha256(
            hashlib.sha256(
                MESSAGE_MAGIC + compact.to_bytes(len(message)) + message
            ).digest()
        ).digest()
        sig = key.sign_at(derivation, commitment)
        return (commitment, sig)

    return _sign


# An idealized strict verifier (Sparrow >=2.5.x).
#
# The numbers are defined in BIP137 and means and
# each one produces different check addresses:
#
# - 27-30: uncompressed-pubkey p2pkh
# - 31-34: compressed-pubkey p2pkh
# - 35-38: compressed-pubkey p2sh-p2wpkh (p2sh ones are found here)
# - >38: compressed-pubkey p2wpkh and beyond
@pytest.fixture
def strict_verify(address_for):
    def _verify(sig, commitment, expected_address, network):
        from embit import ec
        from embit.util import secp256k1

        header = sig[0]
        if not 27 <= header <= 42:
            return False

        recid = (header - 27) & 3
        if 27 <= header <= 30:
            script_type, flag = "p2pkh", secp256k1.EC_UNCOMPRESSED
        elif 31 <= header <= 34:
            script_type, flag = "p2pkh", secp256k1.EC_COMPRESSED
        elif 35 <= header <= 38:
            script_type, flag = "p2sh-p2wpkh", secp256k1.EC_COMPRESSED
        else:
            script_type, flag = "p2wpkh", secp256k1.EC_COMPRESSED

        parsed = secp256k1.ecdsa_recoverable_signature_parse_compact(sig[1:], recid)
        raw = secp256k1.ecdsa_recover(parsed, commitment)
        pub = ec.PublicKey.parse(secp256k1.ec_pubkey_serialize(raw, flag))
        addr = address_for(pub, script_type, network)
        return addr is not None and addr == expected_address

    return _verify


# Idealized lenient verifier (Sparrow  <2.5.x/ Electrum).
#
# By lenient we mean that the verification still occurs for recids and flags,
# but the script type and thus address, will be trusted by a provided script
# type, not by a checked one.
@pytest.fixture
def lenient_verify(address_for):
    def _verify(sig, commitment, expected_address, network, script_type):
        from embit import ec
        from embit.util import secp256k1

        header = sig[0]
        if not 27 <= header <= 42:
            return False
        recid = (header - 27) & 3
        flag = (
            secp256k1.EC_UNCOMPRESSED if 27 <= header <= 30 else secp256k1.EC_COMPRESSED
        )

        parsed = secp256k1.ecdsa_recoverable_signature_parse_compact(sig[1:], recid)
        raw = secp256k1.ecdsa_recover(parsed, commitment)
        pub = ec.PublicKey.parse(secp256k1.ec_pubkey_serialize(raw, flag))
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
        # lenient ones could sign p2tr using this conversion
        ("p2tr", P2PKH_HEADER),
        ("p2wsh", P2PKH_HEADER),
    ]
    for i, case in enumerate(cases):
        print("Case: %d", i)
        for recid in range(4):
            assert build_header(fake_raw_sig(recid), case[0]) == case[1] + recid


def test_fail_build_header(mocker, m5stickv):
    from krux.bip137 import build_header

    for bad in (0, 26, 35, 255):
        raw = bytes([bad]) + b"\x00" * 64
        with pytest.raises(ValueError, match="Invalid sig header"):
            build_header(raw, "p2pkh")


def test_lenient_signatures(mocker, m5stickv, tdata, lenient_sign):
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
        # lenient ones could sign p2tr using this conversion
        (P2TR_DERIV, "p2tr", P2PKH_HEADER),
    ]
    key = tdata.SINGLESIG_SIGNING_KEY
    for i, case in enumerate(cases):
        print("Case: %d ", i)
        derivation_str, script_type, current_header_base = case
        derivation = bip32.parse_path(derivation_str)

        lenient_commitment, lenient_sig = lenient_sign(key, derivation, MESSAGE)
        strict_commitment, strict_sig = sign(MESSAGE, key, derivation, script_type)

        assert lenient_commitment == strict_commitment

        # lenient sigs should sig on lenient verifiers
        assert 31 <= lenient_sig[0] <= 34
        lenient_recid = lenient_sig[0] - P2PKH_HEADER
        strict_recid = strict_sig[0] - case[2]
        assert lenient_recid == strict_recid
        assert strict_sig[0] == case[2] + strict_recid
        assert lenient_sig[1:] == strict_sig[1:]


def test_strict_signatures(
    mocker,
    m5stickv,
    tdata,
    address_for,
    lenient_sign,
    lenient_verify,
    strict_verify,
):
    from embit import bip32
    from embit.networks import NETWORKS
    from krux.bip137 import sign

    key = tdata.SINGLESIG_SIGNING_KEY
    network = NETWORKS["main"]

    # Now we will not rely on provided script type
    # (derivation, script_type) to strict_verify and lenient_verify
    cases = [
        (P2PKH_DERIV, "p2pkh"),
        (P2SH_P2WPKH_DERIV, "p2sh-p2wpkh"),
        (P2WPKH_DERIV, "p2wpkh"),
        (P2TR_DERIV, "p2tr"),
    ]

    for i, case in enumerate(cases):
        print("Case %d, script=%s" % (i, case[1]))
        derivation = bip32.parse_path(case[0])
        pub = key.root.derive(derivation).to_public().key
        addr = address_for(pub, case[1], network)

        old_commitment, old_sig = lenient_sign(key, derivation, MESSAGE)
        new_commitment, new_sig = sign(MESSAGE, key, derivation, case[1])

        if case[1] == "p2pkh":
            # build_header returns P2PKH_HEADER; old_sig == new_sig bytewise
            assert strict_verify(new_sig, new_commitment, addr, network)
            assert lenient_verify(new_sig, new_commitment, addr, network, case[1])
        elif case[1] == "p2tr":
            # Strict rejects (BIP-137 has no taproot scheme)
            assert not strict_verify(new_sig, new_commitment, addr, network)
            assert lenient_verify(new_sig, new_commitment, addr, network, case[1])
        else:
            # Strict accepts only the new form; lenient accepts both old
            # and new header formats (for Sparrow <2.5.x / Electrum compatibility).
            assert not strict_verify(old_sig, old_commitment, addr, network)
            assert strict_verify(new_sig, new_commitment, addr, network)
            assert lenient_verify(old_sig, old_commitment, addr, network, case[1])
            assert lenient_verify(new_sig, new_commitment, addr, network, case[1])


def test_verify_uncompressed_p2pkh(
    mocker, m5stickv, tdata, lenient_sign, strict_verify, lenient_verify
):
    from embit import bip32, script
    from embit.networks import NETWORKS
    from krux.bip137 import (
        P2PKH_HEADER,
        P2PKH_UNCOMPRESSED_HEADER,
        sign,
    )

    # Same secret, two distinct p2pkh addresses (compressed && uncompressed)
    key = tdata.SINGLESIG_SIGNING_KEY
    network = NETWORKS["main"]
    derivation = bip32.parse_path(P2PKH_DERIV)
    pub = key.root.derive(derivation).to_public().key

    # compressed addr from uncompressed key
    compressed_addr = script.p2pkh(pub).address(network=network)
    pub.compressed = False
    uncompressed_addr = script.p2pkh(pub).address(network=network)

    # check if the compressed addr not match the uncompressed addr one
    assert compressed_addr != uncompressed_addr

    lenient_commitment, lenient_sig = lenient_sign(key, derivation, MESSAGE)
    uncompressed_commitment, uncompressed_sig = sign(
        MESSAGE, key, derivation, "p2pkh", compressed=False
    )

    assert uncompressed_sig[0] >= P2PKH_UNCOMPRESSED_HEADER
    assert uncompressed_sig[0] < P2PKH_HEADER
    assert strict_verify(
        uncompressed_sig, uncompressed_commitment, uncompressed_addr, network
    )
    assert lenient_verify(
        uncompressed_sig, uncompressed_commitment, uncompressed_addr, network, "p2pkh"
    )
    assert not strict_verify(
        lenient_sig, lenient_commitment, uncompressed_addr, network
    )
    assert not lenient_verify(
        lenient_sig, lenient_commitment, uncompressed_addr, network, "p2pkh"
    )
