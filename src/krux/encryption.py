# The MIT License (MIT)

# Copyright (c) 2021-2023 Krux contributors

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
from .krux_settings import Settings, PBKDF2_HMAC_ECB, PBKDF2_HMAC_CBC, AES_BLOCK_SIZE


MNEMONICS_FILE = "seeds.json"

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


class AESCipher:
    """Helper for AES encrypt/decrypt"""

    def __init__(self, key, salt, iterations):
        self.key = hashlib.pbkdf2_hmac(
            "sha256", key.encode(), salt.encode(), iterations
        )

    def encrypt(self, raw, mode=ucryptolib.MODE_ECB, iv=None):
        """Encrypt using AES MODE_ECB and return the value encoded as base64"""
        data_bytes = raw.encode()
        encryptor = ucryptolib.aes(self.key, mode, iv)
        if iv:
            data_bytes = iv + data_bytes
        encrypted = encryptor.encrypt(
            data_bytes + b"\x00" * ((16 - (len(data_bytes) % 16)) % 16)
        )
        return base_encode(encrypted, 64)

    def decrypt(self, encrypted, mode, iv=None):
        """Decrypt a base64 using AES MODE_ECB and return the value decoded as string"""
        decryptor = ucryptolib.aes(self.key, mode, iv)
        load = decryptor.decrypt(encrypted).decode("utf-8")
        return load.replace("\x00", "")


class MnemonicStorage:
    """Handler of stored encrypted seeds"""

    def __init__(self) -> None:
        self.stored = {}
        self.stored_sd = {}
        self.has_sd_card = False
        try:
            with SDHandler() as sd:
                self.has_sd_card = True
                self.stored_sd = json.loads(sd.read(MNEMONICS_FILE))
        except:
            pass
        try:
            with open("/flash/" + MNEMONICS_FILE, "r") as f:
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
                version = self.stored_sd.get(mnemonic_id)["version"]
        except:
            return None
        data = base_decode(encrypted_data, 64)
        mode = VERSION_MODE[version]
        if mode == ucryptolib.MODE_ECB:
            encrypted_mnemonic = data
            iv = None
        else:
            encrypted_mnemonic = data[AES_BLOCK_SIZE:]
            iv = data[:AES_BLOCK_SIZE]
        decryptor = AESCipher(key, mnemonic_id, iterations)
        words = decryptor.decrypt(encrypted_mnemonic, mode, iv)
        return words

    def store_encrypted(self, key, mnemonic_id, mnemonic, sd_card=False, iv=None):
        """Saves the encrypted mnemonic on a file"""
        encryptor = AESCipher(key, mnemonic_id, Settings().encryption.pbkdf2_iterations)
        mode = VERSION_MODE[Settings().encryption.version]
        encrypted = encryptor.encrypt(mnemonic, mode, iv).decode("utf-8")
        mnemonics = {}
        success = True
        if sd_card:
            # load current MNEMONICS_FILE
            try:
                with SDHandler() as sd:
                    mnemonics = json.loads(sd.read(MNEMONICS_FILE))
            except:
                pass

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
                    sd.write(MNEMONICS_FILE, json.dumps(mnemonics))
            except:
                success = False
        else:
            try:
                # load current MNEMONICS_FILE
                with open("/flash/" + MNEMONICS_FILE, "r") as f:
                    mnemonics = json.loads(f.read())
            except:
                pass
            try:
                # save the new MNEMONICS_FILE
                with open("/flash/" + MNEMONICS_FILE, "w") as f:
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
                success = False
        return success

    def del_mnemonic(self, mnemonic_id, sd_card=False):
        """Remove an entry from encrypted mnemonics file"""
        if sd_card:
            self.stored_sd.pop(mnemonic_id)
            try:
                with SDHandler() as sd:
                    sd.write(MNEMONICS_FILE, json.dumps(self.stored_sd))
            except:
                pass
        else:
            self.stored.pop(mnemonic_id)
            try:
                with open("/flash/" + MNEMONICS_FILE, "w") as f:
                    f.write(json.dumps(self.stored))
            except:
                pass
