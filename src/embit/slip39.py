import hmac
import sys
import hashlib
from .bip39 import mnemonic_from_bytes, mnemonic_to_bytes

from .wordlists.uslip39 import SLIP39_WORDS

try:
    # if urandom is available from os module:
    from os import urandom as _urandom
except:
    # otherwise - try reading from /dev/urandom
    def _urandom(n):
        with open("/dev/urandom", "rb") as f:
            return f.read(n)

def _getrandbits(k):
    b = _urandom(k//8+1)
    return int.from_bytes(b,'big') % (2**k)

def secure_randint(vmin:int, vmax:int) -> int:
    """
    Normal random.randint uses PRNG that is not suitable
    for cryptographic applications.
    This one uses os.urandom for randomness.
    """
    import math
    assert vmax > vmin
    delta = vmax - vmin
    nbits = math.ceil(math.log2(delta+1))
    randn = _getrandbits(nbits)
    while randn > delta:
        randn = _getrandbits(nbits)
    return vmin + randn

# functions for SLIP39 checksum
def rs1024_polymod(values):
    GEN = [
        0xE0E040,
        0x1C1C080,
        0x3838100,
        0x7070200,
        0xE0E0009,
        0x1C0C2412,
        0x38086C24,
        0x3090FC48,
        0x21B1F890,
        0x3F3F120,
    ]
    chk = 1
    for v in values:
        b = chk >> 20
        chk = (chk & 0xFFFFF) << 10 ^ v
        for i in range(10):
            chk ^= GEN[i] if ((b >> i) & 1) else 0
    return chk


def rs1024_verify_checksum(cs, data):
    return rs1024_polymod([x for x in cs] + data) == 1


def rs1024_create_checksum(cs, data):
    values = [x for x in cs] + data
    polymod = rs1024_polymod(values + [0, 0, 0]) ^ 1
    return [(polymod >> 10 * (2 - i)) & 1023 for i in range(3)]


# function for encryption/decryption
def _crypt(payload, id, exponent, passphrase, indices):
    if len(payload) % 2:
        raise ValueError("payload should be an even number of bytes")
    else:
        half = len(payload) // 2
    left = payload[:half]
    right = payload[half:]
    salt = b"shamir" + id.to_bytes(2, "big")
    for i in indices:
        f = hashlib.pbkdf2_hmac(
            "sha256",
            i + passphrase,
            salt + right,
            2500 << exponent,
            half,
        )
        left, right = right, bytes(x ^ y for x, y in zip(left, f))
    return right + left


class Share:
    def __init__(
        self,
        share_bit_length,
        id,
        exponent,
        group_index,
        group_threshold,
        group_count,
        member_index,
        member_threshold,
        value,
    ):
        self.share_bit_length = share_bit_length
        self.id = id
        self.exponent = exponent
        self.group_index = group_index
        if group_index < 0 or group_index > 15:
            raise ValueError(
                "Group index should be between 0 and 15 inclusive"
            )
        self.group_threshold = group_threshold
        if group_threshold < 1 or group_threshold > group_count:
            raise ValueError(
                "Group threshold should be between 1 and %d inclusive" % group_count
            )
        self.group_count = group_count
        if group_count < 1 or group_count > 16:
            raise ValueError(
                "Group count should be between 1 and 16 inclusive"
            )
        self.member_index = member_index
        if member_index < 0 or member_index > 15:
            raise ValueError(
                "Member index should be between 0 and 15 inclusive"
            )
        self.member_threshold = member_threshold
        if member_threshold < 1 or member_threshold > 16:
            raise ValueError(
                "Member threshold should be between 1 and 16 inclusive"
            )
        self.value = value
        self.bytes = value.to_bytes(share_bit_length // 8, "big")

    @classmethod
    def parse(cls, mnemonic):
        # convert mnemonic into bits
        words = mnemonic.split()
        indices = [SLIP39_WORDS.index(word) for word in words]
        if not rs1024_verify_checksum(b"shamir", indices):
            raise ValueError("Invalid Checksum")
        id = (indices[0] << 5) | (indices[1] >> 5)
        exponent = indices[1] & 31
        group_index = indices[2] >> 6
        group_threshold = ((indices[2] >> 2) & 15) + 1
        group_count = (((indices[2] & 3) << 2) | (indices[3] >> 8)) + 1
        member_index = (indices[3] >> 4) & 15
        member_threshold = (indices[3] & 15) + 1
        value = 0
        for index in indices[4:-3]:
            value = (value << 10) | index
        share_bit_length = (len(indices) - 7) * 10 // 16 * 16
        if value >> share_bit_length != 0:
            raise SyntaxError("Share not 0-padded properly")
        if share_bit_length < 128:
            raise ValueError("not enough bits")
        return cls(
            share_bit_length,
            id,
            exponent,
            group_index,
            group_threshold,
            group_count,
            member_index,
            member_threshold,
            value,
        )

    def mnemonic(self):
        all_bits = (self.id << 5) | self.exponent
        all_bits <<= 4
        all_bits |= self.group_index
        all_bits <<= 4
        all_bits |= self.group_threshold - 1
        all_bits <<= 4
        all_bits |= self.group_count - 1
        all_bits <<= 4
        all_bits |= self.member_index
        all_bits <<= 4
        all_bits |= self.member_threshold - 1
        padding = 10 - self.share_bit_length % 10
        all_bits <<= padding + self.share_bit_length
        all_bits |= self.value
        num_words = 4 + (padding + self.share_bit_length) // 10
        indices = [
            (all_bits >> 10 * (num_words - i - 1)) & 1023 for i in range(num_words)
        ]
        checksum = rs1024_create_checksum(b"shamir", indices)
        return " ".join([SLIP39_WORDS[index] for index in indices + checksum])


class ShareSet:
    @classmethod
    def _load(cls):
        """Pre-computes the exponent/log for LaGrange calculation"""
        cls.exp = [0] * 255
        cls.log2 = [0] * 256
        cur = 1
        for i in range(255):
            cls.exp[i] = cur
            cls.log2[cur] = i
            cur = (cur << 1) ^ cur
            if cur > 255:
                cur ^= 0x11B

    def __init__(self, shares):
        self.shares = shares
        if len(shares) > 1:
            # check that the identifiers are the same
            ids = {s.id for s in shares}
            if len(ids) != 1:
                raise TypeError("Shares are from different secrets")
            # check that the exponents are the same
            exponents = {s.exponent for s in shares}
            if len(exponents) != 1:
                raise TypeError("Shares should have the same exponent")
            # check that the k-of-n is the same
            k = {s.group_threshold for s in shares}
            if len(k) != 1:
                raise ValueError("K of K-of-N should be the same")
            n = {s.group_count for s in shares}
            if len(n) != 1:
                raise ValueError("N of K-of-N should be the same")
            if k.pop() > n.pop():
                raise ValueError("K > N in K-of-N")
            # check that the share lengths are the same
            lengths = {s.share_bit_length for s in shares}
            if len(lengths) != 1:
                raise ValueError("all shares should have the same length")
            # check that the x coordinates are unique
            xs = {(s.group_index, s.member_index) for s in shares}
            if len(xs) != len(shares):
                raise ValueError("Share indices should be unique")
        self.id = shares[0].id
        self.salt = b"shamir" + self.id.to_bytes(2, "big")
        self.exponent = shares[0].exponent
        self.group_threshold = shares[0].group_threshold
        self.group_count = shares[0].group_count
        self.share_bit_length = shares[0].share_bit_length

    def decrypt(self, secret, passphrase=b""):
        # decryption does the reverse of encryption
        indices = (b"\x03", b"\x02", b"\x01", b"\x00")
        return _crypt(secret, self.id, self.exponent, passphrase, indices)

    @classmethod
    def encrypt(cls, payload, id, exponent, passphrase=b""):
        # encryption goes from 0 to 3 in bytes
        indices = (b"\x00", b"\x01", b"\x02", b"\x03")
        return _crypt(payload, id, exponent, passphrase, indices)

    @classmethod
    def interpolate(cls, x, share_data):
        """Gets the y value at a particular x"""
        # we're using the LaGrange formula
        # https://github.com/satoshilabs/slips/blob/master/slip-0039/lagrange.png
        # the numerator of the multiplication part is what we're pre-computing
        # (x - x_i) 0<=i<=m where x_i is each x in the share
        # we don't store this, but the log of this
        # and exponentiate later
        log_product = sum(cls.log2[share_x ^ x] for share_x, _ in share_data)
        # the y value that we want is stored in result
        result = bytes(len(share_data[0][1]))
        for share_x, share_bytes in share_data:
            # we have to subtract the current x - x_i since
            # the formula is for j where j != i
            log_numerator = log_product - cls.log2[share_x ^ x]
            # the denominator we can just sum because we cheated and made
            # log(0) = 0 which will happen when i = j
            log_denominator = sum(
                cls.log2[share_x ^ other_x] for other_x, _ in share_data
            )
            log = (log_numerator - log_denominator) % 255
            result = bytes(
                c ^ (cls.exp[(cls.log2[y] + log) % 255] if y > 0 else 0)
                for y, c in zip(share_bytes, result)
            )
        return result

    @classmethod
    def digest(cls, r, shared_secret):
        return hmac.new(r, shared_secret, "sha256").digest()[:4]

    @classmethod
    def recover_secret(cls, share_data):
        """return a shared secret from a list of shares"""
        shared_secret = cls.interpolate(255, share_data)
        digest_share = cls.interpolate(254, share_data)
        digest = digest_share[:4]
        random = digest_share[4:]
        if digest != cls.digest(random, shared_secret):
            raise ValueError("Digest does not match secret")
        return shared_secret

    def recover(self, passphrase=b""):
        """recover a shared secret from the current group of shares"""
        # group by group index
        groups = [[] for _ in range(self.group_count)]
        for share in self.shares:
            groups[share.group_index].append(share)
        # gather share data of each group
        share_data = []
        for i, group in enumerate(groups):
            if len(group) == 0:
                continue
            member_thresholds = {share.member_threshold for share in group}
            if len(member_thresholds) != 1:
                raise ValueError("Member thresholds should be the same within a group")
            member_threshold = member_thresholds.pop()
            if member_threshold == 1:
                share_data.append((i, group[0].bytes))
            elif member_threshold > len(group):
                raise ValueError("Not enough shares")
            else:
                member_data = [(share.member_index, share.bytes) for share in group]
                share_data.append((i, self.recover_secret(member_data)))
        if self.group_threshold == 1:
            return self.decrypt(share_data[0][1], passphrase)
        elif self.group_threshold > len(share_data):
            raise ValueError("Not enough shares")
        shared_secret = self.recover_secret(share_data)
        return self.decrypt(shared_secret, passphrase)

    @classmethod
    def split_secret(cls, secret, k, n, randint=secure_randint):
        """Split secret into k-of-n shares"""
        if n < 1:
            raise ValueError("N is too small, must be at least 1")
        if n > 16:
            raise ValueError("N is too big, must be 16 or less")
        if k < 1:
            raise ValueError("K is too small, must be at least 1")
        if k > n:
            raise ValueError("K is too big, K <= N")
        num_bytes = len(secret)
        if num_bytes not in (16, 32):
            raise ValueError("secret should be 128 bits or 256 bits")
        if k == 1:
            return [(0, secret)]
        else:
            r = bytes(randint(0, 255) for _ in range(num_bytes - 4))
            digest = cls.digest(r, secret)
            digest_share = digest + r
            share_data = [
                (i, bytes(randint(0, 255) for _ in range(num_bytes))) for i in range(k - 2)
            ]
            more_data = share_data.copy()
            share_data.append((254, digest_share))
            share_data.append((255, secret))
            for i in range(k - 2, n):
                more_data.append((i, cls.interpolate(i, share_data)))
        return more_data

    @classmethod
    def generate_shares(cls, mnemonic, k, n, passphrase=b"", exponent=0, randint=secure_randint):
        """Takes a BIP39 mnemonic along with k, n, passphrase and exponent.
        Returns a list of SLIP39 mnemonics, any k of of which, along with the passphrase, recover the secret"""
        # convert mnemonic to a shared secret
        secret = mnemonic_to_bytes(mnemonic)
        num_bits = len(secret) * 8
        if num_bits not in (128, 256):
            raise ValueError("mnemonic must be 12 or 24 words")
        # generate id
        id = randint(0, 32767)
        # encrypt secret with passphrase
        encrypted = cls.encrypt(secret, id, exponent, passphrase)
        # split encrypted payload and create shares
        shares = []
        data = cls.split_secret(encrypted, k, n, randint=randint)
        for group_index, share_bytes in data:
            share = Share(
                share_bit_length=num_bits,
                id=id,
                exponent=exponent,
                group_index=group_index,
                group_threshold=k,
                group_count=n,
                member_index=0,
                member_threshold=1,
                value=int.from_bytes(share_bytes, "big"),
            )
            shares.append(share.mnemonic())
        return shares

    @classmethod
    def recover_mnemonic(cls, share_mnemonics, passphrase=b""):
        """Recovers the BIP39 mnemonic from a bunch of SLIP39 mnemonics"""
        shares = [Share.parse(m) for m in share_mnemonics]
        share_set = ShareSet(shares)
        secret = share_set.recover(passphrase)
        return mnemonic_from_bytes(secret)


ShareSet._load()
