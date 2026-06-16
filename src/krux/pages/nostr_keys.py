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
import hmac
from embit import ec, bip39
from embit.bech32 import bech32_encode, convertbits, Encoding
from ..krux_settings import t
from ..qr import FORMAT_NONE
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
)

NOSTR_HRP = "nsec"
NOSTR_PUB_HRP = "npub"


class NostrKeys(Page):
    """UI for managing Nostr key pairs"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def derive_nostr_keys(self):
        """Derive Nostr keys from the current wallet mnemonic"""
        if self.ctx.wallet is None or self.ctx.wallet.key is None:
            self.flash_error(t("No wallet loaded"))
            return MENU_CONTINUE

        try:
            mnemonic = self.ctx.wallet.key.mnemonic
            seed = bip39.mnemonic_to_seed(mnemonic)
            priv_bytes = hmac.new(b"nostr", seed, digestmod="sha256").digest()
            priv_key = ec.PrivateKey(priv_bytes)
            pub_key = priv_key.get_public_key()

            nsec_data = convertbits(priv_bytes, 8, 5)
            nsec = bech32_encode(Encoding.BECH32, NOSTR_HRP, nsec_data)
            npub_data = convertbits(pub_key.serialize()[1:], 8, 5)
            npub = bech32_encode(Encoding.BECH32, NOSTR_PUB_HRP, npub_data)
        except Exception as e:
            self.flash_error(str(e))
            return MENU_CONTINUE

        info = t("Public Key") + ":\n" + npub
        info += "\n\n" + t("Private Key") + ":\n" + nsec

        while True:
            self.ctx.display.clear()
            info_len = self.ctx.display.draw_hcentered_text(
                info, info_box=True
            )

            from ..display import FONT_HEIGHT, DEFAULT_PADDING
            info_len *= FONT_HEIGHT
            info_len += DEFAULT_PADDING

            menu_items = [
                (
                    t("QR Code (npub)"),
                    lambda: self.display_qr_codes(
                        npub, FORMAT_NONE, title=t("Nostr Public Key")
                    ),
                ),
                (
                    t("QR Code (nsec)"),
                    lambda: self.display_qr_codes(
                        nsec, FORMAT_NONE, title=t("Nostr Private Key")
                    ),
                ),
                (
                    t("Save to SD card"),
                    (
                        None
                        if not self.has_sd_card()
                        else lambda: self._save_to_sd(npub, nsec)
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

    def _save_to_sd(self, npub, nsec):
        """Save Nostr keys to SD card"""
        from ..file_operations import SaveFile

        content = "Nostr Keys\n\n"
        content += "Public Key (npub):\n" + npub + "\n\n"
        content += "Private Key (nsec):\n" + nsec + "\n"

        save_page = SaveFile(self.ctx)
        save_page.save_file(
            content,
            "nostr_keys",
            "nostr_keys",
            t("Nostr Keys") + ":",
            ".txt",
            save_as_binary=False,
        )

    def nostr_menu(self):
        """Nostr keys menu"""
        submenu = Menu(
            self.ctx,
            [
                (t("Derive Nostr Keys"), self.derive_nostr_keys),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE
