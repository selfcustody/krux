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

import time
from binascii import hexlify
from ..display import DEFAULT_PADDING, FONT_HEIGHT, BOTTOM_PROMPT_LINE
from ..krux_settings import t, Settings
from ..encryption import QR_CODE_ITER_MULTIPLE
from krux import kef
from ..themes import theme
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
    ESC_KEY,
    LETTERS,
    UPPERCASE_LETTERS,
    NUM_SPECIAL_1,
    NUM_SPECIAL_2,
    DIGITS,
)

ENCRYPTION_KEY_MAX_LEN = 200


def decrypt_kef(ctx, data):
    """finds kef-envelope and returns data fully decrypted, else ValueError"""
    from binascii import unhexlify
    from krux.baseconv import base_decode, hint_encodings

    err = "Not decrypted"  # intentionally vague

    # if data is str, assume encoded, look for kef envelope
    kef_envelope = None
    if isinstance(data, str):
        encodings = hint_encodings(data)
        for encoding in encodings:
            as_bytes = None
            if encoding in ("hex", "HEX"):
                try:
                    as_bytes = unhexlify(data)
                except:
                    continue
            elif encoding == 32:
                try:
                    as_bytes = base_decode(data, 32)
                except:
                    continue
            elif encoding == 64:
                try:
                    as_bytes = base_decode(data, 64)
                except:
                    continue
            elif encoding == 43:
                try:
                    as_bytes = base_decode(data, 43)
                except:
                    continue

            if as_bytes:
                kef_envelope = KEFEnvelope(ctx)
                if kef_envelope.parse(as_bytes):
                    break
                kef_envelope = None
                del as_bytes

    # kef_envelope may already be parsed, else do so or fail early
    if kef_envelope is None:
        if not isinstance(data, bytes):
            raise ValueError(err)

        kef_envelope = KEFEnvelope(ctx)
        if not kef_envelope.parse(data):
            raise ValueError(err)

    # unpack as many kef_envelopes as there may be
    while True:
        data = kef_envelope.unseal_ui()
        if data is None:
            # fail if not unsealed
            raise ValueError(err)
        # we may have unsealed another envelope
        kef_envelope = KEFEnvelope(ctx)
        if not kef_envelope.parse(data):
            return data
    raise ValueError(err)


def prompt_for_text_update(
    ctx,
    dflt_value,
    dflt_prompt=None,
    dflt_affirm=True,
    prompt_highlight_prefix="",
    title=None,
    keypads=None,
    esc_prompt=False,
):
    """Clears screen, prompts question, allows for keypad input"""
    if dflt_value and not dflt_prompt:
        dflt_prompt = t("Use current value?") + " " + dflt_value
    ctx.display.clear()
    if dflt_value and dflt_prompt:
        ctx.display.draw_centered_text(
            dflt_prompt, highlight_prefix=prompt_highlight_prefix
        )
        dflt_answer = Page(ctx).prompt("", BOTTOM_PROMPT_LINE)
        if dflt_affirm == dflt_answer:
            return dflt_value
    if not isinstance(keypads, list) or keypads is None:
        keypads = [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2]
    value = Page(ctx).capture_from_keypad(
        title, keypads, starting_buffer=dflt_value, esc_prompt=esc_prompt
    )
    if isinstance(value, str):
        return value
    return dflt_value


class KEFEnvelope(Page):
    """UI to handle KEF-Encryption-Format Envelopes"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.__key = None
        self.__iv = None
        self.label = None
        self.iterations = Settings().encryption.pbkdf2_iterations + (
            int(time.ticks_ms()) % QR_CODE_ITER_MULTIPLE
        )
        self.mode_name = Settings().encryption.version
        self.mode = kef.MODE_NUMBERS[self.mode_name]
        self.iv_len = kef.MODE_IVS.get(self.mode, 0)
        self.version = None
        self.version_name = None
        self.ciphertext = None

    def parse(self, kef_envelope):
        """parses envelope, from kef.wrap()"""
        if self.ciphertext is not None:
            raise ValueError("KEF Envelope already parsed")
        try:
            self.label, self.version, self.iterations, self.ciphertext = kef.unwrap(
                kef_envelope
            )
        except:
            return False
        self.version_name = kef.VERSIONS[self.version]["name"]
        self.mode = kef.VERSIONS[self.version]["mode"]
        self.mode_name = [k for k, v in kef.MODE_NUMBERS.items() if v == self.mode][0]
        return True

    def input_key_ui(self, creating=True):
        """calls ui to gather master key"""
        ui = EncryptionKey(self.ctx)
        self.__key = ui.encryption_key(creating)
        return bool(self.__key)

    def input_mode_ui(self):
        """implements ui to allow user to select KEF mode-of-operation"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            t("Use default Mode?") + " " + self.mode_name, highlight_prefix="?"
        )
        if self.prompt("", BOTTOM_PROMPT_LINE):
            return True
        menu_items = [(k, v) for k, v in kef.MODE_NUMBERS.items() if v is not None]
        idx, _ = Menu(
            self.ctx, [(x[0], lambda: None) for x in menu_items], back_label=None
        ).run_loop()
        self.mode_name, self.mode = menu_items[idx]
        self.iv_len = kef.MODE_IVS.get(self.mode, 0)
        return True

    def input_version_ui(self):
        """implements ui to allow user to select KEF version"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            t("Use default Mode?") + " " + self.mode_name, highlight_prefix="?"
        )
        if self.prompt("", BOTTOM_PROMPT_LINE):
            return True
        menu_items = [
            (v["name"], k)
            for k, v in kef.VERSIONS.items()
            if isinstance(v, dict) and v["mode"] is not None
        ]
        idx, _ = Menu(
            self.ctx, [(x[0], lambda: None) for x in menu_items], back_label=None
        ).run_loop()
        self.version = [v for i, (name, v) in enumerate(menu_items) if i == idx][0]
        self.version_name = kef.VERSIONS[self.version]["name"]
        self.mode = kef.VERSIONS[self.version]["mode"]
        self.mode_name = [k for k, v in kef.MODE_NUMBERS.items() if v == self.mode][0]
        self.iv_len = kef.MODE_IVS.get(self.mode, 0)
        return True

    def input_iterations_ui(self):
        """implements ui to allow user to set key-stretch iterations"""
        curr_value = str(self.iterations)
        dflt_prompt = t("Use default Key iter.?") + " " + curr_value
        title = t("Key iter.") + ": 10K - 510K"
        keypads = [DIGITS]
        iterations = prompt_for_text_update(
            self.ctx, curr_value, dflt_prompt, True, "?", title, keypads
        )
        if QR_CODE_ITER_MULTIPLE <= int(iterations) <= 500000 + QR_CODE_ITER_MULTIPLE:
            self.iterations = int(iterations)
            return True
        return None

    def input_label_ui(
        self,
        dflt_label="",
        dflt_prompt="",
        dflt_affirm=True,
        title=t("Visible Label"),
        keypads=None,
    ):
        """implements ui to allow user to set a KEF label"""
        if dflt_label and not dflt_prompt:
            dflt_prompt = t("Update KEF ID?") + " " + dflt_label
            dflt_affirm = False
        self.label = prompt_for_text_update(
            self.ctx, dflt_label, dflt_prompt, dflt_affirm, "?", title, keypads
        )
        return True

    def input_iv_ui(self):
        """implements ui to allow user to gather entropy from camera for iv"""
        if self.iv_len > 0:
            error_txt = t("Failed gathering camera entropy")
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Additional entropy from camera required for") + " " + self.mode_name
            )
            if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
                self.flash_error(error_txt)
                self.__iv = None
                return None
            from .capture_entropy import CameraEntropy

            camera_entropy = CameraEntropy(self.ctx)
            entropy = camera_entropy.capture(show_entropy_details=False)
            if entropy is None:
                self.flash_error(error_txt)
                self.__iv = None
                return None
            self.__iv = entropy[: self.iv_len]
            return True
        self.__iv = None
        return True

    def public_info_ui(self, kef_envelope=None, prompt_decrypt=False):
        """implements ui to allow user to see public exterior of KEF envelope"""
        if kef_envelope:
            self.parse(kef_envelope)
        elif not self.ciphertext:
            raise ValueError("KEF Envelope not yet parsed")
        try:
            displayable_label = self.label.decode()
        except:
            displayable_label = "0x" + hexlify(self.label).decode()

        public_info = "\n".join(
            [
                t("KEF Encrypted") + " (" + str(len(self.ciphertext)) + " B)",
                self.fit_to_line(displayable_label, t("ID") + ": "),
                t("Version") + ": " + self.version_name,
                t("Key iter.") + ": " + str(self.iterations),
            ]
        )
        self.ctx.display.clear()
        if prompt_decrypt:
            return self.prompt(
                public_info + "\n\n" + t("Decrypt?"), self.ctx.display.height() // 2
            )
        self.ctx.display.draw_hcentered_text(public_info)
        self.ctx.input.wait_for_button()
        return True

    def seal_ui(self, plaintext, override_defaults=False, specific_version=False):
        """implements ui to allow user to seal plaintext inside a KEF envelope"""
        if self.ciphertext:
            raise ValueError("KEF Envelope already sealed")
        if not (self.__key or self.input_key_ui()):
            return None
        if override_defaults:
            if not self.input_iterations_ui():
                return None
            if specific_version:
                if not self.input_version_ui():
                    return None
            else:
                if not self.input_mode_ui():
                    return None
        if self.iv_len:
            if not (self.__iv or self.input_iv_ui()):
                return None
        if override_defaults or not self.label:
            self.input_label_ui(self.label)
        if self.version is None:
            self.version = kef.suggest_versions(plaintext, self.mode_name)[0]
            self.version_name = kef.VERSIONS[self.version]["name"]
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing.."))
        cipher = kef.Cipher(self.__key, self.label, self.iterations)
        self.ciphertext = cipher.encrypt(plaintext, self.version, self.__iv)
        self.__key = None
        self.__iv = None
        return kef.wrap(self.label, self.version, self.iterations, self.ciphertext)

    def unseal_ui(self, kef_envelope=None, prompt_decrypt=True, display_plain=False):
        """implements ui to allow user to unseal a plaintext from a sealed KEF envelope"""
        if kef_envelope:
            if not self.parse(kef_envelope):
                return None
        if not self.ciphertext:
            raise ValueError("KEF Envelope not yet parsed")
        if prompt_decrypt:
            if not self.public_info_ui(prompt_decrypt=prompt_decrypt):
                return None
        if not (self.__key or self.input_key_ui(creating=False)):
            return None
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing.."))
        cipher = kef.Cipher(self.__key, self.label, self.iterations)
        plaintext = cipher.decrypt(self.ciphertext, self.version)
        self.__key = None
        if plaintext is None:
            raise KeyError("Failed to decrypt")
        if display_plain:
            self.ctx.display.clear()
            try:
                self.ctx.display.draw_centered_text(plaintext.decode())
            except:
                self.ctx.display.draw_centered_text("0x" + hexlify(plaintext).decode())
            self.ctx.input.wait_for_button()
        return plaintext


class EncryptionKey(Page):
    """UI to capture an encryption key"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def key_strength(self, key_string):
        """Check the strength of a key."""

        if isinstance(key_string, bytes):
            key_string = hexlify(key_string).decode()

        if len(key_string) < 8:
            return t("Weak")

        # Helper function to check if character is alphanumeric
        def is_alnum(c):
            return ("a" <= c <= "z") or ("A" <= c <= "Z") or ("0" <= c <= "9")

        # Check for presence of character types
        has_upper = any(c.isupper() for c in key_string)
        has_lower = any(c.islower() for c in key_string)
        has_digit = any(c.isdigit() for c in key_string)
        has_special = any(not is_alnum(c) for c in key_string)

        # Count how many character types are present
        score = sum([has_upper, has_lower, has_digit, has_special])

        # Add length score to score
        key_len = len(key_string)
        if key_len >= 12:
            score += 1
        if key_len >= 16:
            score += 1
        if key_len >= 20:
            score += 1
        if key_len >= 40:
            score += 1

        set_len = len(set(key_string))
        if set_len < 6:
            score -= 1
        if set_len < 3:
            score -= 1

        # Determine key strength
        if score >= 4:
            return t("Strong")
        if score >= 3:
            return t("Medium")
        return t("Weak")

    def encryption_key(self, creating=False):
        """Loads and returns an encryption key from keypad or QR code"""
        submenu = Menu(
            self.ctx,
            [
                (t("Type Key"), self.load_key),
                (t("Scan Key QR Code"), self.load_qr_encryption_key),
            ],
            back_label=None,
        )
        _, key = submenu.run_loop()

        try:
            # encryption key may have been encrypted
            decrypted = decrypt_kef(self.ctx, key)
            try:
                # no assumed decodings except for utf8
                decrypted = decrypted.decode()
            except:
                pass
            key = decrypted if decrypted else key
        except:
            pass

        while True:
            if key in (None, "", b"", ESC_KEY, MENU_CONTINUE):
                self.flash_error(t("Failed to load"))
                return None

            self.ctx.display.clear()
            offset_y = DEFAULT_PADDING
            displayable = key if isinstance(key, str) else "0x" + hexlify(key).decode()
            key_lines = self.ctx.display.draw_hcentered_text(
                "{}: {}".format(t("Key"), displayable), offset_y, highlight_prefix=":"
            )

            if creating:
                strength = self.key_strength(key)
                offset_y += (key_lines + 1) * FONT_HEIGHT
                color = theme.error_color if strength == t("Weak") else theme.fg_color
                self.ctx.display.draw_hcentered_text(
                    "{}: {}".format(t("Strength"), strength),
                    offset_y,
                    color,
                    highlight_prefix=":",
                )

            if self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
                return key

            # user did not confirm to proceed
            if not isinstance(key, str):
                return None
            key = self.load_key(key)

    def load_key(self, data=""):
        """Loads and returns a key from keypad"""
        if not isinstance(data, str):
            raise TypeError("load_key() expected str")
        data = self.capture_from_keypad(
            t("Key"),
            [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2],
            starting_buffer=data,
        )
        if len(str(data)) > ENCRYPTION_KEY_MAX_LEN:
            raise ValueError("Maximum length exceeded (%s)" % ENCRYPTION_KEY_MAX_LEN)
        return data

    def load_qr_encryption_key(self):
        """Loads and returns a key from a QR code"""

        from .qr_capture import QRCodeCapture

        qr_capture = QRCodeCapture(self.ctx)
        data, _ = qr_capture.qr_capture_loop()
        if data is None:
            return None
        if len(data) > ENCRYPTION_KEY_MAX_LEN:
            raise ValueError("Maximum length exceeded (%s)" % ENCRYPTION_KEY_MAX_LEN)
        return data


class EncryptMnemonic(Page):
    """UI with mnemonic encryption output options"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.mode_name = Settings().encryption.version

    def encrypt_menu(self):
        """Menu with mnemonic encryption output options"""

        encrypt_outputs_menu = [
            (t("Store on Flash"), self.store_mnemonic_on_memory),
            (
                t("Store on SD Card"),
                (
                    None
                    if not self.has_sd_card()
                    else lambda: self.store_mnemonic_on_memory(True)
                ),
            ),
            (t("Encrypted QR Code"), self.encrypted_qr_code),
        ]
        submenu = Menu(self.ctx, encrypt_outputs_menu)
        _, _ = submenu.run_loop()
        return MENU_CONTINUE

    def _get_user_inputs(self):
        """Ask user for the key, mnemonic_id and i_vector"""

        error_txt = t("Mnemonic was not encrypted")

        key_capture = EncryptionKey(self.ctx)
        key = key_capture.encryption_key(creating=True)
        if key is None:
            self.flash_error(t("Key was not provided"))
            return None

        i_vector = None
        iv_len = kef.MODE_IVS.get(kef.MODE_NUMBERS[self.mode_name], 0)
        if iv_len > 0:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Additional entropy from camera required for") + " " + self.mode_name
            )
            if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
                self.flash_error(error_txt)
                return None
            from .capture_entropy import CameraEntropy

            camera_entropy = CameraEntropy(self.ctx)
            entropy = camera_entropy.capture(show_entropy_details=False)
            if entropy is None:
                self.flash_error(error_txt)
                return None
            i_vector = entropy[:iv_len]

        mnemonic_id = None
        self.ctx.display.clear()
        if not self.prompt(
            t("Use fingerprint as ID?"),
            self.ctx.display.height() // 2,
        ):
            mnemonic_id = self.capture_from_keypad(
                t("Mnemonic ID"),
                [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1],
            )
        if mnemonic_id in (None, ESC_KEY):
            mnemonic_id = self.ctx.wallet.key.fingerprint_hex_str()

        return (key, mnemonic_id, i_vector)

    def store_mnemonic_on_memory(self, sd_card=False):
        """Save encrypted mnemonic on flash or sd_card"""

        user_inputs = self._get_user_inputs()
        if user_inputs is None:
            return
        key, mnemonic_id, i_vector = user_inputs

        from ..encryption import MnemonicStorage

        mnemonic_storage = MnemonicStorage()
        if mnemonic_id in mnemonic_storage.list_mnemonics(sd_card):
            self.flash_error(
                t("ID already exists") + "\n" + t("Encrypted mnemonic was not stored")
            )
            del mnemonic_storage
            return

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing.."))
        words = self.ctx.wallet.key.mnemonic
        if mnemonic_storage.store_encrypted(key, mnemonic_id, words, sd_card, i_vector):
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Encrypted mnemonic stored with ID:") + " " + mnemonic_id,
                highlight_prefix=":",
            )
        else:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Failed to store mnemonic"), theme.error_color
            )
        self.ctx.input.wait_for_button()
        del mnemonic_storage

    def encrypted_qr_code(self):
        """Exports an encryprted mnemonic QR code"""

        user_inputs = self._get_user_inputs()
        if user_inputs is None:
            return
        key, mnemonic_id, i_vector = user_inputs

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing.."))

        from ..encryption import EncryptedQRCode

        encrypted_qr = EncryptedQRCode()
        words = self.ctx.wallet.key.mnemonic
        qr_data = encrypted_qr.create(key, mnemonic_id, words, i_vector)
        version_number = encrypted_qr.version
        del encrypted_qr

        from .qr_view import SeedQRView

        if version_number > 1:
            from ..baseconv import base_encode

            # Convert to base43
            qr_data = base_encode(qr_data, 43)
        seed_qr_view = SeedQRView(self.ctx, data=qr_data, title=mnemonic_id)
        seed_qr_view.display_qr(allow_export=True)


class LoadEncryptedMnemonic(Page):
    """UI to load encrypted mnemonics stored on flash and Sd card"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def load_from_storage(self, remove_opt=False):
        """Lists all encrypted mnemonics stored is flash and SD card"""
        from ..encryption import MnemonicStorage
        from ..settings import THIN_SPACE

        mnemonic_ids_menu = []
        mnemonic_storage = MnemonicStorage()
        mnemonics = mnemonic_storage.list_mnemonics()
        sd_mnemonics = mnemonic_storage.list_mnemonics(sd_card=True)
        del mnemonic_storage

        for mnemonic_id in sorted(mnemonics):
            mnemonic_ids_menu.append(
                (
                    mnemonic_id + " (flash)",
                    lambda m_id=mnemonic_id: (
                        self._remove_encrypted_mnemonic(m_id)
                        if remove_opt
                        else self._load_encrypted_mnemonic(m_id)
                    ),
                )
            )
        for mnemonic_id in sorted(sd_mnemonics):
            mnemonic_ids_menu.append(
                (
                    mnemonic_id + " (SD" + THIN_SPACE + "card)",
                    lambda m_id=mnemonic_id: (
                        self._remove_encrypted_mnemonic(m_id, sd_card=True)
                        if remove_opt
                        else self._load_encrypted_mnemonic(m_id, sd_card=True)
                    ),
                )
            )
        submenu = Menu(self.ctx, mnemonic_ids_menu)
        index, status = submenu.run_loop()
        if index == submenu.back_index:
            return MENU_CONTINUE
        return status

    def _load_encrypted_mnemonic(self, mnemonic_id, sd_card=False):
        """Uses encryption module to load and decrypt a mnemonic"""
        from ..encryption import MnemonicStorage

        error_txt = t("Failed to decrypt")

        key_capture = EncryptionKey(self.ctx)
        key = key_capture.encryption_key()
        if key in (None, "", ESC_KEY):
            self.flash_error(t("Key was not provided"))
            return MENU_CONTINUE
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing.."))
        mnemonic_storage = MnemonicStorage()
        try:
            words = mnemonic_storage.decrypt(key, mnemonic_id, sd_card).split()
        except:
            self.flash_error(error_txt)
            return MENU_CONTINUE

        if len(words) not in (12, 24):
            self.flash_error(error_txt)
            return MENU_CONTINUE
        del mnemonic_storage
        return words

    def _remove_encrypted_mnemonic(self, mnemonic_id, sd_card=False):
        """Deletes a mnemonic"""
        from ..encryption import MnemonicStorage

        mnemonic_storage = MnemonicStorage()
        self.ctx.display.clear()
        if self.prompt(t("Remove %s?") % mnemonic_id, self.ctx.display.height() // 2):
            mnemonic_storage.del_mnemonic(mnemonic_id, sd_card)
            message = t("%s removed.") % mnemonic_id
            message += "\n\n"
            if sd_card:
                message += t(
                    "Fully erase your SD card in another device to ensure data is unrecoverable"
                )
            else:
                message += t("To ensure data is unrecoverable use Wipe Device feature")
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(message)
            self.ctx.input.wait_for_button()
        del mnemonic_storage
