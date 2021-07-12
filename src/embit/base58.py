# Partially copy-pasted from python-bitcoinlib:
# https://github.com/petertodd/python-bitcoinlib/blob/master/bitcoin/base58.py

"""Base58 encoding and decoding"""

import binascii
from . import hashes

B58_DIGITS = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def encode(b):
    """Encode bytes to a base58-encoded string"""

    # Convert big-endian bytes to integer
    n = int("0x0" + binascii.hexlify(b).decode("utf8"), 16)

    # Divide that integer into bas58
    res = []
    while n > 0:
        n, r = divmod(n, 58)
        res.append(B58_DIGITS[r])
    res = "".join(res[::-1])

    pad = 0
    for c in b:
        if c == 0:
            pad += 1
        else:
            break
    return B58_DIGITS[0] * pad + res


def decode(s):
    """Decode a base58-encoding string, returning bytes"""
    if not s:
        return b""

    # Convert the string to an integer
    n = 0
    for c in s:
        n *= 58
        if c not in B58_DIGITS:
            raise ValueError("Character %r is not a valid base58 character" % c)
        digit = B58_DIGITS.index(c)
        n += digit

    # Convert the integer to bytes
    h = "%x" % n
    if len(h) % 2:
        h = "0" + h
    res = binascii.unhexlify(h.encode("utf8"))

    # Add padding back.
    pad = 0
    for c in s[:-1]:
        if c == B58_DIGITS[0]:
            pad += 1
        else:
            break
    return b"\x00" * pad + res


def encode_check(b):
    """Encode bytes to a base58-encoded string with a checksum"""
    return encode(b + hashes.double_sha256(b)[0:4])


def decode_check(s):
    """Decode a base58-encoding string with checksum check.
    Returns bytes without checksum
    """
    b = decode(s)
    checksum = hashes.double_sha256(b[:-4])[:4]
    if b[-4:] != checksum:
        raise ValueError(
            "Checksum mismatch: expected %r, calculated %r" % (b[-4:], checksum)
        )
    return b[:-4]
