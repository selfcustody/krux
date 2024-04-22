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

from .. import (
    Page,
    MENU_CONTINUE,
)
from ...display import DEFAULT_PADDING, BOTTOM_PROMPT_LINE
from ...krux_settings import t
from ...qr import FORMAT_NONE
from ...sd_card import DESCRIPTOR_FILE_EXTENSION, JSON_FILE_EXTENSION
from ...themes import theme


class WalletDescriptor(Page):
    """Page to load and export wallet descriptor"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def wallet(self):
        """Handler for the 'wallet' menu item"""
        self.ctx.display.clear()
        if not self.ctx.wallet.is_loaded():
            self.ctx.display.draw_centered_text(
                t("Wallet output descriptor not found.")
            )
            if self.prompt(t("Load one?"), BOTTOM_PROMPT_LINE):
                return self._load_wallet()
        else:
            self.display_wallet(self.ctx.wallet)
            wallet_data, qr_format = self.ctx.wallet.wallet_qr()
            title = t("Wallet output descriptor")
            from ..utils import Utils

            utils = Utils(self.ctx)
            utils.print_standard_qr(wallet_data, qr_format, title)

            # Try to save the Wallet output descriptor on the SD card
            if self.has_sd_card():
                from ..file_operations import SaveFile

                save_page = SaveFile(self.ctx)
                save_page.save_file(
                    self.ctx.wallet.descriptor.to_string(),
                    self.ctx.wallet.label,
                    self.ctx.wallet.label,
                    title + ":",
                    DESCRIPTOR_FILE_EXTENSION,
                    save_as_binary=False,
                )
        return MENU_CONTINUE

    def _load_wallet(self):
        wallet_data, qr_format = self.capture_qr_code()
        if wallet_data is None:
            # Try to read the wallet output descriptor from a file on the SD card
            qr_format = FORMAT_NONE
            try:
                from ..utils import Utils

                utils = Utils(self.ctx)
                _, wallet_data = utils.load_file(
                    (DESCRIPTOR_FILE_EXTENSION, JSON_FILE_EXTENSION)
                )
            except OSError:
                pass

        if wallet_data is None:
            # Both the camera and the file on SD card failed!
            self.flash_error(t("Failed to load output descriptor"))
            return MENU_CONTINUE

        try:
            from ...wallet import Wallet

            wallet = Wallet(self.ctx.wallet.key)
            wallet.load(wallet_data, qr_format)
            self.ctx.display.clear()
            self.display_wallet(wallet, include_qr=False)
            if self.prompt(t("Load?"), BOTTOM_PROMPT_LINE):
                self.ctx.wallet = wallet
                self.flash_text(t("Wallet output descriptor loaded!"))

                # BlueWallet single sig descriptor without fingerprint
                if (
                    self.ctx.wallet.descriptor.key
                    and not self.ctx.wallet.descriptor.key.origin
                ):
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(
                        t("Warning:") + "\n" + t("Incomplete output descriptor"),
                        theme.error_color,
                    )
                    self.ctx.input.wait_for_button()

        except Exception as e:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Invalid wallet:") + "\n%s" % repr(e), theme.error_color
            )
            self.ctx.input.wait_for_button()

        return MENU_CONTINUE

    def display_wallet(self, wallet, include_qr=True):
        """Displays a wallet, including its label and abbreviated xpubs.
        If include_qr is True, a QR code of the wallet will be shown
        which will contain the same data as was originally loaded, in
        the same QR format
        """
        about = [wallet.label]
        if wallet.is_multisig():
            import binascii

            fingerprints = []
            for i, key in enumerate(wallet.descriptor.keys):
                fingerprints.append(
                    str(i + 1) + ". " + binascii.hexlify(key.fingerprint).decode()
                )
            about.extend(fingerprints)
        else:
            about.append(wallet.key.fingerprint_hex_str())
            xpub = wallet.key.xpub()
            about.append(self.fit_to_line(xpub))

        if not wallet.is_multisig() and include_qr:
            wallet_data, qr_format = wallet.wallet_qr()
            self.display_qr_codes(wallet_data, qr_format, title=about)
        else:
            self.ctx.display.draw_hcentered_text(about, offset_y=DEFAULT_PADDING)

        # If multisig, show loaded wallet again with all XPUB
        if wallet.is_multisig():
            about = [wallet.label]
            xpubs = []
            for i, xpub in enumerate(wallet.policy["cosigners"]):
                xpubs.append(self.fit_to_line(xpub, str(i + 1) + ". "))
            about.extend(xpubs)

            if include_qr:
                self.ctx.input.wait_for_button()
                self.ctx.display.clear()
                self.ctx.display.draw_hcentered_text(about, offset_y=DEFAULT_PADDING)
                self.ctx.input.wait_for_button()

                # Try to show the wallet output descriptor as a QRCode
                try:
                    wallet_data, qr_format = wallet.wallet_qr()
                    self.display_qr_codes(wallet_data, qr_format, title=wallet.label)
                except Exception as e:
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(
                        t("Error:") + "\n%s" % repr(e), theme.error_color
                    )
                    self.ctx.input.wait_for_button()
            else:
                self.ctx.input.wait_for_button()
                self.ctx.display.clear()
                self.ctx.display.draw_hcentered_text(about, offset_y=DEFAULT_PADDING)
