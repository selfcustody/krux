"""
This is a fallback option if the library can't do ctypes bindings to secp256k1 library.
Mimics the micropython bindings and internal representation of data structs in secp256k1.
"""

from . import key as _key

# Flags to pass to context_create.
CONTEXT_VERIFY = 0b0100000001
CONTEXT_SIGN = 0b1000000001
CONTEXT_NONE = 0b0000000001

# Flags to pass to ec_pubkey_serialize
EC_COMPRESSED = 0b0100000010
EC_UNCOMPRESSED = 0b0000000010


def context_randomize(seed, context=None):
    pass


def _reverse64(b):
    """Converts (a,b) from big to little endian to be consistent with secp256k1"""
    x = b[:32]
    y = b[32:]
    return x[::-1] + y[::-1]


def _pubkey_serialize(pub):
    """Returns pubkey representation like secp library"""
    b = pub.get_bytes()[1:]
    return _reverse64(b)


def _pubkey_parse(b):
    """Returns pubkey class instance"""
    pub = _key.ECPubKey()
    pub.set(b"\x04" + _reverse64(b))
    return pub


def ec_pubkey_create(secret, context=None):
    if len(secret) != 32:
        raise ValueError("Private key should be 32 bytes long")
    pk = _key.ECKey()
    pk.set(secret, compressed=False)
    if not pk.is_valid:
        raise ValueError("Invalid private key")
    return _pubkey_serialize(pk.get_pubkey())


def ec_pubkey_parse(sec, context=None):
    if len(sec) != 33 and len(sec) != 65:
        raise ValueError("Serialized pubkey should be 33 or 65 bytes long")
    if len(sec) == 33:
        if sec[0] != 0x02 and sec[0] != 0x03:
            raise ValueError("Compressed pubkey should start with 0x02 or 0x03")
    else:
        if sec[0] != 0x04:
            raise ValueError("Uncompressed pubkey should start with 0x04")
    pub = _key.ECPubKey()
    pub.set(sec)
    pub.compressed = False
    if not pub.is_valid:
        raise ValueError("Failed parsing public key")
    return _pubkey_serialize(pub)


def ec_pubkey_serialize(pubkey, flag=EC_COMPRESSED, context=None):
    if len(pubkey) != 64:
        raise ValueError("Pubkey should be 64 bytes long")
    if flag not in [EC_COMPRESSED, EC_UNCOMPRESSED]:
        raise ValueError("Invalid flag")
    pub = _pubkey_parse(pubkey)
    if not pub.is_valid:
        raise ValueError("Failed to serialize pubkey")
    if flag == EC_COMPRESSED:
        pub.compressed = True
    return pub.get_bytes()


def ecdsa_signature_parse_compact(compact_sig, context=None):
    if len(compact_sig) != 64:
        raise ValueError("Compact signature should be 64 bytes long")
    sig = _reverse64(compact_sig)
    return sig


def ecdsa_signature_parse_der(der, context=None):
    if der[1] + 2 != len(der):
        raise ValueError("Failed parsing compact signature")
    if len(der) < 4:
        raise ValueError("Failed parsing compact signature")
    if der[0] != 0x30:
        raise ValueError("Failed parsing compact signature")
    if der[2] != 0x02:
        raise ValueError("Failed parsing compact signature")
    rlen = der[3]
    if len(der) < 6 + rlen:
        raise ValueError("Failed parsing compact signature")
    if rlen < 1 or rlen > 33:
        raise ValueError("Failed parsing compact signature")
    if der[4] >= 0x80:
        raise ValueError("Failed parsing compact signature")
    if rlen > 1 and (der[4] == 0) and not (der[5] & 0x80):
        raise ValueError("Failed parsing compact signature")
    r = int.from_bytes(der[4 : 4 + rlen], "big")
    if der[4 + rlen] != 0x02:
        raise ValueError("Failed parsing compact signature")
    slen = der[5 + rlen]
    if slen < 1 or slen > 33:
        raise ValueError("Failed parsing compact signature")
    if len(der) != 6 + rlen + slen:
        raise ValueError("Failed parsing compact signature")
    if der[6 + rlen] >= 0x80:
        raise ValueError("Failed parsing compact signature")
    if slen > 1 and (der[6 + rlen] == 0) and not (der[7 + rlen] & 0x80):
        raise ValueError("Failed parsing compact signature")
    s = int.from_bytes(der[6 + rlen : 6 + rlen + slen], "big")

    # Verify that r and s are within the group order
    if r < 1 or s < 1 or r >= _key.SECP256K1_ORDER or s >= _key.SECP256K1_ORDER:
        raise ValueError("Failed parsing compact signature")
    if s >= _key.SECP256K1_ORDER_HALF:
        raise ValueError("Failed parsing compact signature")

    return r.to_bytes(32, "little") + s.to_bytes(32, "little")


def ecdsa_signature_serialize_der(sig, context=None):
    if len(sig) != 64:
        raise ValueError("Signature should be 64 bytes long")
    r = int.from_bytes(sig[:32], "little")
    s = int.from_bytes(sig[32:], "little")
    rb = r.to_bytes((r.bit_length() + 8) // 8, "big")
    sb = s.to_bytes((s.bit_length() + 8) // 8, "big")
    return (
        b"\x30"
        + bytes([4 + len(rb) + len(sb), 2, len(rb)])
        + rb
        + bytes([2, len(sb)])
        + sb
    )


def ecdsa_signature_serialize_compact(sig, context=None):
    if len(sig) != 64:
        raise ValueError("Signature should be 64 bytes long")
    return _reverse64(sig)


def ecdsa_signature_normalize(sig, context=None):
    if len(sig) != 64:
        raise ValueError("Signature should be 64 bytes long")
    r = int.from_bytes(sig[:32], "little")
    s = int.from_bytes(sig[32:], "little")
    if s >= _key.SECP256K1_ORDER_HALF:
        s = _key.SECP256K1_ORDER - s
    return r.to_bytes(32, "little") + s.to_bytes(32, "little")


def ecdsa_verify(sig, msg, pub, context=None):
    if len(sig) != 64:
        raise ValueError("Signature should be 64 bytes long")
    if len(msg) != 32:
        raise ValueError("Message should be 32 bytes long")
    if len(pub) != 64:
        raise ValueError("Public key should be 64 bytes long")
    pubkey = _pubkey_parse(pub)
    return pubkey.verify_ecdsa(ecdsa_signature_serialize_der(sig), msg)


def ecdsa_sign(msg, secret, context=None):
    if len(msg) != 32:
        raise ValueError("Message should be 32 bytes long")
    if len(secret) != 32:
        raise ValueError("Secret key should be 32 bytes long")
    pk = _key.ECKey()
    pk.set(secret, False)
    sig = pk.sign_ecdsa(msg)
    return ecdsa_signature_parse_der(sig)


def ec_seckey_verify(secret, context=None):
    if len(secret) != 32:
        raise ValueError("Secret should be 32 bytes long")
    pk = _key.ECKey()
    pk.set(secret, compressed=False)
    return pk.is_valid


def ec_privkey_negate(secret, context=None):
    # negate in place
    if len(secret) != 32:
        raise ValueError("Secret should be 32 bytes long")
    s = int.from_bytes(secret, "big")
    s2 = _key.SECP256K1_ORDER - s
    s2arr = s2.to_bytes(32, "big")
    for i in range(len(secret)):
        secret[i] = s2arr[i]


def ec_pubkey_negate(pubkey, context=None):
    if len(pubkey) != 64:
        raise ValueError("Pubkey should be a 64-byte structure")
    r = _secp.secp256k1_ec_pubkey_negate(context, pubkey)
    if r == 0:
        raise ValueError("Failed to negate pubkey")


def ec_privkey_tweak_add(secret, tweak, context=None):
    res = ec_privkey_add(secret, tweak)
    for i in range(len(secret)):
        secret[i] = res[i]


def ec_pubkey_tweak_add(pub, tweak, context=None):
    res = ec_pubkey_add(pub, tweak)
    for i in range(len(pub)):
        pub[i] = res[i]


def ec_privkey_add(secret, tweak, context=None):
    if len(secret) != 32 or len(tweak) != 32:
        raise ValueError("Secret and tweak should both be 32 bytes long")
    s = int.from_bytes(secret, "big")
    t = int.from_bytes(tweak, "big")
    r = (s + t) % _key.SECP256K1_ORDER
    return r.to_bytes(32, "big")


def ec_pubkey_add(pub, tweak, context=None):
    if len(pub) != 64:
        raise ValueError("Public key should be 64 bytes long")
    if len(tweak) != 32:
        raise ValueError("Tweak should be 32 bytes long")
    pubkey = _pubkey_parse(pub)
    pubkey.compressed = True
    t = int.from_bytes(tweak, "big")
    Q = _key.SECP256K1.affine(
        _key.SECP256K1.mul([(_key.SECP256K1_G, t), (pubkey.p, 1)])
    )
    if Q is None:
        return None
    return Q[0].to_bytes(32, "little") + Q[1].to_bytes(32, "little")


# def ec_privkey_tweak_mul(secret, tweak, context=None):
#     if len(secret)!=32 or len(tweak)!=32:
#         raise ValueError("Secret and tweak should both be 32 bytes long")
#     s = int.from_bytes(secret, 'big')
#     t = int.from_bytes(tweak, 'big')
#     if t > _key.SECP256K1_ORDER or s > _key.SECP256K1_ORDER:
#         raise ValueError("Failed to tweak the secret")
#     r = pow(s, t, _key.SECP256K1_ORDER)
#     res = r.to_bytes(32, 'big')
#     for i in range(len(secret)):
#         secret[i] = res[i]

# def ec_pubkey_tweak_mul(pub, tweak, context=None):
#     if len(pub)!=64:
#         raise ValueError("Public key should be 64 bytes long")
#     if len(tweak)!=32:
#         raise ValueError("Tweak should be 32 bytes long")
#     if _secp.secp256k1_ec_pubkey_tweak_mul(context, pub, tweak) == 0:
#         raise ValueError("Failed to tweak the public key")

# def ec_pubkey_combine(*args, context=None):
#     pub = bytes(64)
#     pubkeys = (c_char_p * len(args))(*args)
#     r = _secp.secp256k1_ec_pubkey_combine(context, pub, pubkeys, len(args))
#     if r == 0:
#         raise ValueError("Failed to negate pubkey")
#     return pub


def ecdsa_sign_recoverable(msg, secret, context=None):
    sig = ecdsa_sign(msg, secret)
    pub = ec_pubkey_create(secret)
    # Search for correct index. Not efficient but I am lazy.
    # For efficiency use c-bindings to libsecp256k1
    for i in range(4):
        if ecdsa_recover(sig + bytes([i]), msg) == pub:
            return sig + bytes([i])
    raise ValueError("Failed to sign")


def ecdsa_recoverable_signature_serialize_compact(sig, context=None):
    if len(sig) != 65:
        raise ValueError("Recoverable signature should be 65 bytes long")
    compact = ecdsa_signature_serialize_compact(sig[:64])
    return compact, sig[64]


def ecdsa_recoverable_signature_parse_compact(compact_sig, recid, context=None):
    if len(compact_sig) != 64:
        raise ValueError("Signature should be 64 bytes long")
    # TODO: also check r value so recid > 2 makes sense
    if recid < 0 or recid > 4:
        raise ValueError("Failed parsing compact signature")
    return ecdsa_signature_parse_compact(compact_sig) + bytes([recid])


def ecdsa_recoverable_signature_convert(sigin, context=None):
    if len(sigin) != 65:
        raise ValueError("Recoverable signature should be 65 bytes long")
    return sigin[:64]


def ecdsa_recover(sig, msghash, context=None):
    if len(sig) != 65:
        raise ValueError("Recoverable signature should be 65 bytes long")
    if len(msghash) != 32:
        raise ValueError("Message should be 32 bytes long")
    idx = sig[-1]
    r = int.from_bytes(sig[:32], "little")
    s = int.from_bytes(sig[32:64], "little")
    z = int.from_bytes(msghash, "big")
    # r = Rx mod N, so R can be 02x, 03x, 02(N+x), 03(N+x)
    # two latter cases only if N+x < P
    r_candidates = [
        b"\x02" + r.to_bytes(32, "big"),
        b"\x03" + r.to_bytes(32, "big"),
    ]
    if r + _key.SECP256K1_ORDER < _key.SECP256K1_FIELD_SIZE:
        r2 = r + _key.SECP256K1_ORDER
        r_candidates = r_candidates + [
            b"\x02" + r2.to_bytes(32, "big"),
            b"\x03" + r2.to_bytes(32, "big"),
        ]
    if idx >= len(r_candidates):
        raise ValueError("Failed to recover public key")
    R = _key.ECPubKey()
    R.set(r_candidates[idx])
    # s = (z + d * r)/k
    # (R*s/r - z/r*G) = P
    rinv = _key.modinv(r, _key.SECP256K1_ORDER)
    u1 = (s * rinv) % _key.SECP256K1_ORDER
    u2 = (z * rinv) % _key.SECP256K1_ORDER
    P1 = _key.SECP256K1.mul([(R.p, u1)])
    P2 = _key.SECP256K1.negate(_key.SECP256K1.mul([(_key.SECP256K1_G, u2)]))
    P = _key.SECP256K1.affine(_key.SECP256K1.add(P1, P2))
    result = P[0].to_bytes(32, "little") + P[1].to_bytes(32, "little")
    # verify signature at the end
    pubkey = _pubkey_parse(result)
    if not pubkey.is_valid:
        raise ValueError("Failed to recover public key")
    if not ecdsa_verify(sig[:64], msghash, result):
        raise ValueError("Failed to recover public key")
    return result
