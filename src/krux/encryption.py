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

try:
    import ujson as json
except ImportError:
    import json
import hashlib
import ucryptolib
from .bbqr import deflate_compress, deflate_decompress
from .baseconv import base_encode, base_decode
from .sd_card import SDHandler
from .krux_settings import Settings
from embit import bip39


MNEMONICS_FILE = "seeds.json"
FLASH_PATH = "/flash/"

# encryption versions are defined here
VERSIONS = {
    0: {
        "name": "AES-ECB",
        "mode": ucryptolib.MODE_ECB,
        "auth": -16,
    },
    1: {
        "name": "AES-CBC",
        "mode": ucryptolib.MODE_CBC,
        "auth": -16,
    },
    2: {
        "name": "AES-GCM",
        "mode": ucryptolib.MODE_GCM,
        "pkcs_pad": None,
        "auth": 4,
    },
    3: {
        "name": "AES-ECB v2",
        "mode": ucryptolib.MODE_ECB,
        "auth": 3,
    },
    4: {
        "name": "AES-CBC v2",
        "mode": ucryptolib.MODE_CBC,
        "auth": 4,
    },
    5: {
        "name": "AES-ECB +p",
        "mode": ucryptolib.MODE_ECB,
        "pkcs_pad": True,
        "auth": -4,
    },
    6: {
        "name": "AES-CBC +p",
        "mode": ucryptolib.MODE_CBC,
        "pkcs_pad": True,
        "auth": -4,
    },
    7: {
        "name": "AES-GCM +c",
        "mode": ucryptolib.MODE_GCM,
        "pkcs_pad": None,
        "auth": 4,
        "compress": True,
    },
    8: {
        "name": "AES-ECB +c",
        "mode": ucryptolib.MODE_ECB,
        "pkcs_pad": True,
        "auth": -4,
        "compress": True,
    },
    9: {
        "name": "AES-CBC +c",
        "mode": ucryptolib.MODE_CBC,
        "pkcs_pad": True,
        "auth": -4,
        "compress": True,
    },
}
MODE_NUMBERS = {
    "AES-ECB": ucryptolib.MODE_ECB,
    "AES-CBC": ucryptolib.MODE_CBC,
    "AES-GCM": ucryptolib.MODE_GCM,
}
MODE_IVS = {
    ucryptolib.MODE_CBC: 16,
    ucryptolib.MODE_GCM: 12,
}

AES_BLOCK_SIZE = 16
QR_CODE_ITER_MULTIPLE = 10000


class AESCipher:
    """More than just a helper for AES encrypt/decrypt. Enforces VERSIONS rules"""

    def __init__(self, key, salt, iterations):
        # latin-1 encoding enables all byte values for key and salt (KEF's id_)
        self.key = hashlib.pbkdf2_hmac(
            "sha256", key.encode("latin-1"), salt.encode("latin-1"), iterations
        )

    def encrypt(self, plain, version, iv=b"", fail_unsafe=True):
        """AES encrypt according to krux rules defined by version, returns payload bytes"""
        mode = VERSIONS[version]["mode"]
        v_iv = MODE_IVS.get(mode, 0)
        v_pkcs_pad = VERSIONS[version].get("pkcs_pad", False)
        v_auth = VERSIONS[version].get("auth", 0)
        v_compress = VERSIONS[version].get("compress", False)
        auth = b""

        if not isinstance(plain, bytes):
            raise TypeError("Plaintext is not bytes")

        # for versions that compress
        if v_compress:
            plain = deflate_compress(plain)

        # fail: post-encryption appended "auth" with unfaithful-padding breaks decryption
        if fail_unsafe and v_pkcs_pad is False and v_auth > 0 and plain[-1] == 0x00:
            raise ValueError("Cannot validate decryption for this plaintext")

        # for modes that don't have authentication, krux uses sha256 checksum
        if v_auth != 0 and mode in (ucryptolib.MODE_ECB, ucryptolib.MODE_CBC):
            auth = hashlib.sha256(plain).digest()[: abs(v_auth)]
            if v_auth < 0:
                # fail: same case as above if auth bytes have NUL suffix
                if fail_unsafe and v_pkcs_pad is False and auth[-1] == 0x00:
                    raise ValueError("Cannot validate decryption for this plaintext")
                plain += auth
                auth = b""

        # some modes need to pad to AES 16-byte blocks
        if v_pkcs_pad is True or v_pkcs_pad is False:
            plain = pad(plain, pkcs_pad=v_pkcs_pad)

        # fail to encrypt in modes where it is known unsafe
        if fail_unsafe and mode == ucryptolib.MODE_ECB:
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
            encryptor = ucryptolib.aes(self.key, mode, iv)
        else:
            encryptor = ucryptolib.aes(self.key, mode)
            iv = b""

        # encrypt the plaintext
        encrypted = encryptor.encrypt(plain)

        # for modes that do have inherent authentication, use it
        if mode == ucryptolib.MODE_GCM:
            auth = encryptor.digest()[:v_auth]

        return iv + encrypted + auth

    def decrypt(self, payload, version):
        """AES Decrypt according to krux rules defined by version, returns plaintext bytes"""
        mode = VERSIONS[version]["mode"]
        v_iv = MODE_IVS.get(mode, 0)
        v_pkcs_pad = VERSIONS[version].get("pkcs_pad", False)
        v_auth = VERSIONS[version].get("auth", 0)
        v_compress = VERSIONS[version].get("compress", False)

        # setup decryptor (pulling initialization-vector from payload if necessary)
        if not v_iv:
            decryptor = ucryptolib.aes(self.key, mode)
        else:
            if len(payload) < AES_BLOCK_SIZE + v_iv:
                raise ValueError("Missing IV")
            decryptor = ucryptolib.aes(self.key, mode, payload[:v_iv])
            payload = payload[v_iv:]

        # remove authentication from payload if suffixed to ciphertext
        auth = None
        if v_auth > 0:
            auth = payload[-v_auth:]
            payload = payload[:-v_auth]

        # decrypt the ciphertext
        decrypted = decryptor.decrypt(payload)

        # if authentication added (inherent or added by krux)
        # then: unpad and validate via embeded authentication bytes
        # else: let caller deal with unpad and auth
        if v_auth != 0:
            try:
                decrypted = self._authenticate(
                    decrypted, decryptor, auth, mode, v_auth, v_pkcs_pad
                )
            except:
                decrypted = None

        # for versions that compress
        if decrypted and v_compress:
            decrypted = deflate_decompress(decrypted)

        return decrypted

    def _authenticate(self, decrypted, aes_object, auth, mode, v_auth, v_pkcs_pad):
        if not (
            isinstance(decrypted, bytes)
            # TODO check aes_object
            and (isinstance(auth, bytes) or auth is None)
            and mode in MODE_NUMBERS.values()
            and (isinstance(v_auth, int) and -32 <= v_auth <= 32)
            and (v_pkcs_pad is True or v_pkcs_pad is False or v_pkcs_pad is None)
        ):
            raise ValueError("Invalid call to ._authenticate()")

        # some modes need to unpad
        if v_pkcs_pad in (False, True):
            decrypted = unpad(decrypted, pkcs_pad=v_pkcs_pad)

        if v_auth < 0:
            # auth was added to plaintext
            auth = decrypted[v_auth:]
            decrypted = decrypted[:v_auth]

        # versions that have built-in authentication use their own
        if mode == ucryptolib.MODE_GCM:
            try:
                aes_object.verify(auth)
                return decrypted
            except:
                return None

        # versions that don't have built-in authentication use sha256
        max_attempts = 1
        if v_pkcs_pad is False:
            # NUL padding is imperfect, still attempt to authenticate -- up to a limit...
            # ... of abs(v_auth) + 2 times (ie: auth is all 0x00 + plaintext ends 2 * 0x00)
            max_attempts = abs(v_auth) + 2

        for _ in range(max_attempts):
            cksum = hashlib.sha256(decrypted).digest()[: abs(v_auth)]
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


def pad(some_bytes, pkcs_pad):
    """
    Pads some_bytes to AES block size of 16 bytes, returns bytes
    pkcs_pad: False=NUL-pad, True=PKCS#7-pad, None=no-pad
    """
    if pkcs_pad is None:
        return some_bytes
    len_padding = (16 - len(some_bytes) % 16) % 16
    if pkcs_pad is True:
        if len_padding == 0:
            len_padding = 16
        return some_bytes + (len_padding).to_bytes(1, "big") * len_padding
    if pkcs_pad is False:
        return some_bytes + b"\x00" * len_padding
    raise TypeError("pkcs_pad is not (None, True, False)")


def unpad(some_bytes, pkcs_pad):
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


class MnemonicStorage:
    """Handler of stored encrypted seeds"""

    def __init__(self) -> None:
        self.stored = {}
        self.stored_sd = {}
        try:
            with SDHandler() as sd:
                self.stored_sd = json.loads(sd.read(MNEMONICS_FILE))
        except:
            pass
        try:
            with open(FLASH_PATH + MNEMONICS_FILE, "r") as f:
                self.stored = json.loads(f.read())
        except:
            pass

    def _deprecated_decrypt(self, key, salt, iterations, mode, payload):
        """in-the-wild, some `seeds.json` may have encrypted mnemonic words"""

        def stretch_key(key, salt, iterations):
            return hashlib.pbkdf2_hmac(
                "sha256", key.encode("latin-1"), salt.encode("latin-1"), iterations
            )

        if not (
            isinstance(key, str)
            and isinstance(salt, str)
            and isinstance(iterations, int)
            and isinstance(payload, bytes)
        ):
            return None

        mode_name = [k for k, v in MODE_NUMBERS.items() if v == mode][0]
        stretched_key = stretch_key(key, salt, iterations)
        if mode_name == "AES-CBC":
            decryptor = ucryptolib.aes(stretched_key, mode, payload[:16])
            payload = payload[16:]
        else:
            decryptor = ucryptolib.aes(stretched_key, mode)
        try:
            plaintext = unpad(decryptor.decrypt(payload), pkcs_pad=False)
            return plaintext.decode()
        except:
            return None

    def list_mnemonics(self, sd_card=False):
        """List all seeds stored on a file"""
        mnemonic_ids = []
        source = self.stored_sd if sd_card else self.stored
        for mnemonic_id in source:
            mnemonic_ids.append(mnemonic_id)
        return mnemonic_ids

    def decrypt(self, key, mnemonic_id, sd_card=False):
        """Decrypt a selected encrypted mnemonic from a file"""
        try:
            if sd_card:
                stored_value = self.stored_sd.get(mnemonic_id)
            else:
                stored_value = self.stored.get(mnemonic_id)
        except:
            return None

        if stored_value.get("b64_kef"):
            kef_wrapper = base_decode(stored_value["b64_kef"], 64)
            id_, version, iterations, data = kef_unwrap(kef_wrapper)
            decryptor = AESCipher(key, id_, iterations)
            decrypted = decryptor.decrypt(data, version)
            if decrypted:
                return bip39.mnemonic_from_bytes(decrypted)
        else:
            iterations = stored_value.get("key_iterations")
            version = stored_value.get("version")
            mode = VERSIONS[version]["mode"]
            data = base_decode(stored_value.get("data"), 64)
            return self._deprecated_decrypt(key, mnemonic_id, iterations, mode, data)
        return None

    def store_encrypted(self, key, mnemonic_id, mnemonic, sd_card=False, i_vector=None):
        """Saves the encrypted mnemonic on a file, returns True if successful"""
        iterations = Settings().encryption.pbkdf2_iterations
        encryptor = AESCipher(key, mnemonic_id, iterations)
        mode_name = Settings().encryption.version
        plain = bip39.mnemonic_to_bytes(mnemonic)
        version = suggest_versions(plain, mode_name)[0]
        encrypted = encryptor.encrypt(plain, version, i_vector)
        kef_wrapper = kef_wrap(mnemonic_id, version, iterations, encrypted)
        b64_kef = base_encode(kef_wrapper, 64).decode()
        mnemonics = {}
        if sd_card:
            # load current MNEMONICS_FILE
            try:
                with SDHandler() as sd:
                    contents = sd.read(MNEMONICS_FILE)
                    orig_len = len(contents)
                    mnemonics = json.loads(contents)
            except:
                orig_len = 0

            # save the new MNEMONICS_FILE
            try:
                with SDHandler() as sd:
                    mnemonics[mnemonic_id] = {"b64_kef": b64_kef}
                    contents = json.dumps(mnemonics)
                    # pad contents to orig_len to avoid abandoned bytes on sdcard
                    if len(contents) < orig_len:
                        contents += " " * (orig_len - len(contents))
                    sd.write(MNEMONICS_FILE, contents)
            except:
                return False
        else:
            try:
                # load current MNEMONICS_FILE
                with open(FLASH_PATH + MNEMONICS_FILE, "r") as f:
                    mnemonics = json.loads(f.read())
            except:
                pass
            try:
                # save the new MNEMONICS_FILE
                with open(FLASH_PATH + MNEMONICS_FILE, "w") as f:
                    mnemonics[mnemonic_id] = {"b64_kef": b64_kef}
                    f.write(json.dumps(mnemonics))
            except:
                return False
        return True

    def del_mnemonic(self, mnemonic_id, sd_card=False):
        """Remove an entry from encrypted mnemonics file"""
        if sd_card:
            self.stored_sd.pop(mnemonic_id)
            with SDHandler() as sd:
                orig_len = len(sd.read(MNEMONICS_FILE))
                contents = json.dumps(self.stored_sd)
                # pad contents to orig_len to avoid abandoned bytes on sdcard
                if len(contents) < orig_len:
                    contents += " " * (orig_len - len(contents))
                sd.write(MNEMONICS_FILE, contents)
        else:
            self.stored.pop(mnemonic_id)
            with open(FLASH_PATH + MNEMONICS_FILE, "w") as f:
                f.write(json.dumps(self.stored))


class EncryptedQRCode:
    """Creates and decrypts encrypted mnemonic QR codes"""

    def __init__(self) -> None:
        self.mnemonic_id = None
        self.version = None
        self.iterations = Settings().encryption.pbkdf2_iterations
        self.encrypted_data = None

    def create(self, key, mnemonic_id, mnemonic, i_vector=None):
        """encrypted mnemonic QR codes"""
        mode_name = Settings().encryption.version
        encryptor = AESCipher(key, mnemonic_id, self.iterations)
        bytes_to_encrypt = bip39.mnemonic_to_bytes(mnemonic)
        self.version = suggest_versions(bytes_to_encrypt, mode_name)[0]
        bytes_encrypted = encryptor.encrypt(bytes_to_encrypt, self.version, i_vector)
        return kef_wrap(mnemonic_id, self.version, self.iterations, bytes_encrypted)

    def public_data(self, data):
        """Parse and returns encrypted mnemonic QR codes public data"""
        try:
            (self.mnemonic_id, self.version, self.iterations, self.encrypted_data) = (
                kef_unwrap(data)
            )
            version_name = VERSIONS[self.version]["name"]
        except:
            return None

        return "\n".join(
            [
                "Encrypted QR Code:",
                "ID: " + self.mnemonic_id,
                "Version: " + version_name,
                "Key iter.: " + str(self.iterations),
            ]
        )

    def decrypt(self, key):
        """Decrypts encrypted mnemonic QR codes"""
        decryptor = AESCipher(key, self.mnemonic_id, self.iterations)
        decrypted_data = decryptor.decrypt(self.encrypted_data, self.version)
        return decrypted_data


def kef_wrap(id_, version, iterations, payload):
    """
    Wraps inputs into KEF Encryption Format, returns bytes
    """

    try:
        # latin-1 encoding enables all byte values in id_ (salt for key-stretch)
        id_ = id_.encode("latin-1")
        assert 0 <= len(id_) <= 255
        len_id = len(id_).to_bytes(1, "big")
    except:
        raise ValueError("Invalid ID")

    try:
        assert 0 <= version <= 255 and version in VERSIONS
    except:
        raise ValueError("Invalid version")

    try:
        assert isinstance(iterations, int)
        if iterations % 10000 == 0:
            iterations = iterations // 10000
            assert 1 <= iterations <= 10000 * 10000
        else:
            assert 10000 < iterations < 2**24
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


def kef_unwrap(kef_bytes):
    """
    Unwraps KEF Encryption Format bytes, returns tuple of parsed values
    """
    len_id = kef_bytes[0]
    version = kef_bytes[1 + len_id]  # out-of-order reading to validate version early
    if version not in VERSIONS:
        raise ValueError("Invalid format")
    id_ = kef_bytes[1 : 1 + len_id].decode("latin-1")
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
