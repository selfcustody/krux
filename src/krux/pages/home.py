# The MIT License (MIT)

# Copyright (c) 2021-2022 Krux contributors

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
import binascii
import gc
import hashlib
import os
import lcd
from .stack_1248 import Stackbit
from .tiny_seed import TinySeed
from embit.wordlists.bip39 import WORDLIST
from ..baseconv import base_encode
from ..display import DEFAULT_PADDING
from ..psbt import PSBTSigner
from ..qr import FORMAT_NONE, FORMAT_PMOFN
from ..wallet import Wallet, parse_address
from ..krux_settings import t
from . import Page, Menu, MENU_CONTINUE, MENU_EXIT
from ..sd_card import SDHandler
from ..input import (
    BUTTON_ENTER,
    BUTTON_PAGE,
    BUTTON_PAGE_PREV,
    BUTTON_TOUCH,
    SWIPE_DOWN,
    SWIPE_RIGHT,
    SWIPE_LEFT,
    SWIPE_UP,
)
import qrcode


class Home(Page):
    """Home is the main menu page of the app"""

    def __init__(self, ctx):
        super().__init__(
            ctx,
            Menu(
                ctx,
                [
                    (t("Mnemonic"), self.mnemonic),
                    (t("Extended Public Key"), self.public_key),
                    (t("Wallet"), self.wallet),
                    (t("Scan Address"), self.scan_address),
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
        if self.ctx.printer is None:
            return MENU_CONTINUE
        self.ctx.display.clear()
        if self.prompt(t("Print?"), self.ctx.display.height() // 2):
            self.ctx.display.clear()
            self.ctx.display.draw_hcentered_text(
                t("Printing ..."), self.ctx.display.height() // 2
            )
            self.ctx.printer.print_string("Seed Words\n")
            words = self.ctx.wallet.key.mnemonic.split(" ")
            lines = len(words) // 3
            for i in range(lines):
                index = i + 1
                string = str(index) + ":" + words[index - 1] + " "
                while len(string) < 10:
                    string += " "
                index += lines
                string += str(index) + ":" + words[index - 1] + " "
                while len(string) < 21:
                    string += " "
                index += lines
                string += str(index) + ":" + words[index - 1] + "\n"
                self.ctx.printer.print_string(string)
            self.ctx.printer.feed(3)
        return MENU_CONTINUE

    def display_standard_qr(self):
        """Displays regular words QR code"""
        self.display_qr_codes(self.ctx.wallet.key.mnemonic, FORMAT_NONE, None)
        self.print_qr_prompt(self.ctx.wallet.key.mnemonic, FORMAT_NONE)
        return MENU_CONTINUE

    def display_seed_qr(self, binary=False):
        """Disables touch and displays compact SeedQR code with grid to help
        drawing"""

        def draw_grided_qr(mode, qr_size):
            """Draws grided QR"""
            if mode > 0:
                self.ctx.display.draw_qr_code(0, code, bright=True)
                if self.ctx.display.width() > 140:
                    grid_size = self.ctx.display.width() // 140
                else:
                    grid_size = 1
            else:
                self.ctx.display.draw_qr_code(0, code)
                grid_size = 0
            grid_offset = self.ctx.display.width() % (qr_size + 2)
            grid_offset //= 2
            grid_pad = self.ctx.display.width() // (qr_size + 2)
            grid_offset += grid_pad
            if mode == 2:
                for i in range(2):
                    line_offset = grid_pad * line
                    self.ctx.display.fill_rectangle(
                        grid_offset,
                        grid_offset + i * grid_pad + line_offset,
                        qr_size * grid_pad + 1,
                        grid_size,
                        lcd.RED,
                    )
                for i in range(qr_size + 1):
                    self.ctx.display.fill_rectangle(
                        grid_offset + i * grid_pad,
                        grid_offset + line_offset,
                        grid_size,
                        grid_pad + 1,
                        lcd.RED,
                    )
            else:
                for i in range(qr_size + 1):
                    self.ctx.display.fill_rectangle(
                        grid_offset,
                        grid_offset + i * grid_pad,
                        qr_size * grid_pad + 1,
                        grid_size,
                        lcd.RED,
                    )
                    self.ctx.display.fill_rectangle(
                        grid_offset + i * grid_pad,
                        grid_offset,
                        grid_size,
                        qr_size * grid_pad + 1,
                        lcd.RED,
                    )

        if binary:
            code, qr_size = self._binary_seed_qr()
            label = "Compact SeedQR"
        else:
            code, qr_size = self._seed_qr()
            label = "SeedQR"
        label += "\nSwipe to change mode"
        if self.ctx.input.touch is not None:
            self.ctx.display.draw_hcentered_text(
                t(label),
                self.ctx.display.qr_offset(),
                color=lcd.WHITE,
            )
        mode = 0
        line = 0
        button = None
        while button not in (SWIPE_DOWN, SWIPE_UP):
            draw_grided_qr(mode, qr_size)
            # # Avoid the need of double click
            # self.ctx.input.buttons_active = True
            button = self.ctx.input.wait_for_button()
            if button in (BUTTON_PAGE, SWIPE_LEFT):  # page, swipe
                mode += 1
                mode %= 3
                line = 0
                # draw_grided_qr(grid_size, qr_size)
            elif button in (BUTTON_PAGE_PREV, SWIPE_RIGHT):  # page, swipe
                mode -= 1
                mode %= 3
                line = 0
            elif button == BUTTON_TOUCH:
                if mode == 0:
                    button = SWIPE_DOWN  # leave
                if mode == 2:  # Lines mode
                    line += 1
                    line %= qr_size
            elif button == BUTTON_ENTER:
                if mode == 2:  # Lines mode
                    line += 1
                    line %= qr_size
                else:
                    button = SWIPE_DOWN  # leave
        if self.ctx.printer is None:
            return MENU_CONTINUE
        self.ctx.display.clear()
        if self.prompt(t("Print to QR?"), self.ctx.display.height() // 2):
            self.ctx.display.clear()
            self.ctx.display.draw_hcentered_text(
                t("Printing ..."), self.ctx.display.height() // 2
            )
            if binary:
                self.ctx.printer.print_string("Compact SeedQR\n\n")
            else:
                self.ctx.printer.print_string("SeedQR\n\n")
            self.ctx.printer.print_qr_code(code)
        return MENU_CONTINUE

    def stackbit(self):
        """Displays which numbers 1248 user should punch on 1248 steel card"""
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
            if self.ctx.input.wait_for_button() == 2:
                if word_index > 12:
                    word_index -= 12
                else:
                    word_index = 1
            self.ctx.display.clear()
        return MENU_CONTINUE

    def tiny_seed(self):
        """Displays the seed in Tiny Seed format"""
        tiny_seed = TinySeed(self.ctx)
        tiny_seed.export()
        if self.ctx.printer is None:
            return MENU_CONTINUE
        if self.prompt(t("Print?"), self.ctx.display.height() // 2):
            tiny_seed.print_tiny_seed()
        return MENU_CONTINUE

    def public_key(self):
        """Handler for the 'xpub' menu item"""
        zpub = "Zpub" if self.ctx.wallet.key.multisig else "zpub"
        for version in [None, self.ctx.wallet.key.network[zpub]]:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                self.ctx.wallet.key.key_expression(version, pretty=True)
            )
            self.ctx.input.wait_for_button()
            xpub = self.ctx.wallet.key.key_expression(version)
            self.display_qr_codes(xpub, FORMAT_NONE, None)
            self.print_qr_prompt(xpub, FORMAT_NONE)
        return MENU_CONTINUE

    def wallet(self):
        """Handler for the 'wallet' menu item"""
        self.ctx.display.clear()
        if not self.ctx.wallet.is_loaded():
            self.ctx.display.draw_centered_text(t("Wallet not found."))
            if self.prompt(t("Load one?"), self.ctx.display.bottom_prompt_line):
                return self._load_wallet()
        else:
            self.display_wallet(self.ctx.wallet)
            wallet_data, qr_format = self.ctx.wallet.wallet_qr()
            self.print_qr_prompt(wallet_data, qr_format)
        return MENU_CONTINUE

    def _seed_qr(self):
        words = self.ctx.wallet.key.mnemonic.split(" ")
        numbers = ""
        for word in words:
            numbers += str("%04d" % WORDLIST.index(word))
        qr_size = 25 if len(words) == 12 else 29
        return qrcode.encode_to_string(numbers), qr_size

    def _binary_seed_qr(self):
        binary_seed = self._to_compact_seed_qr(self.ctx.wallet.key.mnemonic)
        qr_size = 21 if len(binary_seed) == 16 else 25
        return qrcode.encode_to_string(binary_seed), qr_size

    def _to_compact_seed_qr(self, mnemonic):
        mnemonic = mnemonic.split(" ")
        checksum_bits = 8 if len(mnemonic) == 24 else 4
        indexes = [WORDLIST.index(word) for word in mnemonic]
        bitstring = "".join(["{:0>11}".format(bin(index)[2:]) for index in indexes])[
            :-checksum_bits
        ]
        return int(bitstring, 2).to_bytes((len(bitstring) + 7) // 8, "big")

    def _load_wallet(self):
        wallet_data, qr_format = self.capture_qr_code()
        if wallet_data is None:
            self.ctx.display.flash_text(t("Failed to load wallet"), lcd.RED)
            return MENU_CONTINUE

        try:
            wallet = Wallet(self.ctx.wallet.key)
            wallet.load(wallet_data, qr_format)
            self.ctx.display.clear()
            self.display_wallet(wallet, include_qr=False)
            if self.prompt(t("Load?"), self.ctx.display.bottom_prompt_line):
                self.ctx.wallet = wallet
                self.ctx.log.debug(
                    "Wallet descriptor: %s" % self.ctx.wallet.descriptor.to_string()
                )
                self.ctx.display.flash_text(t("Loaded wallet"))
        except Exception as e:
            self.ctx.log.exception("Exception occurred loading wallet")
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Invalid wallet:\n%s") % repr(e), lcd.RED
            )
            self.ctx.input.wait_for_button()
        if self.ctx.wallet.descriptor.key:  # If single sig
            if not self.ctx.wallet.descriptor.key.origin:
                # Blue exports descriptors without a fingerprint
                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(
                    t("Warning:\nIncomplete descriptor"), lcd.RED
                )
                self.ctx.input.wait_for_button()
        return MENU_CONTINUE

    def scan_address(self):
        """Handler for the 'scan address' menu item"""
        data, qr_format = self.capture_qr_code()
        if data is None or qr_format != FORMAT_NONE:
            self.ctx.display.flash_text(t("Failed to load address"), lcd.RED)
            return MENU_CONTINUE

        addr = None
        try:
            addr = parse_address(data)
        except:
            self.ctx.display.flash_text(t("Invalid address"), lcd.RED)
            return MENU_CONTINUE

        self.display_qr_codes(data, qr_format, title=addr)
        self.print_qr_prompt(data, qr_format)

        if self.ctx.wallet.is_loaded() or not self.ctx.wallet.is_multisig():
            self.ctx.display.clear()
            if not self.prompt(
                t("Check that address belongs to this wallet?"),
                self.ctx.display.height() // 2,
            ):
                return MENU_CONTINUE

            found = False
            num_checked = 0
            while not found:
                for recv_addr in self.ctx.wallet.receive_addresses(
                    num_checked, limit=20
                ):
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(
                        t("Checking receive address %d for match..") % num_checked
                    )

                    num_checked += 1

                    found = addr == recv_addr
                    if found:
                        break

                gc.collect()

                if not found:
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(
                        t("Checked %d receive addresses with no matches.") % num_checked
                    )
                    if not self.prompt(
                        t("Try more?"), self.ctx.display.bottom_prompt_line
                    ):
                        break

            self.ctx.display.clear()
            result_message = (
                t("%s\n\nis a valid receive address") % addr
                if found
                else t("%s\n\nwas NOT FOUND in the first %d receive addresses")
                % (addr, num_checked)
            )
            self.ctx.display.draw_centered_text(result_message)
            self.ctx.input.wait_for_button()
        return MENU_CONTINUE

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
        if not self.ctx.wallet.is_loaded():
            self.ctx.display.draw_centered_text(
                t("WARNING:\nWallet not loaded.\n\nSome checks cannot be performed."),
                lcd.WHITE,
            )
            if not self.prompt(t("Proceed?"), self.ctx.display.bottom_prompt_line):
                return MENU_CONTINUE

        data, qr_format = (None, FORMAT_NONE)
        psbt_filename = None
        try:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Checking for SD card"))
            with SDHandler() as sd:
                psbt_filename = next(
                    filter(
                        lambda filename: filename.endswith(".psbt"),
                        os.listdir("/sd"),
                    )
                )
                self.ctx.display.clear()
                self.ctx.display.draw_hcentered_text(
                    t("Found PSBT on SD card:\n%s") % psbt_filename
                )
                if self.prompt(t("Load?"), self.ctx.display.bottom_prompt_line):
                    data = sd.read_binary(psbt_filename)
        except:
            pass

        if data is None:
            psbt_filename = None
            data, qr_format = self.capture_qr_code()

        qr_format = FORMAT_PMOFN if qr_format == FORMAT_NONE else qr_format

        if data is None:
            self.ctx.display.flash_text(t("Failed to load PSBT"), lcd.RED)
            return MENU_CONTINUE

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Loading.."))

        signer = PSBTSigner(self.ctx.wallet, data, qr_format)
        self.ctx.log.debug("Received PSBT: %s" % signer.psbt)

        outputs = signer.outputs()
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text("\n \n".join(outputs))
        if self.prompt(t("Sign?"), self.ctx.display.bottom_prompt_line):
            signer.sign()
            self.ctx.log.debug("Signed PSBT: %s" % signer.psbt)
            try:
                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(t("Checking for SD card"))
                with SDHandler() as sd:
                    self.ctx.display.clear()
                    if self.prompt(
                        t("Save PSBT to SD card?"), self.ctx.display.height() // 2
                    ):
                        psbt_filename = "signed-%s" % (
                            psbt_filename
                            if psbt_filename is not None
                            else "QRCode.psbt"
                        )
                        sd.write_binary(psbt_filename, signer.psbt.serialize())
                        self.ctx.display.flash_text(
                            t("Saved PSBT to SD card:\n%s") % psbt_filename
                        )
            except:
                pass

            signed_psbt, qr_format = signer.psbt_qr()
            signer = None
            gc.collect()
            self.display_qr_codes(signed_psbt, qr_format)
            self.print_qr_prompt(signed_psbt, qr_format, width=45)
        return MENU_CONTINUE

    def sign_message(self):
        """Handler for the 'sign message' menu item"""
        data, qr_format = self.capture_qr_code()
        if data is None or qr_format != FORMAT_NONE:
            self.ctx.display.flash_text(t("Failed to load message"), lcd.RED)
            return MENU_CONTINUE

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

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            t("SHA256:\n%s") % binascii.hexlify(message_hash).decode()
        )
        if not self.prompt(t("Sign?"), self.ctx.display.bottom_prompt_line):
            return MENU_CONTINUE

        sig = self.ctx.wallet.key.sign(message_hash).serialize()

        # Encode sig as base64 string
        encoded_sig = base_encode(sig, 64).decode()
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Signature:\n\n%s") % encoded_sig)
        self.ctx.input.wait_for_button()

        try:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Checking for SD card"))
            with SDHandler() as sd:
                self.ctx.display.clear()
                if self.prompt(
                    t("Save signature to SD card?"), self.ctx.display.height() // 2
                ):
                    sig_filename = "signed-message.sig"
                    sd.write_binary(sig_filename, sig)
                    self.ctx.display.flash_text(
                        t("Saved signature to SD card:\n%s") % sig_filename
                    )
        except:
            pass

        self.display_qr_codes(encoded_sig, qr_format)
        self.print_qr_prompt(encoded_sig, qr_format)

        pubkey = binascii.hexlify(self.ctx.wallet.key.account.sec()).decode()
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Public Key:\n\n%s") % pubkey)
        self.ctx.input.wait_for_button()
        self.display_qr_codes(pubkey, qr_format)
        self.print_qr_prompt(pubkey, qr_format)

        return MENU_CONTINUE

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
                    + xpub[4:7]
                    + ".."
                    + xpub[len(xpub) - 3 : len(xpub)]
                )
            about += "\n".join(xpubs)
        else:
            xpub = wallet.key.xpub()
            about += xpub[4:7] + ".." + xpub[len(xpub) - 3 : len(xpub)]
        if include_qr:
            wallet_data, qr_format = wallet.wallet_qr()
            self.display_qr_codes(wallet_data, qr_format, title=about)
        else:
            self.ctx.display.draw_hcentered_text(about, offset_y=DEFAULT_PADDING)
