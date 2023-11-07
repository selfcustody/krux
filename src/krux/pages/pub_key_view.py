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

from .utils import Utils
from ..qr import FORMAT_NONE
from ..krux_settings import t
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
)

from ..sd_card import PUBKEY_FILE_EXTENSION

# to start xpub value without the xpub/zpub/ypub prefix
WALLET_XPUB_START = 4


class PubkeyView(Page):
    """UI to show and export extended public key"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.utils = Utils(self.ctx)

    def public_key(self):
        """Handler for the 'xpub' menu item"""

        def _save_xpub_to_sd(version):
            from .files_operations import SaveFile

            save_page = SaveFile(self.ctx)
            xpub = self.ctx.wallet.key.key_expression(version)
            title = self.ctx.wallet.key.account_pubkey_str(version)[
                :WALLET_XPUB_START
            ].upper()
            save_page.save_file(
                xpub,
                title,
                title,
                title + ":",
                PUBKEY_FILE_EXTENSION,
                save_as_binary=False,
            )

        def _pub_key_text(version):
            pub_text_menu_items = []
            if self.has_sd_card():
                pub_text_menu_items.append(
                    (t("Save to SD card?"), lambda ver=version: _save_xpub_to_sd(ver))
                )
            pub_text_menu_items.append((t("Back"), lambda: MENU_EXIT))
            full_pub_key = self.ctx.wallet.key.account_pubkey_str(version)
            menu_offset = 5 + len(self.ctx.display.to_lines(full_pub_key))
            menu_offset *= self.ctx.display.font_height
            pub_key_menu = Menu(self.ctx, pub_text_menu_items, offset=menu_offset)
            self.ctx.display.clear()
            self.ctx.display.draw_hcentered_text(
                self.ctx.wallet.key.fingerprint_hex_str()
                + "\n\n"
                + self.ctx.wallet.key.derivation_str()
                + "\n\n"
                + full_pub_key,
                offset_y=self.ctx.display.font_height,
                info_box=True,
            )
            pub_key_menu.run_loop()

        def _pub_key_qr(version):
            # TODO: Add menu to offer print and export as image
            title = self.ctx.wallet.key.account_pubkey_str(version)[
                :WALLET_XPUB_START
            ].upper()
            xpub = self.ctx.wallet.key.key_expression(version)
            self.display_qr_codes(xpub, FORMAT_NONE, title)
            self.utils.print_standard_qr(xpub, FORMAT_NONE, title)

        zpub = "Zpub" if self.ctx.wallet.key.multisig else "zpub"
        pub_key_menu_items = []
        for version in [None, self.ctx.wallet.key.network[zpub]]:
            title = self.ctx.wallet.key.account_pubkey_str(version)[
                :WALLET_XPUB_START
            ].upper()
            pub_key_menu_items.append(
                (title + " - " + t("Text"), lambda ver=version: _pub_key_text(ver))
            )
            pub_key_menu_items.append(
                (title + " - " + t("QR Code"), lambda ver=version: _pub_key_qr(ver))
            )
        pub_key_menu_items.append((t("Back"), lambda: MENU_EXIT))
        pub_key_menu = Menu(self.ctx, pub_key_menu_items)
        while True:
            _, status = pub_key_menu.run_loop()
            if status == MENU_EXIT:
                break

        return MENU_CONTINUE
