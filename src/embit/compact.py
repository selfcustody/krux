""" Compact Int parsing / serialization """
try:
    import uio as io
except ImportError:
    import io

def to_bytes(i: int):
    """encodes an integer as a compact int"""
    if i < 0:
        raise ValueError("integer can't be negative: {}".format(i))
    order = 0
    while i >> (8 * (2 ** order)):
        order += 1
    if order == 0:
        if i < 0xFD:
            return bytes([i])
        order = 1
    if order > 3:
        raise ValueError("integer too large: {}".format(i))
    return bytes([0xFC + order]) + i.to_bytes(2 ** order, "little")


def from_bytes(b: bytes):
    s = io.io.BytesIO(b)
    res = read_from(s)
    if len(s.read(1)) > 0:
        raise ValueError("Too many bytes")
    return res


def read_from(stream):
    """reads a compact integer from a stream"""
    i = stream.read(1)[0]
    if i >= 0xFD:
        bytes_to_read = 2 ** (i - 0xFC)
        return int.from_bytes(stream.read(bytes_to_read), "little")
    else:
        return i
