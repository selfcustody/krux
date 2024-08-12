# Mnemonic convertion to seed and to/from bytes
import hashlib
from embit.misc import const

from embit.wordlists.bip39 import WORDLIST

PBKDF2_ROUNDS = const(2048)

WORDINDEX = {word: i for i, word in enumerate(WORDLIST)}


def mnemonic_to_bytes(mnemonic: str, ignore_checksum: bool = False, wordlist=WORDLIST):
    words = mnemonic.strip().split()
    if len(words) % 3 != 0 or len(words) < 12:
        raise ValueError("Invalid recovery phrase")

    accumulator = 0
    for word in words:
        try:
            if wordlist is WORDLIST:
                accumulator = (accumulator << 11) + WORDINDEX[word]
            else:
                accumulator = (accumulator << 11) + wordlist.index(word)
        except Exception:
            raise ValueError("Word '%s' is not in the dictionary" % word)

    entropy_length_bits = len(words) * 11 // 33 * 32
    checksum_length_bits = len(words) * 11 // 33
    checksum = accumulator & (2**checksum_length_bits -1)
    accumulator >>= checksum_length_bits
    data = accumulator.to_bytes(entropy_length_bits // 8, "big")
    computed_checksum = hashlib.sha256(data).digest()[0] >> 8 - checksum_length_bits

    if not ignore_checksum and checksum != computed_checksum:
        raise ValueError("Checksum verification failed")
    return data


def mnemonic_is_valid(mnemonic: str, wordlist=WORDLIST):
    """Checks if mnemonic is valid (checksum and words)"""
    try:
        mnemonic_to_bytes(mnemonic, wordlist=wordlist)
        return True
    except Exception as e:
        return False


def mnemonic_to_seed(mnemonic: str, password: str = "", wordlist=WORDLIST):
    # first we try to convert mnemonic to bytes
    # and raise a correct error if it is invalid
    # If wordlist is None - don't check mnemonic.
    if wordlist is not None:
        mnemonic_to_bytes(mnemonic, wordlist=wordlist)
    return hashlib.pbkdf2_hmac(
        "sha512",
        mnemonic.encode("utf-8"),
        ("mnemonic" + password).encode("utf-8"),
        PBKDF2_ROUNDS,
        64,
    )


def _extract_index(bits, b, n):
    value = 0
    for pos in range(n * bits, (n + 1) * bits):
        value = value << 1
        if b[pos // 8] & (1 << (7 - pos % 8)):
            value += 1
    return value


def mnemonic_from_bytes(entropy, wordlist=WORDLIST):
    if len(entropy) % 4 != 0:
        raise ValueError("Byte array should be multiple of 4 long (16, 20, ..., 32)")
    total_bits = len(entropy) * 8
    checksum_bits = total_bits // 32
    total_mnemonics = (total_bits + checksum_bits) // 11
    # no need to truncate checksum - we already know total_mnemonics
    checksum = bytearray(hashlib.sha256(entropy).digest())
    entropy += checksum
    mnemonic = []
    for i in range(0, total_mnemonics):
        idx = _extract_index(11, entropy, i)
        mnemonic.append(wordlist[idx])
    return " ".join(mnemonic)


def find_candidates(word_part, nmax=5, wordlist=WORDLIST):
    candidates = []
    for w in wordlist:
        if w.startswith(word_part):
            candidates.append(w)
        if len(candidates) >= nmax:
            break
    return candidates
