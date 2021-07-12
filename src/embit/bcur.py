try:
    import uio as io
except ImportError:
    import io
import hashlib

CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
BCHARSET_LOWER = list(CHARSET.encode())
BCHARSET_UPPER = list(CHARSET.upper().encode())
GENERATOR = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]

def bech32_polymod_update(value, chk=1):
    """Internal function that computes the Bech32 checksum."""
    top = chk >> 25
    chk = (chk & 0x1FFFFFF) << 5 ^ value
    for i in range(5):
        chk ^= GENERATOR[i] if ((top >> i) & 1) else 0
    return chk


def convertbits_chunk(bufin, lin, frombits, bufout, tobits, pad=True):
    """General power-of-2 base conversion."""
    acc = 0
    bits = 0
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    idx = 0
    for i in range(lin):
        value = bufin[i]
        if value < 0 or (value >> frombits):
            return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            bufout[idx] = ((acc >> bits) & maxv)
            idx += 1
    if pad:
        if bits:
            bufout[idx] = ((acc << (tobits - bits)) & maxv)
            idx += 1
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return idx


def bcur_decode_stream(sin, sout, checksum=None, cbor=True, size=None):
    """
    Stream-decoder of bcur data, reads from sin, writes to sout.
    """
    # bech32 chars
    barr = bytearray(8)
    # indexes
    idxarr = bytearray(8)
    # raw bytes
    outarr = bytearray(5)
    # hash-based bcur checksum
    if checksum:
        h = hashlib.sha256()
    # polymod checksum
    polymod = bech32_polymod_update(0)
    l = 0
    ltot = 0
    cbor_len = None
    if not cbor:
        if not size:
            start = sin.tell()
            # move to the end of the file
            sin.seek(0, 2)
            end = sin.tell()
            # rewind back where we were
            sin.seek(start, 0)
            if end-start <= 0:
                raise ValueError("Invalid length")
            size = (end-start-6)*5//8
        cbor_len = size

    while True:
        l = sin.readinto(barr)
        for i in range(l):
            if barr[i] in BCHARSET_LOWER:
                idxarr[i] = BCHARSET_LOWER.index(barr[i])
            elif barr[i] in BCHARSET_UPPER:
                idxarr[i] = BCHARSET_UPPER.index(barr[i])
            else:
                # \r or \n
                if barr[i] not in [10, 13]:
                    raise ValueError("Invalid character %d" % barr[i])
                l = i
                break
            polymod = bech32_polymod_update(idxarr[i], polymod)
        if l == 0:
            break
        lout = convertbits_chunk(idxarr, l, 5, outarr, 8)
        if lout is None:
            raise ValueError("Failed to convert")
        # if cbor_len is not defined yet, read it from the chunk we just decoded
        if cbor_len is None:
            # update hash
            if checksum:
                h.update(outarr)
            # decode len
            b = outarr[0]
            if b >= 0x40 and b < 0x58:
                cbor_len = b - 0x40
                sout.write(outarr[1:], lout-1)
                ltot += lout-1
            elif b == 0x58:
                cbor_len = outarr[1]
                sout.write(outarr[2:], lout-2)
                ltot += lout-2
            elif b == 0x59:
                cbor_len = int.from_bytes(outarr[1:3], "big")
                sout.write(outarr[3:], lout-3)
                ltot += lout-3
            elif b == 0x60:
                cbor_len = int.from_bytes(outarr[1:5], "big")
            else:
                raise ValueError("Invalid CBOR encoding")
        else:
            if cbor_len < ltot+lout:
                sout.write(outarr, cbor_len-ltot)
                if checksum:
                    h.update(outarr[:cbor_len-ltot])
                break
            else:
                sout.write(outarr, lout)
                ltot += lout
                # update hash
                if checksum:
                    if lout == len(outarr):
                        h.update(outarr)
                    else:
                        h.update(outarr[:lout])
        if l < 8:
            break
    # polymod check
    l = sin.readinto(barr, 6)
    for i in range(l):
        if barr[i] in BCHARSET_LOWER:
            idxarr[i] = BCHARSET_LOWER.index(barr[i])
        elif barr[i] in BCHARSET_UPPER:
            idxarr[i] = BCHARSET_UPPER.index(barr[i])
        else:
            # \r or \n
            if barr[i] not in [10, 13]:
                raise ValueError("Invalid character %d" % barr[i])
            l = i
            break
        polymod = bech32_polymod_update(idxarr[i], polymod)
    if polymod != 0x3FFFFFFF:
        raise ValueError("Invalid bech32 checksum")
    if checksum:
        # hash is small, so we can decode without streams
        hsh = bcur_decode(checksum, cbor=False)
        hsh2 = h.digest()
        if hsh != hsh2:
            raise ValueError("Checksum mismatch")
    return cbor_len

def bcur_decode(data, checksum=None, cbor=True, size=None):
    """Returns decoded data, verifies hash if provided"""
    sin = io.BytesIO(data)
    sout = io.BytesIO()
    if size is None:
        size = None if cbor else (len(data)-6)*5//8
    bcur_decode_stream(sin, sout, checksum, cbor=cbor, size=size)
    return sout.getvalue()


def bcur_encode_stream(sin, sout, upper=True, cbor=True, checksum=True, size=None):
    """
    Stream-encoder of bcur data, reads from sin, writes to sout.
    Writes and reads in binary.
    Returns number of bytes written to sout and hash checksum.
    """
    BCHARSET = BCHARSET_UPPER if upper else BCHARSET_LOWER
    if not size:
        start = sin.tell()
        # move to the end of the file
        sin.seek(0, 2)
        end = sin.tell()
        # rewind back where we were
        sin.seek(start, 0)
        size = end-start

    # indexes
    idxarr = bytearray(8)
    # bech32 chars
    barr = bytearray(8)
    # bech32 checksum
    polymod = bech32_polymod_update(0)
    # hash checksum
    if checksum:
        h = hashlib.sha256()

    res = 0
    # first chunk with cbor length
    if not cbor:
        prefix = b""
    elif size <= 23:
        prefix = bytes([0x40 + size])
    elif size <= 255:
        prefix = bytes([0x58, size])
    elif size <= 65535:
        prefix = b"\x59" + size.to_bytes(2, "big")
    else:
        prefix = b"\x60" + size.to_bytes(4, "big")
    if len(prefix) < 5:
        prefix += sin.read(5-len(prefix))
    # raw bytes
    inarr = bytearray(prefix)
    lin = len(prefix)
    while lin > 0:
        if checksum:
            if lin == len(inarr):
                h.update(inarr)
            else:
                h.update(inarr[:lin])
        lout = convertbits_chunk(inarr, lin, 8, idxarr, 5)
        for i in range(lout):
            barr[i] = BCHARSET[idxarr[i]]
            polymod = bech32_polymod_update(idxarr[i], polymod)
        if sout is not None:
            sout.write(barr, lout)
        res += lout
        lin = sin.readinto(inarr)

    for i in range(6):
        polymod = bech32_polymod_update(0, polymod)
    polymod = polymod ^ 0x3FFFFFFF
    chk = [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]
    if sout is not None:
        sout.write(bytes([BCHARSET[c] for c in chk]))
    res += len(chk)
    if checksum:
        hsh = h.digest()
        enc_hash, _ = bcur_encode(hsh, upper=upper, cbor=False, checksum=False)
        return res, enc_hash
    else:
        return res, None


def bcur_encode(data, upper=True, cbor=True, checksum=True):
    """Returns a tuple - encoded data and encoded hash checksum"""
    sin = io.BytesIO(data)
    sout = io.BytesIO()
    size, hsh = bcur_encode_stream(sin, sout, upper=upper, cbor=cbor, checksum=checksum, size=len(data))
    return sout.getvalue(), hsh
