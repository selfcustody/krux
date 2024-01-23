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

from ..krux_settings import t, Settings, AES_BLOCK_SIZE
from ..themes import theme
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
    ESC_KEY,
    LETTERS,
    UPPERCASE_LETTERS,
    NUM_SPECIAL_1,
    NUM_SPECIAL_2,
)

ENCRYPTION_KEY_MAX_LEN = 200


class EncryptionKey(Page):
    """UI to capture an encryption key"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def encryption_key(self):
        """Loads and returns an ecnryption key from keypad or QR code"""
        submenu = Menu(
            self.ctx,
            [
                (t("Type Key"), self.load_key),
                (t("Scan Key QR code"), self.load_qr_encryption_key),
            ],
        )
        _, key = submenu.run_loop()
        if key in (ESC_KEY, MENU_CONTINUE):
            return None

        if key:
            self.ctx.display.clear()
            continue_string = t("Key: ") + key + "\n\n"
            continue_string += t("Continue?")
            if self.prompt(
                continue_string,
                self.ctx.display.height() // 2,
            ):
                return key
        return None

    def load_key(self):
        """Loads and returns a key from keypad"""
        return self.capture_from_keypad(
            t("Key"), [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2]
        )

    def load_qr_encryption_key(self):
        """Loads and returns a key from a QR code"""
        data, _ = self.capture_qr_code()
        if data is None:
            self.flash_text(t("Failed to load key"), theme.error_color)
            return None
        if len(data) > ENCRYPTION_KEY_MAX_LEN:
            self.flash_text(
                t("Maximum length exceeded (%s)") % ENCRYPTION_KEY_MAX_LEN,
                theme.error_color,
            )
            return None
        return data


class EncryptMnemonic(Page):
    """UI with mnemonic encryption output options"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def encrypt_menu(self):
        """Menu with mnemonic encryption output options"""

        def _sd_store_function():
            return self.store_mnemonic_on_memory(sd_card=True)

        if self.has_sd_card():
            sd_store_func = _sd_store_function
        else:
            sd_store_func = None
        encrypt_outputs_menu = [
            (t("Store on Flash"), self.store_mnemonic_on_memory),
            (t("Store on SD Card"), sd_store_func),
            (t("Encrypted QR Code"), self.encrypted_qr_code),
            (t("Back"), lambda: MENU_EXIT),
        ]
        submenu = Menu(self.ctx, encrypt_outputs_menu)
        _, _ = submenu.run_loop()
        return MENU_CONTINUE

    def store_mnemonic_on_memory(self, sd_card=False):
        """Save encrypted mnemonic on flash or sd_card"""
        from ..encryption import MnemonicStorage

        key_capture = EncryptionKey(self.ctx)
        key = key_capture.encryption_key()
        if key is None:
            self.flash_text(t("Mnemonic was not encrypted"))
            return

        version = Settings().encryption.version
        i_vector = None
        if version == "AES-CBC":
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Additional entropy from camera required for AES-CBC mode")
            )
            if not self.prompt(t("Proceed?"), self.ctx.display.bottom_prompt_line):
                return
            from .capture_entropy import CameraEntropy

            camera_entropy = CameraEntropy(self.ctx)
            entropy = camera_entropy.capture(show_entropy_details=False)
            if entropy is None:
                self.flash_text(t("Mnemonic was not encrypted"))
                return
            i_vector = entropy[:AES_BLOCK_SIZE]
        self.ctx.display.clear()
        mnemonic_storage = MnemonicStorage()
        mnemonic_id = None
        if self.prompt(
            t(
                "Give this mnemonic a custom ID? Otherwise current fingerprint will be used"
            ),
            self.ctx.display.height() // 2,
        ):
            mnemonic_id = self.capture_from_keypad(
                t("Mnemonic ID"),
                [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1],
            )
        if mnemonic_id in (None, ESC_KEY):
            mnemonic_id = self.ctx.wallet.key.fingerprint_hex_str()
        if mnemonic_id in mnemonic_storage.list_mnemonics(sd_card):
            self.flash_text(
                t("ID already exists\n") + t("Encrypted mnemonic was not stored")
            )
            del mnemonic_storage
            return
        words = self.ctx.wallet.key.mnemonic
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing ..."))
        if mnemonic_storage.store_encrypted(key, mnemonic_id, words, sd_card, i_vector):
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Encrypted mnemonic was stored with ID: ") + mnemonic_id
            )
        else:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Failed to store mnemonic"))
        self.ctx.input.wait_for_button()
        del mnemonic_storage

    def encrypted_qr_code(self):
        """Exports an encryprted mnemonic QR code"""

        key_capture = EncryptionKey(self.ctx)
        key = key_capture.encryption_key()
        if key is None:
            self.flash_text(t("Mnemonic was not encrypted"))
            return
        version = Settings().encryption.version
        i_vector = None
        if version == "AES-CBC":
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Aditional entropy from camera required for AES-CBC mode")
            )
            if not self.prompt(t("Proceed?"), self.ctx.display.bottom_prompt_line):
                self.flash_text(t("Mnemonic was not encrypted"))
                return
            from .capture_entropy import CameraEntropy

            camera_entropy = CameraEntropy(self.ctx)
            entropy = camera_entropy.capture(show_entropy_details=False)
            if entropy is None:
                self.flash_text(t("Mnemonic was not encrypted"))
                return
            i_vector = entropy[:AES_BLOCK_SIZE]
        mnemonic_id = None
        self.ctx.display.clear()
        if self.prompt(
            t(
                "Give this mnemonic a custom ID? Otherwise current fingerprint will be used"
            ),
            self.ctx.display.height() // 2,
        ):
            mnemonic_id = self.capture_from_keypad(
                t("Mnemonic Storage ID"),
                [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1],
            )
        if mnemonic_id in (None, ESC_KEY):
            mnemonic_id = self.ctx.wallet.key.fingerprint_hex_str()

        words = self.ctx.wallet.key.mnemonic
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing ..."))

        from ..encryption import EncryptedQRCode

        encrypted_qr = EncryptedQRCode()
        qr_data = encrypted_qr.create(key, mnemonic_id, words, i_vector)
        del encrypted_qr

        from .qr_view import SeedQRView

        seed_qr_view = SeedQRView(self.ctx, data=qr_data, title=mnemonic_id)
        seed_qr_view.display_qr(allow_export=True)


class LoadEncryptedMnemonic(Page):
    """UI to load encrypted mnemonics stored on flash and Sd card"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def load_from_storage(self, delete_opt=False):
        """Lists all encrypted mnemonics stored is flash and SD card"""
        from ..encryption import MnemonicStorage

        mnemonic_ids_menu = []
        mnemonic_storage = MnemonicStorage()
        has_sd = mnemonic_storage.has_sd_card
        mnemonics = mnemonic_storage.list_mnemonics()
        sd_mnemonics = mnemonic_storage.list_mnemonics(sd_card=True)
        del mnemonic_storage

        for mnemonic_id in mnemonics:
            mnemonic_ids_menu.append(
                (
                    mnemonic_id + "(flash)",
                    lambda m_id=mnemonic_id: self._delete_encrypted_mnemonic(m_id)
                    if delete_opt
                    else self._load_encrypted_mnemonic(m_id),
                )
            )
        if has_sd:
            for mnemonic_id in sd_mnemonics:
                mnemonic_ids_menu.append(
                    (
                        mnemonic_id + "(SD card)",
                        lambda m_id=mnemonic_id: self._delete_encrypted_mnemonic(
                            m_id, sd_card=True
                        )
                        if delete_opt
                        else self._load_encrypted_mnemonic(m_id, sd_card=True),
                    )
                )
        mnemonic_ids_menu.append((t("Back"), lambda: MENU_EXIT))
        submenu = Menu(self.ctx, mnemonic_ids_menu)
        index, status = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return MENU_CONTINUE
        return status

    def _load_encrypted_mnemonic(self, mnemonic_id, sd_card=False):
        """Uses encryption module to load and decrypt a mnemonic"""
        from ..encryption import MnemonicStorage

        key_capture = EncryptionKey(self.ctx)
        key = key_capture.encryption_key()
        if key in (None, "", ESC_KEY):
            self.flash_text(t("Key was not provided"), theme.error_color)
            return MENU_CONTINUE
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing ..."))
        mnemonic_storage = MnemonicStorage()
        try:
            words = mnemonic_storage.decrypt(key, mnemonic_id, sd_card).split()
        except:
            self.flash_text(t("Failed to decrypt"), theme.error_color)
            return MENU_CONTINUE

        if len(words) not in (12, 24):
            self.flash_text(t("Failed to decrypt"), theme.error_color)
            return MENU_CONTINUE
        del mnemonic_storage
        return words

    def _delete_encrypted_mnemonic(self, mnemonic_id, sd_card=False):
        """Deletes a mnemonic"""
        from ..encryption import MnemonicStorage

        mnemonic_storage = MnemonicStorage()
        self.ctx.display.clear()
        if self.prompt(t("Delete %s?") % mnemonic_id, self.ctx.display.height() // 2):
            mnemonic_storage.del_mnemonic(mnemonic_id, sd_card)
            self.ctx.display.clear()
            if sd_card:
                message = t("%s was deleted from SD card") % mnemonic_id
                message += "\n\n"
                message += t(
                    "Fully erase your SD card in another device to ensure data is unrecoverable"
                )
            else:
                message = t("%s was deleted from flash") % mnemonic_id
                message += "\n\n"
                message += t("To ensure data is unrecoverable use Wipe Device feature")
            self.ctx.display.draw_centered_text(message)
            self.ctx.input.wait_for_button()
        del mnemonic_storage
