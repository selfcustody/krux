# The MIT License (MIT)

# Copyright (c) 2021-2025 Krux contributors

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

import ucryptolib
import uhashlib_hw

# KEF: AES, MODEs VERSIONS, MODE_NUMBERS, and MODE_IVS are defined here
#  to disable a MODE: set its value to None
#  to disable a VERSION: set its value to None
AES = ucryptolib.aes
MODE_ECB = ucryptolib.MODE_ECB
MODE_CBC = ucryptolib.MODE_CBC
MODE_CTR = ucryptolib.MODE_CTR
MODE_GCM = ucryptolib.MODE_GCM
VERSIONS = {
    # initial versions: released 2023.08 to encrypt bip39 entropy bytes
    0: {
        "name": "AES-ECB v1",
        "mode": MODE_ECB,
        "auth": -16,
    },
    1: {
        "name": "AES-CBC v1",
        "mode": MODE_CBC,
        "auth": -16,
    },
    # AES in ECB mode
    5: {
        # smallest ECB ciphertext, w/ unsafe padding: for high entropy mnemonics, passphrases, etc
        "name": "AES-ECB",
        "mode": MODE_ECB,
        "auth": 3,
    },
    6: {
        # safe padding: for mid-sized plaintext w/o duplicate blocks
        "name": "AES-ECB +p",
        "mode": MODE_ECB,
        "pkcs_pad": True,
        "auth": -4,
    },
    7: {
        # compressed, w/ safe padding: for larger plaintext; may compact otherwise duplicate blocks
        "name": "AES-ECB +c",
        "mode": MODE_ECB,
        "pkcs_pad": True,
        "auth": -4,
        "compress": True,
    },
    # AES in CBC mode
    10: {
        # smallest CBC cipherext, w/ unsafe padding: for mnemonics, passphrases, etc
        "name": "AES-CBC",
        "mode": MODE_CBC,
        "auth": 4,
    },
    11: {
        # safe padding: for mid-sized plaintext
        "name": "AES-CBC +p",
        "mode": MODE_CBC,
        "pkcs_pad": True,
        "auth": -4,
    },
    12: {
        # compressed, w/ safe padding: for larger plaintext
        "name": "AES-CBC +c",
        "mode": MODE_CBC,
        "pkcs_pad": True,
        "auth": -4,
        "compress": True,
    },
    # AES in CTR stream mode
    15: {
        # doesn't require padding: for small and mid-sized plaintext
        "name": "AES-CTR",
        "mode": MODE_CTR,
        "pkcs_pad": None,
        "auth": -4,
    },
    16: {
        # compressed: for larger plaintext
        "name": "AES-CTR +c",
        "mode": MODE_CTR,
        "pkcs_pad": None,
        "auth": -4,
        "compress": True,
    },
    # AES in GCM stream mode
    20: {
        # doesn't require padding: for small and mid-sized plaintext
        "name": "AES-GCM",
        "mode": MODE_GCM,
        "pkcs_pad": None,
        "auth": 4,
    },
    21: {
        # compressed: for larger plaintext
        "name": "AES-GCM +c",
        "mode": MODE_GCM,
        "pkcs_pad": None,
        "auth": 4,
        "compress": True,
    },
}
MODE_NUMBERS = {
    "AES-ECB": MODE_ECB,
    "AES-CBC": MODE_CBC,
    "AES-CTR": MODE_CTR,
    "AES-GCM": MODE_GCM,
}
MODE_IVS = {
    MODE_CBC: 16,
    MODE_CTR: 12,
    MODE_GCM: 12,
}

AES_BLOCK_SIZE = 16


class Cipher:
    """More than just a helper for AES encrypt/decrypt. Enforces KEF VERSIONS rules"""

    def __init__(self, key, salt, iterations):
        key = key if isinstance(key, bytes) else key.encode()
        salt = salt if isinstance(salt, bytes) else salt.encode()
        self._key = uhashlib_hw.pbkdf2_hmac_sha256(key, salt, iterations)

    def encrypt(self, plain, version, iv=b"", fail_unsafe=True):
        """AES encrypt according to KEF rules defined by version, returns payload bytes"""
        mode = VERSIONS[version]["mode"]
        v_iv = MODE_IVS.get(mode, 0)
        v_pkcs_pad = VERSIONS[version].get("pkcs_pad", False)
        v_auth = VERSIONS[version].get("auth", 0)
        v_compress = VERSIONS[version].get("compress", False)
        auth = b""
        if iv is None:
            iv = b""

        if not isinstance(plain, bytes):
            raise TypeError("Plaintext is not bytes")

        # for versions that compress
        if v_compress:
            plain = _deflate(plain)

        # fail: post-encryption appended "auth" with unfaithful-padding breaks decryption
        if fail_unsafe and v_pkcs_pad is False and v_auth > 0 and plain[-1] == 0x00:
            raise ValueError("Cannot validate decryption for this plaintext")

        # for modes that don't have authentication, KEF uses 2 forms of sha256
        if v_auth != 0 and mode in (MODE_ECB, MODE_CBC, MODE_CTR):
            if v_auth > 0:
                # unencrypted (public) auth: hash the plaintext w/ self._key
                auth = uhashlib_hw.sha256(
                    bytes([version]) + iv + plain + self._key
                ).digest()[:v_auth]
            elif v_auth < 0:
                # encrypted auth: hash only the plaintext
                auth = uhashlib_hw.sha256(plain).digest()[:-v_auth]

                # fail: same case as above if auth bytes have NUL suffix
                if fail_unsafe and v_pkcs_pad is False and auth[-1] == 0x00:
                    raise ValueError("Cannot validate decryption for this plaintext")
                plain += auth
                auth = b""

        # some modes need to pad to AES 16-byte blocks
        if v_pkcs_pad is True or v_pkcs_pad is False:
            plain = _pad(plain, pkcs_pad=v_pkcs_pad)

        # fail to encrypt in modes where it is known unsafe
        if fail_unsafe and mode == MODE_ECB:
            unique_blocks = len(
                set((plain[x : x + 16] for x in range(0, len(plain), 16)))
            )
            if unique_blocks != len(plain) // 16:
                raise ValueError("Duplicate blocks in ECB mode")

        # setup the encryptor (checking for modes that need initialization-vector)
        if v_iv > 0:
            if not (isinstance(iv, bytes) and len(iv) == v_iv):
                raise ValueError("Wrong IV length")
        elif iv:
            raise ValueError("IV is not required")
        if iv:
            if mode == MODE_CTR:
                encryptor = AES(self._key, mode, nonce=iv)
            elif mode == MODE_GCM:
                encryptor = AES(self._key, mode, iv, mac_len=v_auth)
            else:
                encryptor = AES(self._key, mode, iv)
        else:
            encryptor = AES(self._key, mode)

        # encrypt the plaintext
        encrypted = encryptor.encrypt(plain)

        # for modes that do have inherent authentication, use it
        if mode == MODE_GCM:
            auth = encryptor.digest()[:v_auth]

        return iv + encrypted + auth

    def decrypt(self, payload, version):
        """AES Decrypt according to KEF rules defined by version, returns plaintext bytes"""
        mode = VERSIONS[version]["mode"]
        v_iv = MODE_IVS.get(mode, 0)
        v_pkcs_pad = VERSIONS[version].get("pkcs_pad", False)
        v_auth = VERSIONS[version].get("auth", 0)
        v_compress = VERSIONS[version].get("compress", False)

        # validate payload size early
        min_payload = 1 if mode in (MODE_CTR, MODE_GCM) else AES_BLOCK_SIZE
        min_payload += min(0, v_auth) + v_iv
        if len(payload) <= min_payload:
            raise ValueError("Invalid Payload")

        # setup decryptor (pulling initialization-vector from payload if necessary)
        if not v_iv:
            iv = b""
            decryptor = AES(self._key, mode)
        else:
            iv = payload[:v_iv]
            if mode == MODE_CTR:
                decryptor = AES(self._key, mode, nonce=iv)
            elif mode == MODE_GCM:
                decryptor = AES(self._key, mode, iv, mac_len=v_auth)
            else:
                decryptor = AES(self._key, mode, iv)
            payload = payload[v_iv:]

        # remove authentication from payload if suffixed to ciphertext
        auth = None
        if v_auth > 0:
            auth = payload[-v_auth:]
            payload = payload[:-v_auth]

        # decrypt the ciphertext
        decrypted = decryptor.decrypt(payload)

        # if authentication added (inherent or added by KEF for ECB/CBC)
        # then: unpad and validate via embeded authentication bytes
        # else: let caller deal with unpad and auth
        if v_auth != 0:
            try:
                decrypted = self._authenticate(
                    version, iv, decrypted, decryptor, auth, mode, v_auth, v_pkcs_pad
                )
            except:
                decrypted = None

        # for versions that compress
        if decrypted and v_compress:
            decrypted = _reinflate(decrypted)

        return decrypted

    def _authenticate(
        self, version, iv, decrypted, aes_object, auth, mode, v_auth, v_pkcs_pad
    ):
        if not (
            isinstance(version, int)
            and 0 <= version <= 255
            and isinstance(iv, bytes)
            and isinstance(decrypted, bytes)
            and (
                mode != MODE_GCM
                or (hasattr(aes_object, "verify") and callable(aes_object.verify))
            )
            and (isinstance(auth, bytes) or auth is None)
            and mode in MODE_NUMBERS.values()
            and (isinstance(v_auth, int) and -32 <= v_auth <= 32)
            and (v_pkcs_pad is True or v_pkcs_pad is False or v_pkcs_pad is None)
        ):
            raise ValueError("Invalid call to ._authenticate()")

        # some modes need to unpad
        len_pre_unpad = len(decrypted)
        if v_pkcs_pad in (False, True):
            decrypted = _unpad(decrypted, pkcs_pad=v_pkcs_pad)

        if v_auth < 0:
            # auth was added to plaintext
            auth = decrypted[v_auth:]
            decrypted = decrypted[:v_auth]

        # versions that have built-in authentication use their own
        if mode == MODE_GCM:
            try:
                aes_object.verify(auth)
                return decrypted
            except:
                return None

        # versions that don't have built-in authentication use 2 forms of sha256
        max_attempts = 1
        if v_pkcs_pad is False:
            # NUL padding is imperfect, still attempt to authenticate -- up to a limit...
            # ... lesser of num bytes unpadded and auth size+1, + 1
            max_attempts = min(len_pre_unpad - len(decrypted), abs(v_auth) + 1) + 1

        for _ in range(max_attempts):
            if v_auth > 0:
                # for unencrypted (public) auth > 0: hash the decrypted w/ self._key
                cksum = uhashlib_hw.sha256(
                    bytes([version]) + iv + decrypted + self._key
                ).digest()[:v_auth]
            else:
                # for encrypted auth < 0: hash only the decrypted
                cksum = uhashlib_hw.sha256(decrypted).digest()[:-v_auth]
            if cksum == auth:
                return decrypted

            if v_auth < 0:
                # for next attempt, assume auth had NUL stripped by unpad()
                decrypted += auth[:1]
                auth = auth[1:] + b"\x00"
            elif v_auth > 0:
                # for next attempt, assume plaintext had NUL stripped by unpad()
                decrypted += b"\x00"
        return None


def suggest_versions(plaintext, mode_name):
    """Suggests a krux encryption version based on plaintext and preferred mode"""

    small_thresh = 32  # if len(plaintext) <= small_thresh: it is small
    big_thresh = 120  # if len(plaintext) >= big_thresh: it is big

    # gather metrics on plaintext
    if not isinstance(plaintext, (bytes, str)):
        raise TypeError("Plaintext is not bytes or str")
    p_length = len(plaintext)
    unique_blocks = len(set((plaintext[x : x + 16] for x in range(0, p_length, 16))))
    p_duplicates = bool(unique_blocks < p_length / 16)
    if isinstance(plaintext, bytes):
        p_nul_suffix = bool(plaintext[-1] == 0x00)
    else:
        p_nul_suffix = bool(plaintext.encode()[-1] == 0x00)

    candidates = []
    for version, values in VERSIONS.items():
        # strategy: eliminate bad choices of versions
        # TODO: explore a strategy that cuts to the best one right away

        if values is None or values["mode"] is None:
            continue

        # never use a version that is not the correct mode
        if values["mode"] != MODE_NUMBERS[mode_name]:
            continue
        v_compress = values.get("compress", False)
        v_auth = values.get("auth", 0)
        v_pkcs_pad = values.get("pkcs_pad", False)

        # never use non-compressed ECB when plaintext has duplicate blocks
        if p_duplicates and mode_name == "AES-ECB" and not v_compress:
            continue

        # never use v1 versions since v2 is smaller
        if mode_name in ("AES-ECB", "AES-CBC") and v_auth == -16:
            continue

        # based on plaintext size
        if p_length <= small_thresh:
            # except unsafe ECB text...
            if mode_name == "AES-ECB" and p_duplicates:
                pass
            else:
                # ...never use pkcs when it's small and can keep it small
                if v_pkcs_pad is True and not p_nul_suffix:
                    continue
                # ...and never compress
                if v_compress:
                    continue
        else:
            # never use non-safe padding for not-small plaintext
            if v_pkcs_pad is False:
                continue

            # except unsafe ECB text...
            if mode_name == "AES-ECB" and p_duplicates:
                pass
            elif p_length < big_thresh:
                # ...never use compressed for not-big plaintext
                if v_compress:
                    continue
            else:
                # never use non-compressed for big plaintext
                if not v_compress:
                    continue

        # never use a version with unsafe padding if plaintext ends 0x00
        if p_nul_suffix and v_pkcs_pad is False:
            continue

        candidates.append(version)
    return candidates


def wrap(id_, version, iterations, payload):
    """
    Wraps inputs into KEF Encryption Format envelope, returns bytes
    """

    try:
        # when wrapping, be tolerant about id_ as bytes or str
        id_ = id_ if isinstance(id_, bytes) else id_.encode()
        if not 0 <= len(id_) <= 252:
            raise ValueError
        len_id = len(id_).to_bytes(1, "big")
    except:
        raise ValueError("Invalid ID")

    try:
        if not (
            0 <= version <= 255
            and VERSIONS[version] is not None
            and VERSIONS[version]["mode"] is not None
        ):
            raise ValueError
    except:
        raise ValueError("Invalid version")

    try:
        if not isinstance(iterations, int):
            raise ValueError
        if iterations % 10000 == 0:
            iterations = iterations // 10000
            if not 1 <= iterations <= 10000:
                raise ValueError
        else:
            if not 10000 < iterations < 2**24:
                raise ValueError
        iterations = iterations.to_bytes(3, "big")
    except:
        raise ValueError("Invalid iterations")

    extra = MODE_IVS.get(VERSIONS[version]["mode"], 0)
    if VERSIONS[version].get("auth", 0) > 0:
        extra += VERSIONS[version]["auth"]
    if not isinstance(payload, bytes):
        raise ValueError("Payload is not bytes")
    if VERSIONS[version].get("pkcs_pad", False) in (True, False):
        if (len(payload) - extra) % 16 != 0:
            raise ValueError("Ciphertext is not aligned")
        if (len(payload) - extra) // 16 < 1:
            raise ValueError("Ciphertext is too short")

    version = version.to_bytes(1, "big")
    return b"".join([len_id, id_, version, iterations, payload])


def unwrap(kef_bytes):
    """
    Unwraps KEF Encryption Format bytes, returns tuple of parsed values
    """
    len_id = kef_bytes[0]

    try:
        # out-of-order reading to validate version early
        version = kef_bytes[1 + len_id]
        if VERSIONS[version] is None or VERSIONS[version]["mode"] is None:
            raise ValueError
    except:
        raise ValueError("Invalid format")

    # When unwrapping, be strict returning id_ as bytes
    id_ = kef_bytes[1 : 1 + len_id]

    kef_iterations = int.from_bytes(kef_bytes[2 + len_id : 5 + len_id], "big")
    if kef_iterations <= 10000:
        iterations = kef_iterations * 10000
    else:
        iterations = kef_iterations

    payload = kef_bytes[len_id + 5 :]
    extra = MODE_IVS.get(VERSIONS[version]["mode"], 0)
    if VERSIONS[version].get("auth", 0) > 0:
        extra += VERSIONS[version]["auth"]
    if VERSIONS[version].get("pkcs_pad", False) in (True, False):
        if (len(payload) - extra) % 16 != 0:
            raise ValueError("Ciphertext is not aligned")
        if (len(payload) - extra) // 16 < 1:
            raise ValueError("Ciphertext is too short")

    return (id_, version, iterations, payload)


def _pad(some_bytes, pkcs_pad):
    """
    Pads some_bytes to AES block size of 16 bytes, returns bytes
    pkcs_pad: False=NUL-pad, True=PKCS#7-pad, None=no-pad
    """
    if pkcs_pad is None:
        return some_bytes
    len_padding = (AES_BLOCK_SIZE - len(some_bytes) % AES_BLOCK_SIZE) % AES_BLOCK_SIZE
    if pkcs_pad is True:
        if len_padding == 0:
            len_padding = AES_BLOCK_SIZE
        return some_bytes + (len_padding).to_bytes(1, "big") * len_padding
    if pkcs_pad is False:
        return some_bytes + b"\x00" * len_padding
    raise TypeError("pkcs_pad is not (None, True, False)")


def _unpad(some_bytes, pkcs_pad):
    """
    Strips padding from some_bytes, returns bytes
    pkcs_pad: False=NUL-pad, True=PKCS#7-pad, None=no-pad
    """
    if pkcs_pad is None:
        return some_bytes
    if pkcs_pad is True:
        len_padding = some_bytes[-1]
        return some_bytes[:-len_padding]
    if pkcs_pad is False:
        return some_bytes.rstrip(b"\x00")
    raise TypeError("pkcs_pad is not in (None, True, False)")


def _deflate(data):
    """Compresses the given data using deflate module"""
    import io
    import deflate

    try:
        stream = io.BytesIO()
        with deflate.DeflateIO(stream) as d:
            d.write(data)
        return stream.getvalue()
    except:
        raise ValueError("Error compressing")


def _reinflate(data):
    """Decompresses the given data using deflate module"""
    import io
    import deflate

    try:
        with deflate.DeflateIO(io.BytesIO(data)) as d:
            return d.read()
    except:
        raise ValueError("Error decompressing")
