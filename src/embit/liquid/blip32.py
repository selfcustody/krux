"""BIP-32 for blinding keys. Non-standard yet!!!"""
import sys
from .. import bip32, ec
from .networks import NETWORKS
import hmac

class BlindingHDKey(bip32.HDKey):
    @classmethod
    def from_seed(cls, seed: bytes, version=NETWORKS["liquidv1"]["xprv"]):
        raw = hmac.new(b"Elements blinding seed", seed, digestmod="sha512").digest()
        private_key = ec.PrivateKey(raw[:32])
        chain_code = raw[32:]
        return cls(private_key, chain_code, version=version)
