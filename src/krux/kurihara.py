# The MIT License (MIT)

# Copyright (c) 2021-2026 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
Kurihara ideal (k, n)-threshold XOR secret sharing.

Reference scheme: J. Kurihara, S. Kiyomoto, K. Fukushima, T. Tanaka,
"A New (k, n)-Threshold Secret Sharing Scheme and Its Extension", ISC 2008,
https://eprint.iacr.org/2008/409

BIP39 adaptation, pen-and-paper derivation, security-property verification and
ready-to-print templates: CaverneCrypto, "Bitcoin Mnemonic Backup via Threshold
XOR (n-of-m): A pen-and-paper adaptation of the Kurihara scheme to BIP39", 2026,
https://doi.org/10.5281/zenodo.20734041 (CC BY 4.0).

This is the pure, UI-less core of an n-of-m threshold backup. It splits a secret
(BIP39 entropy) into m shares such that any n of them reconstruct it, while any
n - 1 reveal nothing (perfect, information-theoretic confidentiality up to the
threshold). Each share is exactly the size of the secret, so it re-encodes to a
valid BIP39 mnemonic of the same word count -- a true threshold generalization
of Krux's existing m-of-m "Mnemonic XOR" (SeedXOR), which has no loss tolerance.

Only XOR is used; there is no finite-field arithmetic beyond GF(2). The module
has no hardware dependency: the randomness source is injected into generate(),
and embit is imported lazily only for the BIP39 glue helpers.

Construction (with fragment 0 fixed to zero by convention):

    W[i][pos] = XOR over t of  R[t][(t*i + pos) mod prime]
                XOR  fragment[(pos - i) mod prime]

where prime is the smallest prime >= m, the fragments are the prime-1 pieces of
the secret, and the R[t] are (n-1) sets of prime uniform random values.
"""

from binascii import hexlify

# Standard BIP39 entropy sizes, in bits
VALID_ENTROPY_BITS = (128, 160, 192, 224, 256)


def xor_bytes(*chunks):
    """XOR several byte sequences of equal length"""
    out = bytearray(len(chunks[0]))
    for chunk in chunks:
        for i in range(len(chunk)):
            out[i] ^= chunk[i]
    return bytes(out)


def is_prime(num):
    """Return True if num is a prime number"""
    if num < 2:
        return False
    if num < 4:
        return True
    if num % 2 == 0:
        return False
    i = 3
    while i * i <= num:
        if num % i == 0:
            return False
        i += 2
    return True


def smallest_prime_gte(num):
    """Return the smallest prime greater than or equal to num"""
    candidate = num if num > 2 else 2
    while not is_prime(candidate):
        candidate += 1
    return candidate


class Share:
    """One share of the split.

    part_id: 1-based share number (S_1, S_2, ...).
    pieces: list of prime-1 byte chunks of d_bytes each.
    meta: dict of instance parameters, shared across sibling shares.
    """

    def __init__(self, part_id, pieces, meta):
        self.part_id = part_id
        self.pieces = pieces
        self.meta = meta

    def to_bytes(self):
        """Concatenated pieces: exactly num_bits, a valid BIP39 entropy"""
        return b"".join(self.pieces)


class KuriharaScheme:
    """Kurihara n-of-m ideal threshold XOR secret-sharing scheme"""

    def __init__(self, n, m, num_bits):
        if not 2 <= n <= m:
            raise ValueError("Need 2 <= n <= m")
        if num_bits not in VALID_ENTROPY_BITS:
            raise ValueError("Not a standard BIP39 entropy size")
        self.n = n
        self.m = m
        self.num_bits = num_bits
        self.prime = smallest_prime_gte(m)
        self.num_fragments = self.prime - 1
        if (
            num_bits % self.num_fragments != 0
            or (num_bits // self.num_fragments) % 8 != 0
        ):
            raise ValueError("num_bits does not split into byte-aligned fragments")
        self.d_bytes = num_bits // self.num_fragments // 8

    def _split_secret(self, secret):
        """Split the secret into prime-1 fragments; fragment 0 is zero"""
        zero = bytes(self.d_bytes)
        fragments = [zero]
        for j in range(self.num_fragments):
            fragments.append(secret[j * self.d_bytes : (j + 1) * self.d_bytes])
        return fragments

    def _gen_random(self, randfunc):
        """Draw (n-1) sets of prime random values"""
        return [
            [randfunc(self.d_bytes) for _ in range(self.prime)]
            for _ in range(self.n - 1)
        ]

    def _piece(self, i, pos, fragments, randoms):
        """Compute the piece W[i][pos] from the Kurihara formula"""
        terms = []
        for t in range(self.n - 1):
            terms.append(randoms[t][(t * i + pos) % self.prime])
        terms.append(fragments[(pos - i) % self.prime])
        return xor_bytes(*terms)

    def generate(self, secret, randfunc):
        """Build m shares with threshold n.

        secret: num_bits / 8 bytes of entropy to protect.
        randfunc: callable(nbytes) -> bytes, the injected randomness source
        (e.g. the device TRNG, or dice). Required so the core stays free of any
        hardware dependency and stays deterministic under test.
        """
        if len(secret) != self.num_bits // 8:
            raise ValueError("Secret must be %d bytes" % (self.num_bits // 8))
        fragments = self._split_secret(secret)
        randoms = self._gen_random(randfunc)
        instance = hexlify(randfunc(4)).decode()
        meta = {
            "instance": instance,
            "n": self.n,
            "m": self.m,
            "num_bits": self.num_bits,
            "prime": self.prime,
        }
        shares = []
        for i in range(self.m):
            pieces = [
                self._piece(i, pos, fragments, randoms)
                for pos in range(self.num_fragments)
            ]
            shares.append(Share(i + 1, pieces, dict(meta)))
        return shares

    def reconstruct(self, shares):
        """Reconstruct the secret from at least n shares"""
        self._check_coalition(shares)
        fragments, _ = self._solve([(s.part_id - 1, s.pieces) for s in shares])
        out = []
        for j in range(1, self.prime):
            out.append(fragments[j])
        return b"".join(out)

    def reconstruct_lost(self, shares, lost_id):
        """Regenerate the lost share S_{lost_id} (1-based) from n others.

        The result is bit-for-bit identical to the original share thanks to the
        shift symmetry of the random values: any choice for the residual free
        variables yields the same recomputed pieces.
        """
        self._check_coalition(shares)
        if not 1 <= lost_id <= self.m:
            raise ValueError("Share id out of range")
        i_lost = lost_id - 1
        for s in shares:
            if s.part_id - 1 == i_lost:
                raise ValueError("Lost share is already in the coalition")
        fragments, randoms = self._solve([(s.part_id - 1, s.pieces) for s in shares])
        pieces = [
            self._piece(i_lost, pos, fragments, randoms)
            for pos in range(self.num_fragments)
        ]
        return Share(lost_id, pieces, dict(shares[0].meta))

    def _check_coalition(self, shares):
        """Ensure enough shares, all from the same instance"""
        if len(shares) < self.n:
            raise ValueError("Need %d shares" % self.n)
        ref = shares[0].meta.get("instance")
        for s in shares[1:]:
            if s.meta.get("instance") != ref:
                raise ValueError("Shares come from different instances")

    def _solve(self, observed):
        """Solve the Kurihara linear system for the observed pieces.

        Each piece is one linear equation over GF(2^d). The GF(2) coefficient
        row is a set of active column indices (XOR of two rows = symmetric
        difference), which keeps the elimination free of big-integer bitmasks
        and portable to MicroPython.

        Column layout:
            R[t][ell]    -> t * prime + ell
            fragment[j]  -> num_r + (j - 1)   (fragment 0 is absorbed)

        Returns (fragments, randoms). Structurally free variables stay zero;
        this affects neither the fragments nor any regenerated share piece.
        """
        num_r = (self.n - 1) * self.prime
        num_vars = num_r + self.num_fragments

        equations = []
        for i, pieces in observed:
            for pos in range(self.num_fragments):
                cols = set()
                for t in range(self.n - 1):
                    cols.add(t * self.prime + (t * i + pos) % self.prime)
                k_idx = (pos - i) % self.prime
                if k_idx != 0:
                    cols.add(num_r + (k_idx - 1))
                equations.append([cols, pieces[pos]])

        pivot_of = {}
        used = set()
        for col in range(num_vars):
            pivot = None
            for row in range(len(equations)):
                if row not in used and col in equations[row][0]:
                    pivot = row
                    break
            if pivot is None:
                continue
            pivot_of[col] = pivot
            used.add(pivot)
            p_cols, p_val = equations[pivot]
            for row in range(len(equations)):
                if row != pivot and col in equations[row][0]:
                    equations[row][0] = equations[row][0] ^ p_cols
                    equations[row][1] = xor_bytes(equations[row][1], p_val)

        zero = bytes(self.d_bytes)
        fragments = [zero] * self.prime
        for j in range(1, self.prime):
            col = num_r + (j - 1)
            if col not in pivot_of:
                raise ValueError("Fragment undetermined: not enough shares?")
            fragments[j] = equations[pivot_of[col]][1]

        randoms = [[zero] * self.prime for _ in range(self.n - 1)]
        for t in range(self.n - 1):
            for ell in range(self.prime):
                col = t * self.prime + ell
                if col in pivot_of:
                    randoms[t][ell] = equations[pivot_of[col]][1]

        return fragments, randoms


# BIP39 glue. A share's concatenated pieces are exactly num_bits, i.e. a
# standard BIP39 entropy, so each share re-encodes to a valid mnemonic of the
# same word count. embit is imported lazily so the core above stays dependency
# free (mirrors krux.pages.home_pages.mnemonic_xor).


def entropy_to_mnemonic(entropy):
    """Encode BIP39 entropy bytes as a mnemonic"""
    from embit.bip39 import mnemonic_from_bytes

    return mnemonic_from_bytes(entropy)


def mnemonic_to_entropy(mnemonic):
    """Decode a BIP39 mnemonic to its entropy bytes"""
    from embit.bip39 import mnemonic_to_bytes

    return mnemonic_to_bytes(mnemonic.strip())


def share_to_mnemonic(share):
    """Encode a share as a BIP39 mnemonic (its pieces, concatenated)"""
    return entropy_to_mnemonic(share.to_bytes())


def share_from_mnemonic(part_id, mnemonic, n, m, num_bits, instance="input"):
    """Decode a BIP39 mnemonic into a Share for the given parameters"""
    entropy = mnemonic_to_entropy(mnemonic)
    if len(entropy) * 8 != num_bits:
        raise ValueError("Mnemonic entropy size does not match num_bits")
    prime = smallest_prime_gte(m)
    d_bytes = num_bits // (prime - 1) // 8
    pieces = [entropy[pos * d_bytes : (pos + 1) * d_bytes] for pos in range(prime - 1)]
    meta = {
        "instance": instance,
        "n": n,
        "m": m,
        "num_bits": num_bits,
        "prime": prime,
    }
    return Share(part_id, pieces, meta)
