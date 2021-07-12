from ..descriptor.descriptor import *
from .networks import NETWORKS
from .addresses import address
from . import slip77
from ..hashes import tagged_hash, sha256
from ..ec import PrivateKey, PublicKey, secp256k1

class LDescriptor(Descriptor):
    """Liquid descriptor that supports blinded() wrapper"""
    def __init__(self, *args, blinding_key=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.blinding_key = blinding_key

    @property
    def is_blinded(self):
        return self.blinding_key is not None

    def address(self, network=NETWORKS["liquidv1"]):
        sc = self.script_pubkey()
        if not self.is_blinded:
            return sc.address(network)
        bkey = self.blinding_key.get_blinding_key(sc)
        return address(sc, bkey, network)

    def derive(self, idx, branch_index=None):
        d = super().derive(idx, branch_index)
        if self.is_blinded:
            blinding_key = self.blinding_key.derive(idx, branch_index)
            d.blinding_key = blinding_key
        return d

    @property
    def is_slip77(self):
        return self.is_blinded and self.blinding_key.slip77

    @property
    def master_blinding_key(self):
        if self.is_slip77:
            return self.blinding_key.key.secret

    def branch(self, branch_index=None):
        d = super().branch(branch_index)
        if self.is_blinded:
            blinding_key = self.blinding_key.branch(branch_index)
            d.blinding_key = blinding_key
        return d

    @classmethod
    def read_from(cls, s):
        # starts with blinded(K,...) or directly with sh(wsh()), sh() or wsh()
        start = s.read(8)
        if not start.startswith(b"blinded("):
            s.seek(-8, 1)
            d = Descriptor.read_from(s)
            return cls(d.miniscript, sh=d.sh, wsh=d.wsh, key=d.key, wpkh=d.wpkh, blinding_key=None)

        blinding_key = BlindingKey.read_from(s)
        if s.read(1) != b",":
            raise DescriptorError("Missing bitcoin descriptor")
        d = Descriptor.read_from(s)
        if s.read(1) != b")":
            raise DescriptorError("Missing ending bracket")
        if not blinding_key.slip77:
            if blinding_key.is_wildcard != d.is_wildcard:
                raise DescriptorError("Wildcards mismatch in blinded key and descriptor")
            if blinding_key.num_branches != d.num_branches:
                raise DescriptorError("Branches mismatch in blinded key and descriptor")
        return cls(d.miniscript, sh=d.sh, wsh=d.wsh, key=d.key, wpkh=d.wpkh, blinding_key=blinding_key)

    def to_string(self, blinded=True):
        res = super().to_string()
        if self.is_blinded and blinded:
            res = "blinded(%s,%s)" % (self.blinding_key, res)
        return res

class BlindingKey(DescriptorBase):
    def __init__(self, key, slip77=False):
        self.key = key
        self.slip77 = slip77

    def derive(self, idx, branch_index=None):
        if self.slip77:
            return self
        else:
            return type(self)(self.key.derive(idx, branch_index), self.slip77)

    def branch(self, branch_index=None):
        if self.slip77:
            return self
        else:
            return type(self)(self.key.branch(branch_index), self.slip77)

    @property
    def is_wildcard(self):
        if not self.slip77:
            return self.key.is_wildcard

    @property
    def num_branches(self):
        if not self.slip77:
            return self.key.num_branches

    def get_blinding_key(self, sc):
        if self.slip77:
            return slip77.blinding_key(self.key.private_key, sc)
        # if not slip77 - make a script tweak to the key
        tweak = tagged_hash("elements/blindingkey", sc.data)
        if self.key.is_private:
            secret = secp256k1.ec_privkey_add(self.key.secret, tweak)
            # negate if it's odd
            if ec.PrivateKey(secret).sec()[0] == 0x03:
                 secp256k1.ec_privkey_negate(secret)
            return ec.PrivateKey(secret)
        else:
            pub = secp256k1.ec_pubkey_add(secp256k1.ec_pubkey_parse(self.key.sec()), tweak)
            if secp256k1.ec_pubkey_serialize(pub)[0] == 0x03:
                secp256k1.ec_pubkey_negate(pub)
            return ec.PublicKey(pub)

    @classmethod
    def read_from(cls, s):
        start = s.read(7)
        slip77 = False
        if start.startswith(b"slip77("):
            slip77 = True
            key = Key.read_from(s)
            if key.is_extended or not key.is_private:
                raise DescriptorError("SLIP-77 key should be a WIF private key")
            if s.read(1) != b")":
                raise DescriptorError("Missing closing bracket after slip77")
        elif start.startswith(b"musig("):
            s.seek(-7, 1)
            key = MuSigKey.read_from(s)
        else:
            s.seek(-7, 1)
            key = Key.read_from(s)
        return cls(key, slip77)

    def to_string(self):
        if self.slip77:
            return "slip77(%s)" % self.key
        else:
            return str(self.key)

class MuSigKey(DescriptorBase):
    def __init__(self, keys):
        self.keys = keys
        self._secret = None
        self._pubkey = None

    def derive(self, idx, branch_index=None):
        return type(self)([k.derive(idx, branch_index) for k in self.keys])

    def to_string(self):
        return "musig(%s)" % (",".join([str(k) for k in self.keys]))

    @property
    def is_wildcard(self):
        return any([key.is_wildcard for key in self.keys])

    @property
    def num_branches(self):
        return max([k.num_branches for k in self.keys])

    @classmethod
    def read_from(cls, s):
        start = s.read(6)
        if start != b"musig(":
            raise DescriptorError("Expected musig()")
        keys = []
        while True:
            keys.append(Key.read_from(s))
            c = s.read(1)
            if c == b")":
                break
            if c != b",":
                raise DescriptorError("Expected , in musig")
        return cls(keys)

    @property
    def is_private(self):
        return all([k.is_private for k in self.keys])

    @property
    def secret(self):
        if self._secret is None:
            self._secret = musig_combine_privs([k.secret for k in self.keys])
        return self._secret

    def sec(self):
        if self._pubkey is None:
            pubs = [secp256k1.ec_pubkey_parse(k.sec()) for k in self.keys]
            pub = musig_combine_pubs(pubs)
            self._pubkey = PublicKey(pub)
        return self._pubkey.sec()

def musig_combine_privs(privs, sort=True):
    keys = [[b""+prv, secp256k1.ec_pubkey_serialize(secp256k1.ec_pubkey_create(prv))] for prv in privs]
    for karr in keys:
        if karr[1][0] == 0x03:
            secp256k1.ec_privkey_negate(karr[0])
        # x only
        karr[1] = karr[1][1:]
    if sort:
        keys = list(sorted(keys, key=lambda k: k[1]))
    secs = [k[1] for k in keys]
    ll = sha256(b"".join(secs))
    coefs = [tagged_hash("MuSig coefficient", ll+i.to_bytes(4,'little')) for i in range(len(keys))]
    # tweak them all
    for i in range(len(keys)):
        secp256k1.ec_privkey_tweak_mul(coefs[i], keys[i][0])
    s = coefs[0]
    for c in coefs[1:]:
        s = secp256k1.ec_privkey_add(s, c)
    pub = secp256k1.ec_pubkey_create(s)
    if secp256k1.ec_pubkey_serialize(pub)[0] == 0x03:
        secp256k1.ec_privkey_negate(s)
    return s

def musig_combine_pubs(pubs, sort=True):
    keys = [[pub, secp256k1.ec_pubkey_serialize(pub)] for pub in pubs]
    for karr in keys:
        if karr[1][0] == 0x03:
            secp256k1.ec_pubkey_negate(karr[0])
        # x only
        karr[1] = karr[1][1:]
    if sort:
        keys = list(sorted(keys, key=lambda k: k[1]))
    secs = [k[1] for k in keys]
    ll = sha256(b"".join(secs))
    coefs = [tagged_hash("MuSig coefficient", ll+i.to_bytes(4,'little')) for i in range(len(keys))]
    # tweak them all
    pubs = [k[0] for k in keys]
    for i in range(len(keys)):
        secp256k1.ec_pubkey_tweak_mul(pubs[i], coefs[i])
    pub = secp256k1.ec_pubkey_combine(*pubs)
    if secp256k1.ec_pubkey_serialize(pub)[0] == 0x03:
        secp256k1.ec_pubkey_negate(pub)
    return pub
