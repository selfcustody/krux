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
from embit.descriptor import Descriptor
from embit.descriptor.arguments import Key, KeyOrigin
from ...krux_settings import t
from ...qr import FORMAT_NONE
from .. import (
    Page,
    Menu,
    MENU_CONTINUE,
)


class DescriptorCreator(Page):
    """UI to create and export wallet descriptors"""

    def create(self):
        """Create a descriptor from the current wallet key"""
        if self.ctx.wallet is None or self.ctx.wallet.key is None:
            self.flash_error(t("No wallet loaded"))
            return MENU_CONTINUE

        key = self.ctx.wallet.key
        policy = self.ctx.wallet.policy_type

        submenu = Menu(
            self.ctx,
            [
                (t("Single-sig"), self._create_singlesig),
                (t("Watch-only"), self._create_watchonly),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def _create_singlesig(self):
        """Create a single-sig descriptor"""
        key = self.ctx.wallet.key
        network = key.network

        if network == "main":
            prefix = "wpkh"
            coin_type = "0h"
        else:
            prefix = "wpkh"
            coin_type = "1h"

        fingerprint = key.fingerprint_hex_str(True)
        derivation = key.derivation_path.replace("m", fingerprint)
        desc_str = "%s([%s]%s/*)/*" % (prefix, derivation, coin_type)

        return self._show_descriptor(desc_str)

    def _create_watchonly(self):
        """Create a watch-only descriptor"""
        key = self.ctx.wallet.key
        network = key.network

        if network == "main":
            prefix = "wpkh"
            coin_type = "0h"
        else:
            prefix = "wpkh"
            coin_type = "1h"

        fingerprint = key.fingerprint_hex_str(True)
        derivation = key.derivation_path.replace("m", fingerprint)
        desc_str = "%s([%s]%s/*)/*" % (prefix, derivation, coin_type)

        return self._show_descriptor(desc_str)

    def _show_descriptor(self, desc_str):
        """Display and offer export options for a descriptor"""
        info = t("Output Descriptor") + ":\n\n" + desc_str

        while True:
            self.ctx.display.clear()
            info_len = self.ctx.display.draw_hcentered_text(
                info, info_box=True
            )

            from ...display import FONT_HEIGHT, DEFAULT_PADDING
            info_len *= FONT_HEIGHT
            info_len += DEFAULT_PADDING

            menu_items = [
                (
                    t("QR Code"),
                    lambda: self.display_qr_codes(
                        desc_str, FORMAT_NONE, title=t("Descriptor")
                    ),
                ),
                (
                    t("Save to SD card"),
                    (
                        None
                        if not self.has_sd_card()
                        else lambda: self._save_to_sd(desc_str)
                    ),
                ),
            ]

            submenu = Menu(
                self.ctx,
                menu_items,
                offset=info_len,
            )
            index, _ = submenu.run_loop()
            if index == submenu.back_index:
                break

        return MENU_CONTINUE

    def _save_to_sd(self, desc_str):
        """Save descriptor to SD card"""
        from ..file_operations import SaveFile

        save_page = SaveFile(self.ctx)
        save_page.save_file(
            desc_str,
            "descriptor",
            "descriptor",
            t("Descriptor") + ":",
            ".txt",
            save_as_binary=False,
        )
