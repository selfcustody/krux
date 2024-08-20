# Mnemonic convertion to seed and to/from bytes
# pylint: disable=W0102

import hashlib
from embit.wordlists.bip39 import WORDLIST

WORDINDEX = {word: i for i, word in enumerate(WORDLIST)}


def mnemonic_to_bytes(mnemonic: str, ignore_checksum: bool = False, wordlist=WORDLIST):
    """Verifies the mnemonic checksum and returns it in bytes"""
    words = mnemonic.strip().split()
    if len(words) % 3 != 0 or not 12 <= len(words) <= 24:
        raise ValueError("Invalid recovery phrase")

    accumulator = 0
    try:
        if wordlist is WORDLIST:
            for word in words:
                accumulator = (accumulator << 11) + WORDINDEX[word]
        else:
            for word in words:
                accumulator = (accumulator << 11) + wordlist.index(word)
    except Exception:
        raise ValueError("Word '%s' is not in the dictionary" % word)

    entropy_length_bits = len(words) * 11 // 33 * 32
    checksum_length_bits = len(words) * 11 // 33
    checksum = accumulator & (2**checksum_length_bits - 1)
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
    except:
        return False
