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

MNEMONICS_FILE = "seeds.json"
MODE_ECB = 3


class AESCipher:
    """Helper for AES encrypt/decrypt"""

    def __init__(self, key, salt):
        self.key = hashlib.pbkdf2_hmac("sha256", key.encode(), salt.encode(), 100000)

    def encrypt(self, raw):
        """Encrypt using AES MODE_ECB and return the value encoded as base64"""
        data_bytes = raw.encode()
        encryptor = ucryptolib.aes(self.key, MODE_ECB)
        encrypted = encryptor.encrypt(
            data_bytes + b"\x00" * ((16 - (len(data_bytes) % 16)) % 16)
        )
        return base_encode(encrypted, 64)

    def decrypt(self, enc):
        """Decrypt a base64 using AES MODE_ECB and return the value decoded as string"""
        encrypted = base_decode(enc, 64)  # test - decode 64
        decryptor = ucryptolib.aes(self.key, MODE_ECB)
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
                self.stored_sd = json.loads(sd.read(MNEMONICS_FILE))
                self.has_sd_card = True
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
        decryptor = AESCipher(key, mnemonic_id)
        try:
            if sd_card:
                load = self.stored_sd.get(mnemonic_id)
            else:
                load = self.stored.get(mnemonic_id)
            words = decryptor.decrypt(load)
        except:
            return None
        return words

    def store_encrypted(self, key, mnemonic_id, mnemonic, sd_card=False):
        """Saves the encrypted mnemonic on a file"""
        encryptor = AESCipher(key, mnemonic_id)
        encrypted = encryptor.encrypt(mnemonic).decode("utf-8")
        mnemonics = {}
        success = True
        if sd_card:
            # load current MNEMONICS_FILE
            try:
                with SDHandler() as sd:
                    mnemonics = json.loads(sd.read(MNEMONICS_FILE))
            except:
                success = False

            # save the new MNEMONICS_FILE
            try:
                with SDHandler() as sd:
                    mnemonics[mnemonic_id] = encrypted
                    sd.write(MNEMONICS_FILE, json.dumps(mnemonics))
            except:
                success = False
        else:
            try:
                # save the new SETTINGS_FILENAME
                with open("/flash/" + MNEMONICS_FILE, "r") as f:
                    mnemonics = json.loads(f.read())
            except:
                success = False
            try:
                with open("/flash/" + MNEMONICS_FILE, "w") as f:
                    mnemonics[mnemonic_id] = encrypted
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
