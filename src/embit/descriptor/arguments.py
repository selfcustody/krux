from binascii import hexlify, unhexlify
from .base import DescriptorBase, read_until
from .errors import ArgumentError
from .. import bip32, ec, compact, hashes


class KeyOrigin:
    def __init__(self, fingerprint: bytes, derivation: list):
        self.fingerprint = fingerprint
        self.derivation = derivation

    @classmethod
    def from_string(cls, s: str):
        arr = s.split("/")
        mfp = unhexlify(arr[0])
        assert len(mfp) == 4
        arr[0] = "m"
        path = "/".join(arr)
        derivation = bip32.parse_path(path)
        return cls(mfp, derivation)

    def __str__(self):
        return bip32.path_to_str(self.derivation, fingerprint=self.fingerprint)


class AllowedDerivation(DescriptorBase):
    # xpub/{0,1}/* - {0,1} is a set of allowed branches, wildcard * is stored as None
    def __init__(self, indexes=[[0, 1], None]):
        # check only one wildcard and only one set is in the derivation
        if len([i for i in indexes if i is None]) > 1:
            raise ArgumentError("Only one wildcard is allowed")
        if len([i for i in indexes if isinstance(i, list)]) > 1:
            raise ArgumentError("Only one wildcard is allowed")
        self.indexes = indexes

    @property
    def is_wildcard(self):
        return None in self.indexes

    def fill(self, idx, branch_index=None):
        # None is ok
        if idx is not None and (idx < 0 or idx >= 0x80000000):
            raise ArgumentError("Hardened indexes are not allowed in wildcard")
        arr = [i for i in self.indexes]
        for i, el in enumerate(arr):
            if el is None:
                arr[i] = idx
            if isinstance(el, list):
                if branch_index is None:
                    arr[i] = el[0]
                else:
                    if branch_index < 0 or branch_index >= len(el):
                        raise ArgumentError("Invalid branch index")
                    arr[i] = el[branch_index]
        return arr

    def branch(self, branch_index):
        arr = self.fill(None, branch_index)
        return type(self)(arr)

    def check_derivation(self, derivation: list):
        if len(derivation) != len(self.indexes):
            return None
        branch_idx = 0  # default branch if no branches in descriptor
        idx = None
        for i, el in enumerate(self.indexes):
            der = derivation[i]
            if isinstance(el, int):
                if el != der:
                    return None
            # branch
            elif isinstance(el, list):
                if der not in el:
                    return None
                branch_idx = el.index(der)
            # wildcard
            elif el is None:
                idx = der
            # shouldn't happen
            else:
                raise ArgumentError("Strange derivation index...")
        if branch_idx is not None and idx is not None:
            return idx, branch_idx

    @classmethod
    def default(cls):
        return AllowedDerivation([[0, 1], None])

    @property
    def branches(self):
        for el in self.indexes:
            if isinstance(el, list):
                return el
        return None

    @property
    def has_hardend(self):
        for idx in self.indexes:
            if isinstance(idx, int) and idx >= 0x80000000:
                return True
            if isinstance(idx, list) and len([i for i in idx if i >= 0x80000000]) > 0:
                return True
        return False

    @classmethod
    def from_string(cls, der: str, allow_hardened=False, allow_set=True):
        if len(der) == 0:
            return None
        indexes = [
            cls.parse_element(d, allow_hardened, allow_set) for d in der.split("/")
        ]
        return cls(indexes)

    @classmethod
    def parse_element(cls, d: str, allow_hardened=False, allow_set=True):
        # wildcard
        if d == "*":
            return None
        # branch set
        if d[0] == "{" and d[-1] == "}":
            if not allow_set:
                raise ArgumentError("Set is not allowed in derivation %s" % d)
            return [
                cls.parse_element(dd, allow_hardened, allow_set=False)
                for dd in d[1:-1].split(",")
            ]
        idx = 0
        if d[-1] == "h":
            if not allow_hardened:
                raise ArgumentError("Hardened derivation is not allowed in %s" % d)
            idx = 0x80000000
            d = d[:-1]
        i = int(d)
        if i < 0 or i >= 0x80000000:
            raise ArgumentError("Derivation index can be in a range [0, 0x80000000)")
        return idx + i

    def __str__(self):
        r = ""
        for idx in self.indexes:
            if idx is None:
                r += "/*"
            if isinstance(idx, int):
                if idx >= 0x80000000:
                    r += "/%dh" % (idx - 0x80000000)
                else:
                    r += "/%d" % idx
            if isinstance(idx, list):
                r += "/{"
                r += ",".join(
                    [
                        str(i) if i < 0x80000000 else str(i - 0x80000000) + "h"
                        for i in idx
                    ]
                )
                r += "}"
        return r


class Key(DescriptorBase):
    def __init__(self, key, origin=None, derivation=None):
        self.origin = origin
        self.key = key
        if not hasattr(key, "derive") and derivation is not None:
            raise ArgumentError("Key %s doesn't support derivation" % key)
        self.allowed_derivation = derivation

    def __len__(self):
        return 34 # <33:sec> - only compressed pubkeys

    @property
    def my_fingerprint(self):
        if self.is_extended:
            return self.key.my_fingerprint
        return None

    @property
    def fingerprint(self):
        if self.origin is not None:
            return self.origin.fingerprint
        else:
            if self.is_extended:
                return self.key.my_fingerprint
        return None

    @property
    def derivation(self):
        return [] if self.origin is None else self.origin.derivation

    @classmethod
    def read_from(cls, s):
        first = s.read(1)
        origin = None
        if first == b"[":
            prefix, char = read_until(s, b"]")
            if char != b"]":
                raise ArgumentError("Invalid key - missing ]")
            origin = KeyOrigin.from_string(prefix.decode())
        else:
            s.seek(-1, 1)
        k, char = read_until(s, b",)/")
        der = b""
        # there is a following derivation
        if char == b"/":
            der, char = read_until(s, b"{,)")
            # we get a set of possible branches: {a,b,c...}
            if char == b"{":
                der += b"{"
                branch, char = read_until(s, b"}")
                if char is None:
                    raise ArgumentError("Failed reading the key, missing }")
                der += branch + b"}"
                rest, char = read_until(s, b",)")
                der += rest
        if char is not None:
            s.seek(-1, 1)
        # parse key
        k = cls.parse_key(k)
        # parse derivation
        allow_hardened = isinstance(k, bip32.HDKey) and isinstance(k.key, ec.PrivateKey)
        derivation = AllowedDerivation.from_string(
            der.decode(), allow_hardened=allow_hardened
        )
        return cls(k, origin, derivation)

    @classmethod
    def parse_key(cls, k: bytes):
        # convert to string
        k = k.decode()
        if len(k) in [66, 130] and k[:2] in ["02", "03", "04"]:
            # bare public key
            return ec.PublicKey.parse(unhexlify(k))
        elif k[1:4] in ["pub", "prv"]:
            # bip32 key
            return bip32.HDKey.from_base58(k)
        else:
            return ec.PrivateKey.from_wif(k)

    @property
    def is_extended(self):
        return isinstance(self.key, bip32.HDKey)

    def check_derivation(self, derivation_path):
        rest = None
        # full derivation path
        if self.fingerprint == derivation_path.fingerprint:
            origin = self.derivation
            if origin == derivation_path.derivation[: len(origin)]:
                rest = derivation_path.derivation[len(origin) :]
        # short derivation path
        if self.my_fingerprint == derivation_path.fingerprint:
            rest = derivation_path.derivation
        if self.allowed_derivation is None or rest is None:
            return None
        return self.allowed_derivation.check_derivation(rest)

    def get_public_key(self):
        return self.key.get_public_key() if (self.is_extended or self.is_private) else self.key

    def sec(self):
        return self.key.sec()

    def serialize(self):
        return self.sec()

    def compile(self):
        d = self.serialize()
        return compact.to_bytes(len(d)) + d

    @property
    def prefix(self):
        if self.origin:
            return "[%s]" % self.origin
        return ""

    @property
    def suffix(self):
        return "" if self.allowed_derivation is None else str(self.allowed_derivation)

    @property
    def can_derive(self):
        return self.allowed_derivation is not None and hasattr(self.key, "derive")

    @property
    def branches(self):
        return self.allowed_derivation.branches if self.allowed_derivation else None

    @property
    def num_branches(self):
        return 1 if self.branches is None else len(self.branches)

    def branch(self, branch_index=None):
        der = self.allowed_derivation.branch(branch_index)
        return type(self)(self.key, self.origin, der)

    @property
    def is_wildcard(self):
        return self.allowed_derivation.is_wildcard if self.allowed_derivation else False

    def derive(self, idx, branch_index=None):
        # nothing to derive
        if self.allowed_derivation is None:
            return self
        der = self.allowed_derivation.fill(idx, branch_index=branch_index)
        k = self.key.derive(der)
        if self.origin:
            origin = KeyOrigin(self.origin.fingerprint, self.origin.derivation + der)
        else:
            origin = KeyOrigin(self.key.child(0).fingerprint, der)
        # empty derivation
        derivation = None
        return type(self)(k, origin, derivation)

    @property
    def is_private(self):
        return isinstance(self.key, ec.PrivateKey) or (
            self.is_extended and self.key.is_private
        )

    @property
    def private_key(self):
        if not self.is_private:
            raise ArgumentError("Key is not private")
        # either HDKey.key or just the key
        return self.key.key if self.is_extended else self.key

    @property
    def secret(self):
        return self.private_key.secret

    def to_string(self, version=None):
        if isinstance(self.key, ec.PublicKey):
            return self.prefix + hexlify(self.key.sec()).decode()
        if isinstance(self.key, bip32.HDKey):
            return self.prefix + self.key.to_base58(version) + self.suffix
        if isinstance(self.key, ec.PrivateKey):
            return self.prefix + self.key.wif()
        return self.prefix + self.key

    @classmethod
    def from_string(cls, s):
        return cls.parse(s.encode())


class KeyHash(Key):
    @classmethod
    def parse_key(cls, k: bytes):
        # convert to string
        k = k.decode()
        # raw 20-byte hash
        if len(k) == 40:
            return k
        if len(k) in [66, 130] and k[:2] in ["02", "03", "04"]:
            # bare public key
            return ec.PublicKey.parse(unhexlify(k))
        elif k[1:4] in ["pub", "prv"]:
            # bip32 key
            return bip32.HDKey.from_base58(k)
        else:
            return ec.PrivateKey.from_wif(k)

    def serialize(self):
        if isinstance(self.key, str):
            return unhexlify(self.key)
        return hashes.hash160(self.key.sec())

    def __len__(self):
        return 21 # <20:pkh>

    def compile(self):
        d = self.serialize()
        return compact.to_bytes(len(d)) + d


class Number(DescriptorBase):
    def __init__(self, num):
        self.num = num

    @classmethod
    def read_from(cls, s):
        num = 0
        char = s.read(1)
        while char in b"0123456789":
            num = 10 * num + int(char.decode())
            char = s.read(1)
        s.seek(-1, 1)
        return cls(num)

    def compile(self):
        if self.num == 0:
            return b"\x00"
        if self.num <= 16:
            return bytes([80 + self.num])
        b = self.num.to_bytes(32, "little").rstrip(b"\x00")
        if b[-1] >= 128:
            b += b"\x00"
        return bytes([len(b)]) + b

    def __len__(self):
        return len(self.compile())

    def __str__(self):
        return "%d" % self.num


class Raw(DescriptorBase):
    def __init__(self, raw):
        if len(raw) != self.LEN * 2:
            raise ArgumentError("Invalid raw element length: %d" % len(raw))
        self.raw = unhexlify(raw)

    @classmethod
    def read_from(cls, s):
        return cls(s.read(2 * cls.LEN).decode())

    def __str__(self):
        return hexlify(self.raw).decode()

    def compile(self):
        return compact.to_bytes(len(self.raw)) + self.raw

    def __len__(self):
        return len(compact.to_bytes(self.LEN)) + self.LEN

class Raw32(Raw):
    LEN = 32
    def __len__(self):
        return 33

class Raw20(Raw):
    LEN = 20
    def __len__(self):
        return 21
