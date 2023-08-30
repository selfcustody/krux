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
from ..themes import theme
from ..display import DEFAULT_PADDING
from ..psbt import PSBTSigner
from ..qr import FORMAT_NONE, FORMAT_PMOFN
from ..krux_settings import t, Settings, THERMAL_ADAFRUIT_TXT
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
    ESC_KEY,
    LETTERS,
    UPPERCASE_LETTERS,
)
from ..sd_card import SDHandler

# to start xpub value without the xpub/zpub/ypub prefix
WALLET_XPUB_START = 4
# len of the xpub to show
WALLET_XPUB_DIGITS = 4

FILE_SPECIAL = "0123456789()-.[]_~"

PSBT_FILE_SUFFIX = "-signed"
PSBT_FILE_EXTENSION = ".psbt"
PUBKEY_FILE_EXTENSION = ".pub"
SIGNATURE_FILE_EXTENSION = ".sig"
SIGNATURE_FILE_SUFFIX = PSBT_FILE_SUFFIX


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

    def mnemonic(self):
        """Handler for the 'mnemonic' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("Words"), self.display_mnemonic_words),
                (t("Plaintext QR"), self.display_standard_qr),
                (t("Compact SeedQR"), lambda: self.display_seed_qr(True)),
                (t("SeedQR"), self.display_seed_qr),
                (t("Stackbit 1248"), self.stackbit),
                (t("Tiny Seed"), self.tiny_seed),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def display_mnemonic_words(self):
        """Displays only the mnemonic words"""
        self.display_mnemonic(self.ctx.wallet.key.mnemonic)
        self.ctx.input.wait_for_button()

        # Avoid printing text on a cnc
        if Settings().printer.driver == THERMAL_ADAFRUIT_TXT:
            self.ctx.display.clear()
            if self.prompt(
                t("Print?\n\n%s\n\n") % Settings().printer.driver,
                self.ctx.display.height() // 2,
            ):
                from .print_page import PrintPage

                print_page = PrintPage(self.ctx)
                print_page.print_mnemonic_text()
        return MENU_CONTINUE

    def display_standard_qr(self):
        """Displays regular words QR code"""
        title = t("Plaintext QR")
        data = self.ctx.wallet.key.mnemonic
        self.display_qr_codes(data, FORMAT_NONE, title)
        self.print_standard_qr(data, FORMAT_NONE, title)
        return MENU_CONTINUE

    def display_seed_qr(self, binary=False):
        """Display Seed QR with with different view modes"""

        from .qr_view import SeedQRView

        seed_qr_view = SeedQRView(self.ctx, binary)
        return seed_qr_view.display_seed_qr()

    def stackbit(self):
        """Displays which numbers 1248 user should punch on 1248 steel card"""
        from .stack_1248 import Stackbit

        stackbit = Stackbit(self.ctx)
        word_index = 1
        words = self.ctx.wallet.key.mnemonic.split(" ")

        while word_index < len(words):
            y_offset = 2 * self.ctx.display.font_height
            for _ in range(6):
                stackbit.export_1248(word_index, y_offset, words[word_index - 1])
                if self.ctx.display.height() > 240:
                    y_offset += 3 * self.ctx.display.font_height
                else:
                    y_offset += 5 + 2 * self.ctx.display.font_height
                word_index += 1
            self.ctx.input.wait_for_button()

            # removed the hability to go back in favor or the Krux UI patter (always move forward)
            # if self.ctx.input.wait_for_button() == BUTTON_PAGE_PREV:
            #     if word_index > 12:
            #         word_index -= 12
            #     else:
            #         word_index = 1
            self.ctx.display.clear()
        return MENU_CONTINUE

    def tiny_seed(self):
        """Displays the seed in Tiny Seed format"""
        from .tiny_seed import TinySeed

        tiny_seed = TinySeed(self.ctx)
        tiny_seed.export()

        # Allow to print on thermal printer only
        if Settings().printer.driver == THERMAL_ADAFRUIT_TXT:
            if self.print_qr_prompt():
                tiny_seed.print_tiny_seed()
        return MENU_CONTINUE

    def encrypt_mnemonic(self):
        """Handler for Mnemonic > Encrypt Mnemonic menu item"""
        from .encryption_ui import EncryptMnemonic

        encrypt_mnemonic_menu = EncryptMnemonic(self.ctx)
        return encrypt_mnemonic_menu.encrypt_menu()

    def public_key(self):
        """Handler for the 'xpub' menu item"""
        zpub = "Zpub" if self.ctx.wallet.key.multisig else "zpub"
        for version in [None, self.ctx.wallet.key.network[zpub]]:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                self.ctx.wallet.key.fingerprint_hex_str(True)
                + "\n\n"
                + self.ctx.wallet.key.derivation_str(True)
                + "\n\n"
                + self.ctx.wallet.key.account_pubkey_str(version)
            )
            self.ctx.input.wait_for_button()

            # title receives first 4 chars (ex: XPUB)
            title = self.ctx.wallet.key.account_pubkey_str(version)[
                :WALLET_XPUB_START
            ].upper()
            xpub = self.ctx.wallet.key.key_expression(version)
            self.display_qr_codes(xpub, FORMAT_NONE, title)
            self.print_standard_qr(xpub, FORMAT_NONE, title)

            # Try to save the XPUB file on the SD card
            try:
                self._save_file(
                    xpub,
                    title,
                    title,
                    title + ":",
                    PUBKEY_FILE_EXTENSION,
                    save_as_binary=False,
                )
            except OSError:
                pass

        return MENU_CONTINUE

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
            self.print_standard_qr(
                wallet_data, qr_format, t("Wallet output descriptor")
            )
        return MENU_CONTINUE

    def _load_wallet(self):
        wallet_data, qr_format = self.capture_qr_code()
        if wallet_data is None:
            self.flash_text(
                t("Failed to load output descriptor"), theme.error_color
            )
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
                        t("Warning:\nIncomplete output descriptor"), theme.error_color
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
        adresses.addresses_menu()

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
                t(
                    """Warning:\nWallet output descriptor not found.\n\n
                    Some checks cannot be performed."""
                )
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
                psbt_filename, data = self._load_file(PSBT_FILE_EXTENSION)
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
                self.print_standard_qr(qr_signed_psbt, qr_format, title, width=45)
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
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Checking for SD card.."))
            try:
                self._save_file(
                    serialized_signed_psbt,
                    "QRCode",
                    psbt_filename,
                    title + ":",
                    PSBT_FILE_EXTENSION,
                    PSBT_FILE_SUFFIX,
                )
            except OSError:
                pass

        return MENU_CONTINUE

    def _load_file(self, file_ext=""):
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Checking for SD card.."))
        with SDHandler() as sd:
            self.ctx.display.clear()
            if self.prompt(
                t("Load from SD card?") + "\n\n", self.ctx.display.height() // 2
            ):
                from .files_manager import FileManager

                file_manager = FileManager(self.ctx)
                filename = file_manager.select_file(file_extension=file_ext)

                if filename:
                    filename = file_manager.display_file(filename)

                    if self.prompt(t("Load?"), self.ctx.display.bottom_prompt_line):
                        return filename, sd.read_binary(filename)
        return "", None

    def sign_message(self):
        """Handler for the 'sign message' menu item"""

        import binascii
        import hashlib
        from ..baseconv import base_encode

        # Try to read a message from camera
        message_filename = ""
        data, qr_format = self.capture_qr_code()

        if data is None:
            # Try to read a message from a file on the SD card
            qr_format = FORMAT_NONE
            try:
                message_filename, data = self._load_file()
            except OSError:
                pass

        if data is None:
            self.flash_text(t("Failed to load message"), theme.error_color)
            return MENU_CONTINUE

        # message read OK!
        data = data.encode() if isinstance(data, str) else data

        message_hash = None
        if len(data) == 32:
            # It's a sha256 hash already
            message_hash = data
        else:
            if len(data) == 64:
                # It may be a hex-encoded sha256 hash
                try:
                    message_hash = binascii.unhexlify(data)
                except:
                    pass
            if message_hash is None:
                # It's a message, so compute its sha256 hash
                message_hash = hashlib.sha256(data).digest()

        # memory management
        del data
        gc.collect()

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            t("SHA256:\n%s") % binascii.hexlify(message_hash).decode()
        )
        if not self.prompt(t("Sign?"), self.ctx.display.bottom_prompt_line):
            return MENU_CONTINUE

        # User confirmed to sign!
        sig = self.ctx.wallet.key.sign(message_hash).serialize()

        # Encode sig as base64 string
        encoded_sig = base_encode(sig, 64).decode()
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Signature") + ":\n\n%s" % encoded_sig)
        self.ctx.input.wait_for_button()

        # Show the base64 signed message as a QRCode
        title = t("Signed Message")
        self.display_qr_codes(encoded_sig, qr_format, title)
        self.print_standard_qr(encoded_sig, qr_format, title)

        # memory management
        del encoded_sig
        gc.collect()

        # Show the public key as a QRCode
        pubkey = binascii.hexlify(self.ctx.wallet.key.account.sec()).decode()
        self.ctx.display.clear()

        title = t("Hex Public Key")
        self.ctx.display.draw_centered_text(title + ":\n\n%s" % pubkey)
        self.ctx.input.wait_for_button()

        # Show the public key in hexadecimal format as a QRCode
        self.display_qr_codes(pubkey, qr_format, title)
        self.print_standard_qr(pubkey, qr_format, title)

        # memory management
        gc.collect()

        # Try to save the signature file on the SD card
        try:
            self._save_file(
                sig,
                "message",
                message_filename,
                t("Signature") + ":",
                SIGNATURE_FILE_EXTENSION,
                SIGNATURE_FILE_SUFFIX,
            )
        except OSError:
            pass

        # Try to save the public key on the SD card
        try:
            self._save_file(
                pubkey, "pubkey", "", title + ":", PUBKEY_FILE_EXTENSION, "", False
            )
        except OSError:
            pass

        return MENU_CONTINUE

    def _save_file(
        self,
        data,
        empty_name,
        filename="",
        file_description="",
        file_extension="",
        file_suffix="",
        save_as_binary=True,
    ):
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Checking for SD card.."))
        with SDHandler() as sd:
            # Wait until user defines a filename or select NO on the prompt
            filename_undefined = True
            while filename_undefined:
                self.ctx.display.clear()
                if self.prompt(
                    file_description + "\n" + t("Save to SD card?") + "\n\n",
                    self.ctx.display.height() // 2,
                ):
                    filename, filename_undefined = self._set_filename(
                        filename,
                        empty_name,
                        file_suffix,
                        file_extension,
                    )

                    # if user defined a filename and it is ok, save!
                    if not filename_undefined:
                        if save_as_binary:
                            sd.write_binary(filename, data)
                        else:
                            sd.write(filename, data)
                        self.ctx.display.clear()
                        self.flash_text(
                            t("Saved to SD card:\n%s") % filename
                        )
                else:
                    filename_undefined = False

    def _set_filename(
        self, curr_filename="", empty_filename="some_file", suffix="", file_extension=""
    ):
        """Helper to set the filename based on a suggestion and the user input"""
        started_filename = curr_filename
        filename_undefined = True

        # remove the file_extension if exists
        curr_filename = (
            curr_filename[: len(curr_filename) - len(file_extension)]
            if curr_filename.endswith(file_extension)
            else curr_filename
        )

        # remove the suffix if exists (because we will add it later)
        curr_filename = (
            curr_filename[: len(curr_filename) - len(suffix)]
            if curr_filename.endswith(suffix)
            else curr_filename
        )

        curr_filename = self.capture_from_keypad(
            t("Filename"),
            [LETTERS, UPPERCASE_LETTERS, FILE_SPECIAL],
            starting_buffer=("%s" + suffix) % curr_filename
            if curr_filename
            else empty_filename + suffix,
        )

        # Verify if user defined a filename and it is not just dots
        if (
            curr_filename
            and curr_filename != ESC_KEY
            and not all(c in "." for c in curr_filename)
        ):
            # add the extension ".psbt"
            curr_filename = (
                curr_filename
                if curr_filename.endswith(file_extension)
                else curr_filename + file_extension
            )
            # check and warn for overwrite filename
            # add the "/sd/" prefix
            if SDHandler.file_exists("/sd/" + curr_filename):
                self.ctx.display.clear()
                if self.prompt(
                    t("Filename %s exists on SD card, overwrite?") % curr_filename
                    + "\n\n",
                    self.ctx.display.height() // 2,
                ):
                    filename_undefined = False
            else:
                filename_undefined = False

        if curr_filename == ESC_KEY:
            curr_filename = started_filename

        return (curr_filename, filename_undefined)

    def display_wallet(self, wallet, include_qr=True):
        """Displays a wallet, including its label and abbreviated xpubs.
        If include_qr is True, a QR code of the wallet will be shown
        which will contain the same data as was originally loaded, in
        the same QR format
        """
        about = wallet.label + "\n"
        if wallet.is_multisig():
            xpubs = []
            for i, xpub in enumerate(wallet.policy["cosigners"]):
                xpubs.append(
                    str(i + 1)
                    + ". "
                    + xpub[WALLET_XPUB_START : WALLET_XPUB_START + WALLET_XPUB_DIGITS]
                    + ".."
                    + xpub[len(xpub) - WALLET_XPUB_DIGITS :]
                )
            about += "\n".join(xpubs)
        else:
            xpub = wallet.key.xpub()
            about += (
                xpub[WALLET_XPUB_START : WALLET_XPUB_START + WALLET_XPUB_DIGITS]
                + ".."
                + xpub[len(xpub) - WALLET_XPUB_DIGITS :]
            )
        if include_qr:
            wallet_data, qr_format = wallet.wallet_qr()
            self.display_qr_codes(wallet_data, qr_format, title=about)
        else:
            self.ctx.display.draw_hcentered_text(about, offset_y=DEFAULT_PADDING)

    def print_standard_qr(self, data, qr_format, title="", width=33):
        """Loads printer driver and UI"""
        if self.print_qr_prompt():
            from .print_page import PrintPage

            print_page = PrintPage(self.ctx)
            print_page.print_qr(data, qr_format, title, width)
