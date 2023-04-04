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

SEED_FILE = "seeds.json"


class AESCipher:
    """Helper for AES encrypt/decrypt"""

    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        """Encrypt using AES MODE_ECB and return the value encoded as base64"""
        data_bytes = raw.encode()
        encryptor = ucryptolib.aes(self.key, ucryptolib.MODE_ECB)
        encrypted = encryptor.encrypt(
            data_bytes + b"\x00" * ((16 - (len(data_bytes) % 16)) % 16)
        )
        return base_encode(encrypted, 64)

    def decrypt(self, enc):
        """Decrypt a base64 using AES MODE_ECB and return the value decoded as string"""
        encrypted = base_decode(enc, 64)  # test - decode 64
        decryptor = ucryptolib.aes(self.key, ucryptolib.MODE_ECB)
        load = decryptor.decrypt(encrypted).decode("utf-8")
        return load.replace("\x00", "")


class StoredSeeds:
    """Handler of stored encrypted seeds"""

    def __init__(self) -> None:
        self.encrypted_store = {}
        try:
            with SDHandler() as sd:
                self.encrypted_store = json.loads(sd.read(SEED_FILE))
        except:
            pass

    def list_fingerprints(self):
        """List all seeds stored on a file"""
        fingerprints = []
        for fingerprint in self.encrypted_store:
            fingerprints.append(fingerprint)
        return fingerprints

    def decrypt(self, key, fingerprint):
        """Decrypt a selected seed from a file"""
        decryptor = AESCipher(key)
        try:
            load = self.encrypted_store.get(fingerprint)
            words = decryptor.decrypt(load)
        except:
            return None
        return words

    def store_encrypted(self, key, fingerprint, seed):
        """Saves the seed encrypted on a file"""
        encryptor = AESCipher(key)
        encrypted = encryptor.encrypt(seed).decode("utf-8")
        seeds = {}

        # load current SEED_FILE
        try:
            with SDHandler() as sd:
                seeds = json.loads(sd.read(SEED_FILE))
        except:
            pass

        # save the new SEED_FILE
        try:
            with SDHandler() as sd:
                seeds[fingerprint] = encrypted
                sd.write(SEED_FILE, json.dumps(seeds))
        except:
            pass

    def del_seed(self, fingerprint):
        """Remove an entry from encrypted seeds file"""
        self.encrypted_store.pop(fingerprint)
        try:
            with SDHandler() as sd:
                sd.write(SEED_FILE, json.dumps(self.encrypted_store))
        except:
            pass
