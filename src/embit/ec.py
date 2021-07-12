import sys

if sys.implementation.name == "micropython":
    import secp256k1
else:
    from .util import secp256k1
from . import base58
from .networks import NETWORKS
from .base import EmbitBase, EmbitError, EmbitKey
from binascii import hexlify, unhexlify


class ECError(EmbitError):
    pass


class PublicKey(EmbitKey):
    def __init__(self, point: bytes, compressed: bool = True):
        self._point = point
        self.compressed = compressed

    @classmethod
    def read_from(cls, stream):
        b = stream.read(1)
        if b not in [b"\x02", b"\x03", b"\x04"]:
            raise ECError("Invalid public key")
        if b == b"\x04":
            b += stream.read(64)
        else:
            b += stream.read(32)
        try:
            point = secp256k1.ec_pubkey_parse(b)
        except Exception as e:
            raise ECError(str(e))
        compressed = b[0] != 0x04
        return cls(point, compressed)

    def sec(self) -> bytes:
        """Sec representation of the key"""
        flag = secp256k1.EC_COMPRESSED if self.compressed else secp256k1.EC_UNCOMPRESSED
        return secp256k1.ec_pubkey_serialize(self._point, flag)

    def write_to(self, stream) -> int:
        return stream.write(self.sec())

    def serialize(self) -> bytes:
        return self.sec()

    def verify(self, sig, msg_hash) -> bool:
        return bool(secp256k1.ecdsa_verify(sig._sig, msg_hash, self._point))

    @classmethod
    def from_string(cls, s):
        return cls.parse(unhexlify(s))

    @property
    def is_private(self) -> bool:
        return False

    def to_string(self):
        return hexlify(self.sec()).decode()

    def __lt__(self, other):
        # for lexagraphic ordering
        return self.sec() < other.sec()

    def __gt__(self, other):
        # for lexagraphic ordering
        return self.sec() > other.sec()

    def __eq__(self, other):
        return self._point == other._point

    def __hash__(self):
        return hash(self._point)


class PrivateKey(EmbitKey):
    def __init__(self, secret, compressed: bool = True, network=None):
        """Creates a private key from 32-byte array"""
        if len(secret) != 32:
            raise ECError("Secret should be 32-byte array")
        if not secp256k1.ec_seckey_verify(secret):
            raise ECError("Secret is not valid (larger then N?)")
        self.compressed = compressed
        self._secret = secret
        if network is None:
            network = NETWORKS["main"]
        self.network = network

    def wif(self, network=None) -> str:
        """Export private key as Wallet Import Format string.
        Prefix 0x80 is used for mainnet, 0xEF for testnet.
        This class doesn't store this information though.
        """
        if network is None:
            network = self.network
        prefix = network["wif"]
        b = prefix + self._secret
        if self.compressed:
            b += bytes([0x01])
        return base58.encode_check(b)

    @property
    def secret(self):
        return self._secret

    def sec(self) -> bytes:
        """Sec representation of the corresponding public key"""
        return self.get_public_key().sec()

    @classmethod
    def from_wif(cls, s):
        """Import private key from Wallet Import Format string."""
        b = base58.decode_check(s)
        prefix = b[:1]
        network = None
        for net in NETWORKS:
            if NETWORKS[net]["wif"] == prefix:
                network = NETWORKS[net]
        secret = b[1:33]
        compressed = False
        if len(b) not in [33, 34]:
            raise ECError("Wrong WIF length")
        if len(b) == 34:
            if b[-1] == 0x01:
                compressed = True
            else:
                raise ECError("Wrong WIF compressed flag")
        return cls(secret, compressed, network)

    # to unify API
    def to_base58(self, network=None) -> str:
        return self.wif(network)

    @classmethod
    def from_base58(cls, s):
        return cls.from_wif(s)

    def get_public_key(self):
        return PublicKey(secp256k1.ec_pubkey_create(self._secret), self.compressed)

    def sign(self, msg_hash):
        return Signature(secp256k1.ecdsa_sign(msg_hash, self._secret))

    def write_to(self, stream) -> int:
        # return a copy of the secret
        return stream.write(self._secret)

    @classmethod
    def read_from(cls, stream):
        # just to unify the API
        return cls(stream.read(32))

    @property
    def is_private(self) -> bool:
        return True


class Signature(EmbitBase):
    def __init__(self, sig):
        self._sig = sig

    def write_to(self, stream) -> int:
        return stream.write(secp256k1.ecdsa_signature_serialize_der(self._sig))

    @classmethod
    def read_from(cls, stream):
        der = stream.read(2)
        der += stream.read(der[1])
        return cls(secp256k1.ecdsa_signature_parse_der(der))
