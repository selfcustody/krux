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
from .krux_settings import Settings, PBKDF2_HMAC_ECB, PBKDF2_HMAC_CBC
from embit import bip39


MNEMONICS_FILE = "seeds.json"
FLASH_PATH = "/flash/"

VERSION_MODE = {
    "AES-ECB": ucryptolib.MODE_ECB,
    "AES-CBC": ucryptolib.MODE_CBC,
    PBKDF2_HMAC_ECB: ucryptolib.MODE_ECB,
    PBKDF2_HMAC_CBC: ucryptolib.MODE_CBC,
}

VERSION_NUMBER = {
    "AES-ECB": PBKDF2_HMAC_ECB,
    "AES-CBC": PBKDF2_HMAC_CBC,
}

AES_BLOCK_SIZE = 16
QR_CODE_ITER_MULTIPLE = 10000


class AESCipher:
    """Helper for AES encrypt/decrypt"""

    def __init__(self, key, salt, iterations):
        self.key = hashlib.pbkdf2_hmac(
            "sha256", key.encode(), salt.encode(), iterations
        )

    def encrypt(self, raw, mode=ucryptolib.MODE_ECB, i_vector=None):
        """Encrypt using AES-ECB or AES-CBC and return the value as bytes"""
        plain = raw.encode("latin-1") if isinstance(raw, str) else raw
        plain += b"\x00" * ((16 - (len(plain) % 16)) % 16)
        if mode == ucryptolib.MODE_ECB:
            unique_blocks = len(
                set((plain[x : x + 16] for x in range(0, len(plain), 16)))
            )
            if unique_blocks != len(plain) // 16:
                raise ValueError("Duplicate blocks in ECB mode")
        if i_vector:
            encryptor = ucryptolib.aes(self.key, mode, i_vector)
        else:
            encryptor = ucryptolib.aes(self.key, mode)
        encrypted = encryptor.encrypt(plain)
        if i_vector:
            encrypted = i_vector + encrypted
        return encrypted

    def decrypt(self, encrypted, mode):
        """Decrypt and return value as bytes"""
        if mode == ucryptolib.MODE_ECB:
            decryptor = ucryptolib.aes(self.key, mode)
        else:
            decryptor = ucryptolib.aes(self.key, mode, encrypted[:AES_BLOCK_SIZE])
            encrypted = encrypted[AES_BLOCK_SIZE:]
        return decryptor.decrypt(encrypted)


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
        mode = VERSION_MODE[version]
        decryptor = AESCipher(key, mnemonic_id, iterations)
        decrypted = decryptor.decrypt(data, mode)
        words = decrypted.decode().replace("\x00", "")
        return words

    def store_encrypted(self, key, mnemonic_id, mnemonic, sd_card=False, i_vector=None):
        """Saves the encrypted mnemonic on a file, returns True if successful"""
        encryptor = AESCipher(key, mnemonic_id, Settings().encryption.pbkdf2_iterations)
        mode = VERSION_MODE[Settings().encryption.version]
        encrypted = encryptor.encrypt(mnemonic, mode, i_vector)
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
                    mnemonics[mnemonic_id]["version"] = VERSION_NUMBER[
                        Settings().encryption.version
                    ]
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
                    mnemonics[mnemonic_id]["version"] = VERSION_NUMBER[
                        Settings().encryption.version
                    ]
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
        self.version = VERSION_NUMBER[Settings().encryption.version]
        self.iterations = Settings().encryption.pbkdf2_iterations
        self.encrypted_data = None

    def create(self, key, mnemonic_id, mnemonic, i_vector=None):
        """encrypted mnemonic QR codes"""
        iterations = (
            Settings().encryption.pbkdf2_iterations // QR_CODE_ITER_MULTIPLE
        ) * QR_CODE_ITER_MULTIPLE
        version = VERSION_NUMBER[Settings().encryption.version]
        mode = VERSION_MODE[version]
        encryptor = AESCipher(key, mnemonic_id, iterations)
        bytes_to_encrypt = bip39.mnemonic_to_bytes(mnemonic)
        bytes_to_encrypt += hashlib.sha256(bytes_to_encrypt).digest()[:16]
        bytes_encrypted = encryptor.encrypt(bytes_to_encrypt, mode, i_vector)
        return kef_encode(mnemonic_id, version, iterations, bytes_encrypted)

    def public_data(self, data):
        """Parse and returns encrypted mnemonic QR codes public data"""
        try:
            (self.mnemonic_id, self.version, self.iterations, self.encrypted_data) = (
                kef_decode(data)
            )
            version_name = [k for k, v in VERSION_NUMBER.items() if v == self.version][
                0
            ]
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
        mode = VERSION_MODE[self.version]
        decryptor = AESCipher(key, self.mnemonic_id, self.iterations)
        decrypted_data = decryptor.decrypt(self.encrypted_data, mode)
        mnemonic_data = decrypted_data[:-AES_BLOCK_SIZE]
        checksum = decrypted_data[-AES_BLOCK_SIZE:]
        # Data validation:
        if hashlib.sha256(mnemonic_data).digest()[:16] != checksum:
            return None
        return mnemonic_data


def kef_encode(id_, version, iterations, ciphertext):
    """
    encodes inputs into krux_encryption_format, returns bytes
    """
    try:
        assert 0 <= len(id_.encode()) <= 255
    except:
        raise ValueError("Invalid ID")

    try:
        assert 0 <= version <= 255 and version in VERSION_MODE
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

    if not isinstance(ciphertext, bytes):
        raise ValueError("Ciphertext is not bytes")
    if len(ciphertext) % 16 != 0:
        raise ValueError("Ciphertext is not aligned")
    if len(ciphertext) // 16 < 2:
        raise ValueError("Ciphertext is too short")

    return b"".join(
        [
            len(id_).to_bytes(1, "big"),
            id_.encode(),
            version.to_bytes(1, "big"),
            int(iterations).to_bytes(3, "big"),
            ciphertext,
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
    ciphertext = payload
    if len(ciphertext) % 16 != 0:
        raise ValueError("Ciphertext is not aligned")
    if len(ciphertext) // 16 < 2:
        raise ValueError("Ciphertext is too short")
    return (id_, version, iterations, ciphertext)
