from binascii import unhexlify
import pytest
from embit.ec import PrivateKey


BASIC_TEST_VECTORS = [
    {
        "scan_priv_key": "0f694e068028a717f8af6b9411f9a133dd3565258714cc226594b34db90c1f2c",
        "spend_priv_key": "9d6ad855ce3417ef84e836892e5a56392bfba05fa5d97ccea30e266f540e08b3",
        "sp_address": "sp1qqgste7k9hx0qftg6qmwlkqtwuy6cycyavzmzj85c6qdfhjdpdjtdgqjuexzk6murw56suy3e0rd2cgqvycxttddwsvgxe2usfpxumr70xc9pkqwv",
    },
    {
        "scan_priv_key": "0000000000000000000000000000000000000000000000000000000000000002",
        "spend_priv_key": "0000000000000000000000000000000000000000000000000000000000000001",
        "sp_address": "sp1qqtrqglu5g8kh6mfsg4qxa9wq0nv9cauwfwxw70984wkqnw2uwz0w2qnehen8a7wuhwk9tgrzjh8gwzc8q2dlekedec5djk0js9d3d7qhnq6lqj3s",
    },
]

LABEL_TEST_VECTORS = {
    "scan_priv_key": "0f694e068028a717f8af6b9411f9a133dd3565258714cc226594b34db90c1f2c",
    "spend_priv_key": "9d6ad855ce3417ef84e836892e5a56392bfba05fa5d97ccea30e266f540e08b3",
    "labels": [2, 3, 1001337],
    "addresses": [
        "sp1qqgste7k9hx0qftg6qmwlkqtwuy6cycyavzmzj85c6qdfhjdpdjtdgqjex54dmqmmv6rw353tsuqhs99ydvadxzrsy9nuvk74epvee55drs734pqq",
        "sp1qqgste7k9hx0qftg6qmwlkqtwuy6cycyavzmzj85c6qdfhjdpdjtdgqsg59z2rppn4qlkx0yz9sdltmjv3j8zgcqadjn4ug98m3t6plujsq9qvu5n",
        "sp1qqgste7k9hx0qftg6qmwlkqtwuy6cycyavzmzj85c6qdfhjdpdjtdgq7c2zfthc6x3a5yecwc52nxa0kfd20xuz08zyrjpfw4l2j257yq6qgnkdh5",
    ],
}


def test_generate_silent_payment_address(m5stickv):
    """Basic SP address derivation against BIP-352 official test vectors"""
    from krux.silent_payment import encode_silent_payment_address

    for v in BASIC_TEST_VECTORS:
        scan_privkey = PrivateKey(unhexlify(v["scan_priv_key"]))
        spend_pubkey = PrivateKey(unhexlify(v["spend_priv_key"])).get_public_key()
        assert encode_silent_payment_address(scan_privkey, spend_pubkey) == v["sp_address"]


def test_generate_labeled_silent_payment_address(m5stickv):
    """Labeled SP address derivation against BIP-352 official test vectors"""
    from krux.silent_payment import encode_silent_payment_address

    scan_privkey = PrivateKey(unhexlify(LABEL_TEST_VECTORS["scan_priv_key"]))
    spend_pubkey = PrivateKey(unhexlify(LABEL_TEST_VECTORS["spend_priv_key"])).get_public_key()

    for label, expected in zip(LABEL_TEST_VECTORS["labels"], LABEL_TEST_VECTORS["addresses"]):
        assert encode_silent_payment_address(scan_privkey, spend_pubkey, label=label) == expected

    with pytest.raises(ValueError):
        encode_silent_payment_address(scan_privkey, spend_pubkey, label=1.0)
