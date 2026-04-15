"""BIP-352 Silent Payments support.

Reference: https://github.com/bitcoin/bips/blob/master/bip-0352.mediawiki

TODO: we should eventually get rid of this file and replace with embit implementation. 
"""

from embit import bech32
from embit.ec import PublicKey
from embit.hashes import tagged_hash
from embit.util import secp256k1


# BIP-352 derivation: m/352'/coin_type'/account'/key_type'/0
# key_type: 0 = spend, 1 = scan
BIP352_PURPOSE = 352


def _bip352_derivation_path(network, account=0, is_scan_key=True):
    """Returns the BIP-352 derivation path for scan or spend key"""
    coin_type = network["bip32"]
    key_type = 1 if is_scan_key else 0
    return "m/%dh/%dh/%dh/%dh/0" % (BIP352_PURPOSE, coin_type, account, key_type)


def derive_bip352_key(root, network, account=0, is_scan_key=True):
    """Derive a BIP-352 HD key (scan or spend) from the root key"""
    path = _bip352_derivation_path(network, account, is_scan_key)
    return root.derive(path)


def encode_silent_payment_address(
    scan_privkey, spend_pubkey, label=None, network="main", version=0
):
    """Encode a BIP-352 silent payment address."""
    scan_pubkey = scan_privkey.get_public_key()

    if label is not None:
        if not isinstance(label, int):
            raise ValueError("label must be an integer")
        if not (0 <= label <= 0xFFFFFFFF):
            raise ValueError("label must be a 32-bit unsigned integer")
        label_bytes = label.to_bytes(4, "big")
        tweak = tagged_hash(
            "BIP0352/Label", scan_privkey.secret + label_bytes
        )
        spend_pubkey = PublicKey(
            secp256k1.ec_pubkey_add(
                secp256k1.ec_pubkey_parse(spend_pubkey.sec()), tweak
            )
        )

    data = bech32.convertbits(scan_pubkey.sec() + spend_pubkey.sec(), 8, 5)
    hrp = "sp" if network == "main" else "tsp"
    return bech32.bech32_encode(bech32.Encoding.BECH32M, hrp, [version] + data)
