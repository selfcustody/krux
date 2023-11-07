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

import gc
from .utils import Utils
from ..themes import theme
from ..display import DEFAULT_PADDING
from ..psbt import PSBTSigner
from ..qr import FORMAT_NONE, FORMAT_PMOFN
from ..krux_settings import t
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
)
from ..sd_card import (
    PSBT_FILE_EXTENSION,
    SIGNED_FILE_SUFFIX,
    DESCRIPTOR_FILE_EXTENSION,
    JSON_FILE_EXTENSION,
)


class Home(Page):
    """Home is the main menu page of the app"""

    def __init__(self, ctx):
        super().__init__(
            ctx,
            Menu(
                ctx,
                [
                    (t("Mnemonic"), self.mnemonic),
                    (t("Encrypt Mnemonic"), self.encrypt_mnemonic),
                    (t("Extended Public Key"), self.public_key),
                    (t("Wallet Descriptor"), self.wallet),
                    (t("Address"), self.addresses_menu),
                    (t("Sign"), self.sign),
                    (t("Shutdown"), self.shutdown),
                ],
            ),
        )
        self.utils = Utils(self.ctx)

    def mnemonic(self):
        """Handler for the 'mnemonic' menu item"""
        from .mnemonic_view import MnemonicsView

        mnemonics_viewer = MnemonicsView(self.ctx)
        return mnemonics_viewer.mnemonic()

    def encrypt_mnemonic(self):
        """Handler for Mnemonic > Encrypt Mnemonic menu item"""
        from .encryption_ui import EncryptMnemonic

        encrypt_mnemonic_menu = EncryptMnemonic(self.ctx)
        return encrypt_mnemonic_menu.encrypt_menu()

    def public_key(self):
        """Handler for the 'xpub' menu item"""
        from .pub_key_view import PubkeyView

        pubkey_viewer = PubkeyView(self.ctx)
        return pubkey_viewer.public_key()

    def wallet(self):
        """Handler for the 'wallet' menu item"""
        self.ctx.display.clear()
        if not self.ctx.wallet.is_loaded():
            self.ctx.display.draw_centered_text(
                t("Wallet output descriptor not found.")
            )
            if self.prompt(t("Load one?"), self.ctx.display.bottom_prompt_line):
                return self._load_wallet()
        else:
            self.display_wallet(self.ctx.wallet)
            wallet_data, qr_format = self.ctx.wallet.wallet_qr()
            title = t("Wallet output descriptor")
            self.utils.print_standard_qr(wallet_data, qr_format, title)

            # Try to save the Wallet output descriptor on the SD card
            if self.has_sd_card():
                from .files_operations import SaveFile

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
                _, wallet_data = self.utils.load_file(
                    (DESCRIPTOR_FILE_EXTENSION, JSON_FILE_EXTENSION)
                )
            except OSError:
                pass

        if wallet_data is None:
            # Both the camera and the file on SD card failed!
            self.flash_text(t("Failed to load output descriptor"), theme.error_color)
            return MENU_CONTINUE

        try:
            from ..wallet import Wallet

            wallet = Wallet(self.ctx.wallet.key)
            wallet.load(wallet_data, qr_format)
            self.ctx.display.clear()
            self.display_wallet(wallet, include_qr=False)
            if self.prompt(t("Load?"), self.ctx.display.bottom_prompt_line):
                self.ctx.wallet = wallet
                self.ctx.log.debug(
                    "Wallet output descriptor: %s"
                    % self.ctx.wallet.descriptor.to_string()
                )
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
            self.ctx.log.exception("Exception occurred loading wallet")
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Invalid wallet:\n%s") % repr(e), theme.error_color
            )
            self.ctx.input.wait_for_button()

        return MENU_CONTINUE

    def addresses_menu(self):
        """Handler for the 'address' menu item"""
        from .addresses import Addresses

        adresses = Addresses(self.ctx)
        return adresses.addresses_menu()

    def sign(self):
        """Handler for the 'sign' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("PSBT"), self.sign_psbt),
                (t("Message"), self.sign_message),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        index, status = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return MENU_CONTINUE
        return status

    def sign_psbt(self):
        """Handler for the 'sign psbt' menu item"""

        # Warns in case multisig wallet descriptor is not loaded
        if not self.ctx.wallet.is_loaded() and self.ctx.wallet.is_multisig():
            self.ctx.display.draw_centered_text(
                t("Warning:")
                + "\n"
                + t("Wallet output descriptor not found.")
                + "\n\n"
                + t("Some checks cannot be performed.")
            )
            if not self.prompt(t("Proceed?"), self.ctx.display.bottom_prompt_line):
                return MENU_CONTINUE

        # Try to read a PSBT from camera
        psbt_filename = ""
        data, qr_format = self.capture_qr_code()

        if data is None:
            # Try to read a PSBT from a file on the SD card
            qr_format = FORMAT_NONE
            try:
                psbt_filename, data = self.utils.load_file(PSBT_FILE_EXTENSION)
            except OSError:
                pass

        if data is None:
            # Both the camera and the file on SD card failed!
            self.flash_text(t("Failed to load PSBT"), theme.error_color)
            return MENU_CONTINUE

        # PSBT read OK! Will try to sign
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Loading.."))

        # TODO: FIX, FORMAT_UR increases QR Code data by a factor of 4.8 compared to FORMAT_PMOFN!!
        qr_format = FORMAT_PMOFN if qr_format == FORMAT_NONE else qr_format
        signer = PSBTSigner(self.ctx.wallet, data, qr_format)
        self.ctx.log.debug("Received PSBT: %s" % signer.psbt)

        outputs = signer.outputs()
        for message in outputs:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(message)
            self.ctx.input.wait_for_button()

        # memory management
        del data, outputs
        gc.collect()

        # If user confirm, Krux will sign
        if self.prompt(t("Sign?"), self.ctx.display.bottom_prompt_line):
            signer.sign()
            self.ctx.log.debug("Signed PSBT: %s" % signer.psbt)

            qr_signed_psbt, qr_format = signer.psbt_qr()
            serialized_signed_psbt = signer.psbt.serialize()

            # memory management
            del signer
            gc.collect()

            # Try to show the signed PSBT as a QRCode
            title = t("Signed PSBT")
            try:
                self.display_qr_codes(qr_signed_psbt, qr_format)
                self.utils.print_standard_qr(qr_signed_psbt, qr_format, title, width=45)
            except Exception as e:
                self.ctx.log.exception(
                    "Exception occurred in sign_psbt when trying to show the qr_signed_psbt"
                )
                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(
                    t("Error:\n%s") % repr(e), theme.error_color
                )
                self.ctx.input.wait_for_button()

            # memory management
            del qr_signed_psbt
            gc.collect()

            # Try to save the signed PSBT file on the SD card
            if self.has_sd_card():
                from .files_operations import SaveFile

                save_page = SaveFile(self.ctx)
                save_page.save_file(
                    serialized_signed_psbt,
                    "QRCode",
                    psbt_filename,
                    title + ":",
                    PSBT_FILE_EXTENSION,
                    SIGNED_FILE_SUFFIX,
                )
        return MENU_CONTINUE

    def sign_message(self):
        """Handler for the 'sign message' menu item"""
        from .sign_message_ui import SignMessage

        message_signer = SignMessage(self.ctx)
        return message_signer.sign_message()

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
                        t("Error:\n%s") % repr(e), theme.error_color
                    )
                    self.ctx.input.wait_for_button()
            else:
                self.ctx.input.wait_for_button()
                self.ctx.display.draw_hcentered_text(about, offset_y=DEFAULT_PADDING)
