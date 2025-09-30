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

import ujson as json
import hashlib
from krux import kef
from .baseconv import base_encode, base_decode
from .sd_card import SDHandler
from embit import bip39
from .settings import FLASH_PATH, MNEMONICS_FILE

FLASH_PATH_STR = "/" + FLASH_PATH + "/%s"

QR_CODE_ITER_MULTIPLE = 10000


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
            with open(FLASH_PATH_STR % MNEMONICS_FILE, "r") as f:
                self.stored = json.loads(f.read())
        except:
            pass

    def _deprecated_decrypt(self, key, salt, iterations, mode, payload):
        """in-the-wild, some `seeds.json` may have encrypted mnemonic words"""

        def stretch_key(key, salt, iterations):
            key = key if isinstance(key, bytes) else key.encode()
            salt = salt if isinstance(salt, bytes) else salt.encode()
            return hashlib.pbkdf2_hmac("sha256", key, salt, iterations)

        if not (isinstance(iterations, int) and isinstance(payload, bytes)):
            return None

        mode_name = [k for k, v in kef.MODE_NUMBERS.items() if v == mode][0]
        stretched_key = stretch_key(key, salt, iterations)
        if mode_name == "AES-CBC":
            decryptor = kef.ucryptolib.aes(stretched_key, mode, payload[:16])
            payload = payload[16:]
        else:
            decryptor = kef.ucryptolib.aes(stretched_key, mode)
        try:
            # pylint: disable=W0212
            plaintext = kef._unpad(decryptor.decrypt(payload), pkcs_pad=False)
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
            envelope = base_decode(stored_value["b64_kef"], 64)
            id_, version, iterations, data = kef.unwrap(envelope)
            decryptor = kef.Cipher(key, id_, iterations)
            decrypted = decryptor.decrypt(data, version)
            if decrypted:
                return bip39.mnemonic_from_bytes(decrypted)
        else:
            iterations = stored_value.get("key_iterations")
            version = stored_value.get("version")
            mode = kef.VERSIONS[version]["mode"]
            data = base_decode(stored_value.get("data"), 64)
            return self._deprecated_decrypt(key, mnemonic_id, iterations, mode, data)
        return None

    def store_encrypted_kef(self, mnemonic_id, kef_envelope, sd_card=False):
        """Saves a KEF envelope directly to storage, returns True if successful"""
        b64_kef = base_encode(kef_envelope, 64)
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
                with open(FLASH_PATH_STR % MNEMONICS_FILE, "r") as f:
                    mnemonics = json.loads(f.read())
            except:
                pass
            try:
                # save the new MNEMONICS_FILE
                with open(FLASH_PATH_STR % MNEMONICS_FILE, "w") as f:
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
            with open(FLASH_PATH_STR % MNEMONICS_FILE, "w") as f:
                f.write(json.dumps(self.stored))
