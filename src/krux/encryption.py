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

STORE_FILE_PATH = "/flash/seeds.json"

class AESCipher(object):

    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        data_bytes = raw.encode()
        encryptor = ucryptolib.aes(self.key, 1)
        encrypted = encryptor.encrypt(data_bytes + b'\x00' * ((16 - (len(data_bytes) % 16)) % 16))
        return base_encode(encrypted,64)

    def decrypt(self, enc):
        encrypted = base_decode(enc, 64) # test - decode 64
        decryptor = ucryptolib.aes(self.key, 1)
        load = decryptor.decrypt(encrypted).decode('utf-8')
        return load.replace('\x00', '')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
    
class StoredSeeds:
    def __init__(self) -> None:
        self.encrypted_store = {}
        try:
            with open(STORE_FILE_PATH, "r") as f:
                self.encrypted_store = json.loads(f.read())
        except:
            pass

    def list_fingerprints(self):
        fingerprints = []
        for fingerprint in self.encrypted_store:
            fingerprints.append(fingerprint)
        return fingerprints
    
    def decrypt(self, key, fingerprint):
        decryptor = AESCipher(key)
        try:
            load = self.encrypted_store.get(fingerprint)
            words = decryptor.decrypt(load)
            print(words)
        except:
            return None
        return words
    
    def sotore_encrypted(self, key, fingerprint, seed):
        encryptor = AESCipher(key)
        encrypted = encryptor.encrypt(seed).decode('utf-8')
        seeds = {}
        try:
            # save the new SETTINGS_FILENAME
            with open(STORE_FILE_PATH, "r") as f:
                seeds = json.loads(f.read())
                print("seeds1",seeds)
        except:
            pass
        try:
            with open(STORE_FILE_PATH, "w") as f:
                seeds[fingerprint] = encrypted
                print("seeds2",seeds)
                f.write(json.dumps(seeds))
        except:
            pass
    
    def del_seed(self, fingerprint):
        self.encrypted_store.pop(fingerprint)
        try:
            with open(STORE_FILE_PATH, "w") as f:
                f.write(json.dumps(self.encrypted_store))
        except:
            pass


