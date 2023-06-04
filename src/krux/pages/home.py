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

import gc
from ..themes import theme
from ..display import DEFAULT_PADDING
from ..psbt import PSBTSigner
from ..qr import FORMAT_NONE, FORMAT_PMOFN
from ..krux_settings import t, Settings, AES_BLOCK_SIZE
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
    ESC_KEY,
    LETTERS,
    UPPERCASE_LETTERS,
    NUM_SPECIAL_1,
)
from ..sd_card import SDHandler

from ..printers import create_printer
from ..printers.cnc import FilePrinter
import board
import uos
import time

STANDARD_MODE = 0
LINE_MODE = 1
ZOOMED_R_MODE = 2
REGION_MODE = 3
TRANSCRIBE_MODE = 4

# to start xpub value without the xpub/zpub/ypub prefix
WALLET_XPUB_START = 4
# len of the xpub to show
WALLET_XPUB_DIGITS = 4


LIST_ADDRESS_QTD = 4  # qtd of address per page
LIST_ADDRESS_DIGITS = 8  # len on large devices per menu item
LIST_ADDRESS_DIGITS_SMALL = 4  # len on small devices per menu item

SCAN_ADDRESS_LIMIT = 20

FILE_SPECIAL = "0123456789()-.[]_~"

PSBT_FILE_SUFFIX = "-signed"
PSBT_FILE_EXTENSION = ".psbt"
MESSAGE_SIG_FILE_EXTENSION = ".sig"
MESSAGE_SIG_FILE_SUFFIX = PSBT_FILE_SUFFIX


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
                    (t("Address"), self.list_address),
                    (t("Sign"), self.sign),
                    (t("Shutdown"), self.shutdown),
                ],
            ),
        )

        # Ensure that the printer was created
        if self.ctx.printer is None:
            try:
                self.ctx.printer = create_printer()
            except:
                self.ctx.log.exception("Exception occurred connecting to printer")

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
        # Avoid printing text on a cnc
        if not isinstance(self.ctx.printer, FilePrinter):
            if self.prompt(
                t("Print?\n\n%s\n\n") % Settings().printer.driver,
                self.ctx.display.height() // 2,
            ):
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
        title = t("Plaintext QR")
        data = self.ctx.wallet.key.mnemonic
        self.display_qr_codes(data, FORMAT_NONE, title, allow_any_btn=True)
        self.print_qr_prompt(data, FORMAT_NONE, title)
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

        if self.ctx.printer is None:
            return MENU_CONTINUE

        # Avoid printing text on a cnc
        if not isinstance(self.ctx.printer, FilePrinter):
            if self.prompt(
                t("Print?\n\n%s\n\n") % Settings().printer.driver,
                self.ctx.display.height() // 2,
            ):
                tiny_seed.print_tiny_seed()
        return MENU_CONTINUE

    def store_mnemonic_on_memory(self, sd_card=False):
        """Save encrypted mnemonic on flash or sd_card"""
        from ..encryption import MnemonicStorage

        from .encryption_key import EncryptionKey

        key_capture = EncryptionKey(self.ctx)
        key = key_capture.encryption_key()
        if key is None:
            self.ctx.display.flash_text(t("Mnemonic was not encrypted"))
            return

        version = Settings().encryption.version
        i_vector = None
        if version == "AES-CBC":
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Aditional entropy from camera required for AES-CBC mode")
            )
            if not self.prompt(t("Proceed?"), self.ctx.display.bottom_prompt_line):
                return
            i_vector = self.capture_camera_entropy()[:AES_BLOCK_SIZE]
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
            self.ctx.display.flash_text(
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

        from .encryption_key import EncryptionKey

        key_capture = EncryptionKey(self.ctx)
        key = key_capture.encryption_key()
        if key is None:
            self.ctx.display.flash_text(t("Mnemonic was not encrypted"))
            return None
        version = Settings().encryption.version
        i_vector = None
        if version == "AES-CBC":
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Aditional entropy from camera required for AES-CBC mode")
            )
            if not self.prompt(t("Proceed?"), self.ctx.display.bottom_prompt_line):
                self.ctx.display.flash_text(t("Mnemonic was not encrypted"))
                return None
            i_vector = self.capture_camera_entropy()[:AES_BLOCK_SIZE]
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
        import qrcode

        encrypted_qr = EncryptedQRCode()
        qr_data = encrypted_qr.create(key, mnemonic_id, words, i_vector)
        code = qrcode.encode_to_string(qr_data)
        del encrypted_qr

        from .qr_view import SeedQRView

        seed_qr_view = SeedQRView(self.ctx, code=code, title=mnemonic_id)
        return seed_qr_view.display_seed_qr()

    def encrypt_mnemonic(self):
        """Handler for Mnemonic > Encrypt Mnemonic menu item"""
        from ..encryption import MnemonicStorage

        encrypt_outputs_menu = []
        encrypt_outputs_menu.append(
            (t("Store on Flash"), self.store_mnemonic_on_memory)
        )
        mnemonic_storage = MnemonicStorage()
        if mnemonic_storage.has_sd_card:
            encrypt_outputs_menu.append(
                (
                    t("Store on SD Card"),
                    lambda: self.store_mnemonic_on_memory(sd_card=True),
                )
            )
        del mnemonic_storage
        encrypt_outputs_menu.append((t("Encrypted QR Code"), self.encrypted_qr_code))
        encrypt_outputs_menu.append((t("Back"), lambda: MENU_EXIT))
        submenu = Menu(self.ctx, encrypt_outputs_menu)
        _, _ = submenu.run_loop()
        return MENU_CONTINUE

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
            title = self.ctx.wallet.key.account_pubkey_str(version)[:4].upper()
            xpub = self.ctx.wallet.key.key_expression(version)
            self.display_qr_codes(xpub, FORMAT_NONE, title, allow_any_btn=True)
            self.print_qr_prompt(xpub, FORMAT_NONE, title)
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
            self.print_qr_prompt(wallet_data, qr_format, t("Wallet output descriptor"))
        return MENU_CONTINUE

    def _load_wallet(self):
        wallet_data, qr_format = self.capture_qr_code()
        if wallet_data is None:
            self.ctx.display.flash_text(
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
                self.ctx.display.flash_text(t("Wallet output descriptor loaded!"))
        except Exception as e:
            self.ctx.log.exception("Exception occurred loading wallet")
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Invalid wallet:\n%s") % repr(e), theme.error_color
            )
            self.ctx.input.wait_for_button()
        if self.ctx.wallet.descriptor.key:  # If single sig
            if not self.ctx.wallet.descriptor.key.origin:
                # Blue exports descriptors without a fingerprint
                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(
                    t("Warning:\nIncomplete output descriptor"), theme.error_color
                )
                self.ctx.input.wait_for_button()
        return MENU_CONTINUE

    def list_address(self):
        """Handler for the 'address' menu item"""
        # only show address for single-key or multisig with wallet output descriptor loaded
        if not self.ctx.wallet.is_loaded() and self.ctx.wallet.is_multisig():
            self.ctx.display.flash_text(
                t("Please load a wallet output descriptor"), theme.error_color
            )
            return MENU_CONTINUE

        submenu = Menu(
            self.ctx,
            [
                ((t("Scan Address"), self.pre_scan_address)),
                (t("Receive Addresses"), self.list_address_type),
                (t("Change Addresses"), lambda: self.list_address_type(1)),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def list_address_type(self, addr_type=0):
        """Handler for the 'receive addresses' or 'change addresses' menu item"""
        # only show address for single-key or multisig with wallet output descriptor loaded
        if self.ctx.wallet.is_loaded() or not self.ctx.wallet.is_multisig():
            custom_start_digits = (
                LIST_ADDRESS_DIGITS + 3
            )  # 3 more because of bc1 address
            custom_end_digts = LIST_ADDRESS_DIGITS
            custom_separator = ". "
            if board.config["type"] == "m5stickv":
                custom_start_digits = (
                    LIST_ADDRESS_DIGITS_SMALL + 3
                )  # 3 more because of bc1 address
                custom_end_digts = LIST_ADDRESS_DIGITS_SMALL
                custom_separator = " "
            start_digits = custom_start_digits

            loading_txt = t("Loading receive address %d..")
            if addr_type == 1:
                loading_txt = t("Loading change address %d..")

            num_checked = 0
            while True:
                items = []
                if num_checked + 1 > LIST_ADDRESS_QTD:
                    items.append(
                        (
                            "%d..%d" % (num_checked - LIST_ADDRESS_QTD, num_checked),
                            lambda: MENU_EXIT,
                        )
                    )

                for addr in self.ctx.wallet.obtain_addresses(
                    num_checked, limit=LIST_ADDRESS_QTD, branch_index=addr_type
                ):
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(loading_txt % (num_checked + 1))

                    if num_checked + 1 > 99:
                        start_digits = custom_start_digits - 1
                    pos_str = str(num_checked + 1)
                    items.append(
                        (
                            pos_str
                            + custom_separator
                            + addr[:start_digits]
                            + ".."
                            + addr[len(addr) - custom_end_digts :],
                            self.show_address,
                            (addr, pos_str + ". " + addr),
                        )
                    )

                    num_checked += 1

                items.append(
                    (
                        "%d..%d" % (num_checked + 1, num_checked + LIST_ADDRESS_QTD),
                        lambda: MENU_EXIT,
                    )
                )
                items.append((t("Back"), lambda: MENU_EXIT))

                submenu = Menu(self.ctx, items)
                stay_on_this_addr_menu = True
                while stay_on_this_addr_menu:
                    index, _ = submenu.run_loop()

                    # Back
                    if index == len(submenu.menu) - 1:
                        del submenu, items
                        gc.collect()
                        return MENU_CONTINUE
                    # Next
                    if index == len(submenu.menu) - 2:
                        stay_on_this_addr_menu = False
                    # Prev
                    if index == 0 and num_checked > LIST_ADDRESS_QTD:
                        stay_on_this_addr_menu = False
                        num_checked -= 2 * LIST_ADDRESS_QTD

        return MENU_CONTINUE

    def show_address(self, addr, title="", qr_format=FORMAT_NONE):
        """Show addr provided as a QRCode"""
        self.display_qr_codes(addr, qr_format, title, allow_any_btn=True)
        self.print_qr_prompt(addr, qr_format, title)
        return MENU_CONTINUE

    def pre_scan_address(self):
        """Handler for the 'scan address' menu item"""
        # only show address for single-key or multisig with wallet output descriptor loaded
        if not self.ctx.wallet.is_loaded() and self.ctx.wallet.is_multisig():
            self.ctx.display.flash_text(
                t("Please load a wallet output descriptor"), theme.error_color
            )
            return MENU_CONTINUE

        submenu = Menu(
            self.ctx,
            [
                (t("Receive"), self.scan_address),
                (t("Change"), lambda: self.scan_address(1)),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def scan_address(self, addr_type=0):
        """Handler for the 'receive' or 'change' menu item"""
        data, qr_format = self.capture_qr_code()
        if data is None or qr_format != FORMAT_NONE:
            self.ctx.display.flash_text(t("Failed to load address"), theme.error_color)
            return MENU_CONTINUE

        addr = None
        try:
            from ..wallet import parse_address

            addr = parse_address(data)
        except:
            self.ctx.display.flash_text(t("Invalid address"), theme.error_color)
            return MENU_CONTINUE

        self.show_address(data, title=addr, qr_format=qr_format)

        if self.ctx.wallet.is_loaded() or not self.ctx.wallet.is_multisig():
            self.ctx.display.clear()
            if not self.prompt(
                t("Check that address belongs to this wallet?"),
                self.ctx.display.height() // 2,
            ):
                return MENU_CONTINUE

            checking_match_txt = t("Checking receive address %d for match..")
            checked_no_match_txt = t("Checked %d receive addresses with no matches.")
            is_valid_txt = t("%s\n\nis a valid receive address!")
            not_found_txt = t("%s\n\nwas NOT FOUND in the first %d receive addresses")
            if addr_type == 1:
                checking_match_txt = t("Checking change address %d for match..")
                checked_no_match_txt = t("Checked %d change addresses with no matches.")
                is_valid_txt = t("%s\n\nis a valid change address!")
                not_found_txt = t(
                    "%s\n\nwas NOT FOUND in the first %d change addresses"
                )

            found = False
            num_checked = 0
            while not found:
                for some_addr in self.ctx.wallet.obtain_addresses(
                    num_checked, limit=SCAN_ADDRESS_LIMIT, branch_index=addr_type
                ):
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(
                        checking_match_txt % (num_checked + 1)
                    )

                    num_checked += 1

                    found = addr == some_addr
                    if found:
                        break

                gc.collect()

                if not found:
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(
                        checked_no_match_txt % num_checked
                    )
                    if not self.prompt(
                        t("Try more?"), self.ctx.display.bottom_prompt_line
                    ):
                        break

            self.ctx.display.clear()
            result_message = (
                is_valid_txt % (str(num_checked) + ". \n\n" + addr)
                if found
                else not_found_txt % (addr, num_checked)
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
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Checking for SD card.."))
            try:
                with SDHandler() as sd:
                    self.ctx.display.clear()
                    if self.prompt(
                        t("Load PSBT from SD card?"), self.ctx.display.height() // 2
                    ):
                        psbt_filename = self.select_file(file_extension=PSBT_FILE_EXTENSION)

                        if psbt_filename:
                            stats = uos.stat(psbt_filename)
                            size = stats[6] / 1024
                            size_deximal_places = str(int(size * 100))[-2:]
                            created = time.localtime(stats[9])
                            modified = time.localtime(stats[8])

                            psbt_filename = psbt_filename[4:]  # remove "/sd/" prefix
                            self.ctx.display.clear()
                            self.ctx.display.draw_hcentered_text(
                                psbt_filename
                                + "\n\n"
                                + t("Size: ")
                                + "{:,}".format(int(size))
                                + "."
                                + size_deximal_places
                                + " KB"
                                + "\n\n"
                                + t("Created: ")
                                + "%s-%s-%s %s:%s"
                                % (
                                    created[0],
                                    created[1],
                                    created[2],
                                    created[3],
                                    created[4],
                                )
                                + "\n\n"
                                + t("Modified: ")
                                + "%s-%s-%s %s:%s"
                                % (
                                    modified[0],
                                    modified[1],
                                    modified[2],
                                    modified[3],
                                    modified[4],
                                )
                            )

                            if self.prompt(
                                t("Load?"), self.ctx.display.bottom_prompt_line
                            ):
                                data = sd.read_binary(psbt_filename)
            except OSError:
                pass

        if data is None:
            # Both the camera and the file on SD card failed!
            self.ctx.display.flash_text(t("Failed to load PSBT"), theme.error_color)
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

            # Show the signed PSBT as a QRCode
            self.display_qr_codes(qr_signed_psbt, qr_format)
            self.print_qr_prompt(qr_signed_psbt, qr_format, t("Signed PSBT"), width=45)

            # memory management
            del qr_signed_psbt
            gc.collect()

            # Try to save the signed PSBT file on the SD card
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Checking for SD card.."))
            try:
                with SDHandler() as sd:
                    # Wait until user defines a filename or select NO on the prompt
                    filename_undefined = True
                    while filename_undefined:
                        self.ctx.display.clear()
                        if self.prompt(
                            t("Save PSBT to SD card?"), self.ctx.display.height() // 2
                        ):
                            psbt_filename, filename_undefined = self._set_filename(
                                psbt_filename,
                                "QRCode",
                                PSBT_FILE_SUFFIX,
                                PSBT_FILE_EXTENSION,
                            )

                            # if user defined a filename and it is ok, save!
                            if not filename_undefined:
                                sd.write_binary(psbt_filename, serialized_signed_psbt)
                                self.ctx.display.clear()
                                self.ctx.display.flash_text(
                                    t("Saved PSBT to SD card:\n%s") % psbt_filename
                                )
                        else:
                            filename_undefined = False
            except OSError:
                pass

        return MENU_CONTINUE

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
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Checking for SD card.."))
            try:
                with SDHandler() as sd:
                    self.ctx.display.clear()
                    if self.prompt(
                        t("Load message from SD card?"), self.ctx.display.height() // 2
                    ):
                        message_filename = self.select_file()

                        if message_filename:
                            self.ctx.display.clear()
                            self.ctx.display.draw_hcentered_text(
                                t("File selected:\n\n%s") % message_filename
                            )
                            message_filename = message_filename[
                                4:
                            ]  # remove "/sd/" prefix
                            if self.prompt(
                                t("Load?"), self.ctx.display.bottom_prompt_line
                            ):
                                data = sd.read_binary(message_filename)
            except OSError:
                pass

        if data is None:
            self.ctx.display.flash_text(t("Failed to load message"), theme.error_color)
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
        self.ctx.display.draw_centered_text(t("Signature:\n\n%s") % encoded_sig)
        self.ctx.input.wait_for_button()

        # Show the base64 signed message as a QRCode
        title = t("Signed Message")
        self.display_qr_codes(encoded_sig, qr_format, title)
        self.print_qr_prompt(encoded_sig, qr_format, title)

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
        self.print_qr_prompt(pubkey, qr_format, title)

        # memory management
        del pubkey
        gc.collect()

        # Try to save the signature file on the SD card
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Checking for SD card.."))
        try:
            with SDHandler() as sd:
                # Wait until user defines a filename or select NO on the prompt
                filename_undefined = True
                while filename_undefined:
                    self.ctx.display.clear()
                    if self.prompt(
                        t("Save signature to SD card?"), self.ctx.display.height() // 2
                    ):
                        message_filename, filename_undefined = self._set_filename(
                            message_filename,
                            "message",
                            MESSAGE_SIG_FILE_SUFFIX,
                            MESSAGE_SIG_FILE_EXTENSION,
                        )

                        # if user defined a filename and it is ok, save!
                        if not filename_undefined:
                            sd.write_binary(message_filename, sig)
                            self.ctx.display.clear()
                            self.ctx.display.flash_text(
                                t("Saved signature to SD card:\n%s") % message_filename
                            )
                    else:
                        filename_undefined = False
        except OSError:
            pass

        return MENU_CONTINUE

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
                    t("Filename %s exists on SD card, overwrite?") % curr_filename,
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
