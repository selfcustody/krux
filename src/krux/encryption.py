# The MIT License (MIT)

# Copyright (c) 2021-2024 Krux contributors

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
    },
    1: {
        "name": "AES-CBC",
        "mode": ucryptolib.MODE_CBC,
        "iv": 16,
    },
    2: {
        "name": "AES-ECB v2",
        "mode": ucryptolib.MODE_ECB,
        "pkcs_pad": True,
        "auth": -4,
    },
    3: {
        "name": "AES-CBC v2",
        "mode": ucryptolib.MODE_CBC,
        "iv": 16,
        "pkcs_pad": True,
        "auth": -4,
    },
    4: {
        "name": "AES-ECB v3",
        "mode": ucryptolib.MODE_ECB,
        "auth": 3,
    },
    5: {
        "name": "AES-CBC v3",
        "mode": ucryptolib.MODE_CBC,
        "iv": 16,
        "auth": 4,
    },
    6: {
        "name": "AES-GCM",
        "mode": ucryptolib.MODE_GCM,
        "iv": 12,  # 12 bytes of IV - nonce
        "auth": 4,  # 4 bytes validation tag
    },
}
VERSION_NUMBERS = {v["name"]: k for k, v in VERSIONS.items()}

AES_BLOCK_SIZE = 16
QR_CODE_ITER_MULTIPLE = 10000


class AESCipher:
    """More than just a helper for AES encrypt/decrypt. Enforces krux encryption versions"""

    def __init__(self, key, salt, iterations):
        self.key = hashlib.pbkdf2_hmac(
            "sha256", key.encode(), salt.encode(), iterations
        )

    def encrypt(self, plain, version, iv=b""):
        """AES encrypt according to krux rules defined by version, returns payload bytes"""
        mode = VERSIONS[version]["mode"]
        v_iv = VERSIONS[version].get("iv", 0)
        v_pkcs_pad = VERSIONS[version].get("pkcs_pad", False)
        v_auth = VERSIONS[version].get("auth", 0)
        auth = b""
        plain = plain.encode("latin-1") if isinstance(plain, str) else plain

        # for modes that don't have authentication, krux uses sha256 checksum
        if v_auth != 0 and mode in (ucryptolib.MODE_ECB, ucryptolib.MODE_CBC):
            auth = hashlib.sha256(plain).digest()[: abs(v_auth)]
            if v_auth < 0:
                plain += auth
                auth = b""

        # AES plaintext must be divisible into 16-byte blocks
        plain = pad(plain, pkcs_pad=v_pkcs_pad)

        # fail to encrypt in modes where it is known unsafe
        if mode == ucryptolib.MODE_ECB:
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
        v_iv = VERSIONS[version].get("iv", 0)
        v_pkcs_pad = VERSIONS[version].get("pkcs_pad", False)
        v_auth = VERSIONS[version].get("auth", 0)

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
            # need to unpad
            decrypted = unpad(decrypted, pkcs_pad=v_pkcs_pad)
            if mode == ucryptolib.MODE_GCM:
                # for modes that have authentication built-in
                try:
                    decryptor.verify(auth)
                except:
                    return None
            else:
                # for modes that don't, krux uses sha256 checksum
                if v_auth < 0:
                    auth = decrypted[v_auth:]
                    decrypted = decrypted[:v_auth]
                if hashlib.sha256(decrypted).digest()[: abs(v_auth)] != auth:
                    return None

        return decrypted


def pad(some_bytes, pkcs_pad=False):
    """Pads some_bytes to AES block size of 16 bytes, returns bytes"""
    len_padding = (16 - len(some_bytes) % 16) % 16
    if pkcs_pad:
        if len_padding == 0:
            len_padding = 16
        return some_bytes + (len_padding).to_bytes(1, "big") * len_padding
    return some_bytes + b"\x00" * len_padding


def unpad(some_bytes, pkcs_pad=False):
    """Strips padding from some_bytes, returns bytes"""
    if pkcs_pad:
        len_padding = some_bytes[-1]
        return some_bytes[:-len_padding]
    stripped = some_bytes.replace(b"\x00", b"")
    if 0 < len(some_bytes) - len(stripped) < 16:
        return stripped
    return some_bytes


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
                encrypted_data = self.stored_sd.get(mnemonic_id)["data"]
                iterations = self.stored_sd.get(mnemonic_id)["key_iterations"]
                version = self.stored_sd.get(mnemonic_id)["version"]
            else:
                encrypted_data = self.stored.get(mnemonic_id)["data"]
                iterations = self.stored.get(mnemonic_id)["key_iterations"]
                version = self.stored.get(mnemonic_id)["version"]
        except:
            return None
        data = base_decode(encrypted_data, 64)
        decryptor = AESCipher(key, mnemonic_id, iterations)
        decrypted = decryptor.decrypt(data, version)
        if not in_cipher_checksum(version):
            return bip39.mnemonic_from_bytes(decrypted)
        # Data validation
        mnemonic_data = decrypted[:-AES_BLOCK_SIZE]
        cksum = decrypted[-AES_BLOCK_SIZE:]
        if hashlib.sha256(mnemonic_data).digest()[:16] == cksum:
            return bip39.mnemonic_from_bytes(mnemonic_data)
        try:  # Deprecated, but supported for decryption
            words = unpad(decrypted).decode()
        except:
            words = None
        return words

    def store_encrypted(self, key, mnemonic_id, mnemonic, sd_card=False, i_vector=None):
        """Saves the encrypted mnemonic on a file, returns True if successful"""
        encryptor = AESCipher(key, mnemonic_id, Settings().encryption.pbkdf2_iterations)
        version = VERSION_NUMBERS[Settings().encryption.version]
        plain = bip39.mnemonic_to_bytes(mnemonic)
        if in_cipher_checksum(version):
            plain += hashlib.sha256(plain).digest()[:16]
        encrypted = encryptor.encrypt(plain, version, i_vector)
        encrypted = base_encode(encrypted, 64).decode()
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
                    mnemonics[mnemonic_id] = {}
                    mnemonics[mnemonic_id]["version"] = version
                    mnemonics[mnemonic_id][
                        "key_iterations"
                    ] = Settings().encryption.pbkdf2_iterations
                    mnemonics[mnemonic_id]["data"] = encrypted
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
                    mnemonics[mnemonic_id] = {}
                    mnemonics[mnemonic_id]["version"] = version
                    mnemonics[mnemonic_id][
                        "key_iterations"
                    ] = Settings().encryption.pbkdf2_iterations
                    mnemonics[mnemonic_id]["data"] = encrypted
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
        self.version = VERSION_NUMBERS[Settings().encryption.version]
        self.iterations = Settings().encryption.pbkdf2_iterations
        self.encrypted_data = None

    def create(self, key, mnemonic_id, mnemonic, i_vector=None):
        """encrypted mnemonic QR codes"""
        iterations = (
            Settings().encryption.pbkdf2_iterations // QR_CODE_ITER_MULTIPLE
        ) * QR_CODE_ITER_MULTIPLE
        version = VERSION_NUMBERS[Settings().encryption.version]
        encryptor = AESCipher(key, mnemonic_id, iterations)
        bytes_to_encrypt = bip39.mnemonic_to_bytes(mnemonic)
        if in_cipher_checksum(version):
            bytes_to_encrypt += hashlib.sha256(bytes_to_encrypt).digest()[:16]
        bytes_encrypted = encryptor.encrypt(bytes_to_encrypt, version, i_vector)
        return kef_encode(mnemonic_id, version, iterations, bytes_encrypted)

    def public_data(self, data):
        """Parse and returns encrypted mnemonic QR codes public data"""
        try:
            (self.mnemonic_id, self.version, self.iterations, self.encrypted_data) = (
                kef_decode(data)
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
        if not in_cipher_checksum(self.version):
            mnemonic_data = decrypted_data
        else:
            # Data validation:
            mnemonic_data = decrypted_data[:-AES_BLOCK_SIZE]
            cksum = decrypted_data[-AES_BLOCK_SIZE:]
            if hashlib.sha256(mnemonic_data).digest()[:16] != cksum:
                return None
        return mnemonic_data


def in_cipher_checksum(version):
    """
    Returns True if the ciphertext contains a block of checksum
    """
    return VERSIONS[version].get("auth", 0) == 0


def kef_encode(id_, version, iterations, payload):
    """
    encodes inputs into krux_encryption_format, returns bytes
    """
    try:
        assert 0 <= len(id_.encode()) <= 255
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
    except:
        raise ValueError("Invalid iterations")

    extra = VERSIONS[version].get("iv", 0)
    if VERSIONS[version].get("auth", 0) <= 0:
        extra += 0
    else:
        extra += VERSIONS[version]["auth"]
    if not isinstance(payload, bytes):
        raise ValueError("Payload is not bytes")
    if (len(payload) - extra) % 16 != 0:
        raise ValueError("Ciphertext is not aligned")
    if (len(payload) - extra) // 16 < 1:
        raise ValueError("Ciphertext is too short")

    return b"".join(
        [
            len(id_).to_bytes(1, "big"),
            id_.encode(),
            version.to_bytes(1, "big"),
            int(iterations).to_bytes(3, "big"),
            payload,
        ]
    )


def kef_decode(kef_bytes):
    """
    decodes krux_encryption_format bytes, returns tuple of parsed values
    """
    len_id = kef_bytes[0]
    try:
        id_ = kef_bytes[1 : 1 + len_id].decode()
    except:
        raise ValueError("Invalid ID encoding")
    version = kef_bytes[1 + len_id]
    kef_iterations = int.from_bytes(kef_bytes[2 + len_id : 5 + len_id], "big")
    if kef_iterations <= 10000:
        iterations = kef_iterations * 10000
    else:
        iterations = kef_iterations
    payload = kef_bytes[len_id + 5 :]
    if len(payload) % 16 != 0:
        raise ValueError("Ciphertext is not aligned")
    if len(payload) // 16 < 2:
        raise ValueError("Ciphertext is too short")
    return (id_, version, iterations, payload)
