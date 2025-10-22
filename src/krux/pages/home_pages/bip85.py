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
from embit import bip85
from ...qr import FORMAT_NONE
from ...sd_card import B64_FILE_EXTENSION
from ...baseconv import base_encode
from ...display import BOTTOM_PROMPT_LINE, FONT_HEIGHT, DEFAULT_PADDING
from ...krux_settings import t
from ...krux_settings import Settings
from .. import (
    Menu,
    Page,
    MENU_CONTINUE,
)

BIP_PWD_APP_INDEX = 707764
DEFAULT_PWD_LEN = "21"
PWD_MIN_LEN = 20
PWD_MAX_LEN = 86


class Bip85(Page):
    """UI to export and load BIP85 entropy"""

    def _derive_mnemonic(self):
        """Derive a BIP85 mnemonic"""
        num_words = self.choose_len_mnemonic()
        if not num_words:
            return MENU_CONTINUE

        from ..utils import Utils

        utils = Utils(self.ctx)
        child_index = ""
        while child_index == "":
            child_index = utils.capture_index_from_keypad(t("Index"))
        if child_index is None:
            return MENU_CONTINUE

        bip85_words = bip85.derive_mnemonic(
            self.ctx.wallet.key.root,
            num_words,
            child_index,
        )
        self.ctx.display.clear()

        from ...key import Key
        from ...themes import theme

        key = Key(
            bip85_words,
            self.ctx.wallet.key.policy_type,
            self.ctx.wallet.key.network,
            script_type=self.ctx.wallet.key.script_type,
        )
        if not Settings().security.hide_mnemonic:
            self.display_mnemonic(
                bip85_words,
                suffix=t("Words"),
                fingerprint=key.fingerprint_hex_str(True),
            )
        else:
            self.ctx.display.draw_centered_text(
                key.fingerprint_hex_str(True), color=theme.highlight_color
            )
        if self.prompt(t("Load?"), BOTTOM_PROMPT_LINE):
            from ...wallet import Wallet

            self.ctx.wallet = Wallet(key)
            self.flash_text(
                t("%s: loaded!") % key.fingerprint_hex_str(True), highlight_prefix=":"
            )

        return MENU_CONTINUE

    def _base64_password_qr(self, code, title):
        """Export BIP85 base64 password as QR"""
        self.display_qr_codes(code, FORMAT_NONE, title=title)

    def _save_b64_pwd_to_sd(self, info):
        from ..file_operations import SaveFile

        save_page = SaveFile(self.ctx)
        title = "BIP85 Password"
        file_name = "BIP85_password"
        save_page.save_file(
            info,
            file_name,
            file_name,
            title + ":",
            B64_FILE_EXTENSION,
            save_as_binary=False,
        )

    def _derive_base64_password(self):
        """Derive a BIP85 base64 password"""
        from ..utils import Utils

        utils = Utils(self.ctx)
        child_index = ""
        while child_index == "":
            child_index = utils.capture_index_from_keypad(t("Index"))
        if child_index is None:
            return MENU_CONTINUE

        # Capture the password length
        pwd_len = ""
        while pwd_len == "":
            pwd_len = utils.capture_index_from_keypad(
                t("Password Length"),
                initial_val=DEFAULT_PWD_LEN,
                range_min=PWD_MIN_LEN,
                range_max=PWD_MAX_LEN,
            )
        if pwd_len is None:
            return MENU_CONTINUE

        entropy = bip85.derive_entropy(
            self.ctx.wallet.key.root,
            BIP_PWD_APP_INDEX,
            [pwd_len, child_index],
        )
        password = base_encode(entropy, 64)
        password = password[:pwd_len]
        info = password
        info += "\n\n" + t("Index") + ": %s" % child_index
        info += "\n" + t("Length:") + " %s" % pwd_len
        while True:
            menu_items = [
                (
                    t("QR Code"),
                    lambda: self._base64_password_qr(password, t("Base64 Password")),
                ),
                (
                    t("Save to SD card"),
                    (
                        None
                        if not self.has_sd_card()
                        else lambda: self._save_b64_pwd_to_sd(info)
                    ),
                ),
            ]
            self.ctx.display.clear()
            info_len = self.ctx.display.draw_hcentered_text(
                info, info_box=True, highlight_prefix=":"
            )
            info_len *= FONT_HEIGHT
            info_len += DEFAULT_PADDING
            submenu = Menu(
                self.ctx,
                menu_items,
                offset=info_len,
            )
            index, _ = submenu.run_loop()
            if index == submenu.back_index:
                break
        return MENU_CONTINUE

    def export(self):
        """Exports BIP85 child mnemonics"""
        submenu = Menu(
            self.ctx,
            [
                (t("BIP39 Mnemonic"), self._derive_mnemonic),
                (t("Base64 Password"), self._derive_base64_password),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE
