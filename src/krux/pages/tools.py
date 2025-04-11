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

import uos
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
    ESC_KEY,
    LETTERS,
    UPPERCASE_LETTERS,
    NUM_SPECIAL_1,
    NUM_SPECIAL_2,
)
from .file_manager import SD_ROOT_PATH
from ..format import generate_thousands_separator
from ..sd_card import SDHandler
from ..display import BOTTOM_PROMPT_LINE
from ..krux_settings import t
from ..qr import FORMAT_NONE


class Tools(Page):
    """Krux generic tools"""

    def __init__(self, ctx):
        super().__init__(
            ctx,
            Menu(
                ctx,
                [
                    (t("Check SD Card"), self.sd_check),
                    (t("Print Test QR"), self.print_test),
                    (t("QR Code Tool"), self.qr_tool),
                    (t("Descriptor Addresses"), self.descriptor_addresses),
                    (t("Flash Tools"), self.flash_tools),
                    (t("Remove Mnemonic"), self.rm_stored_mnemonic),
                ],
            ),
        )
        self.ctx = ctx

    def flash_tools(self):
        """Handler for the 'Flash Tools' menu item"""

        from .flash_tools import FlashTools

        flash_tools = FlashTools(self.ctx)
        flash_tools.flash_tools_menu()
        return MENU_CONTINUE

    def sd_check(self):
        """Handler for the 'SD Check' menu item"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Checking for SD card.."))
        try:
            # Check for SD hot-plug
            with SDHandler():
                sd_status = uos.statvfs(SD_ROOT_PATH)
                sd_total_MB = int(sd_status[2] * sd_status[1] / 1024 / 1024)
                sd_free_MB = int(sd_status[4] * sd_status[1] / 1024 / 1024)

                self.ctx.display.clear()
                self.ctx.display.draw_hcentered_text(
                    t("SD card")
                    + "\n\n"
                    + t("Size:")
                    + " "
                    + generate_thousands_separator(sd_total_MB)
                    + " MB"
                    + "\n\n"
                    + t("Used:")
                    + " "
                    + generate_thousands_separator(sd_total_MB - sd_free_MB)
                    + " MB"
                    + "\n\n"
                    + t("Free:")
                    + " "
                    + generate_thousands_separator(sd_free_MB)
                    + " MB",
                    highlight_prefix=":",
                )
                if self.prompt(t("Explore files?"), BOTTOM_PROMPT_LINE):
                    from .file_manager import FileManager

                    file_manager = FileManager(self.ctx)
                    file_manager.select_file(
                        select_file_handler=file_manager.show_file_details
                    )
        except OSError:
            self.flash_error(t("SD card not detected."))

        return MENU_CONTINUE

    def rm_stored_mnemonic(self):
        """Lists and allow deletion of stored mnemonics"""
        from .encryption_ui import LoadEncryptedMnemonic

        encrypted_mnemonics = LoadEncryptedMnemonic(self.ctx)
        while True:
            ret = encrypted_mnemonics.load_from_storage(remove_opt=True)
            if ret == MENU_CONTINUE:
                del encrypted_mnemonics
                return ret

    def print_test(self):
        """Handler for the 'Print Test QR' menu item"""
        title = t("Krux Printer Test QR")
        self.display_qr_codes(title, FORMAT_NONE, title)
        from .print_page import PrintPage

        print_page = PrintPage(self.ctx)
        print_page.print_qr(title, title=title)
        return MENU_CONTINUE

    def qr_tool(self):
        """Handler for the 'QR Code Tool' menu item"""
        qr_tool_menu = [
            (t("Scan a QR"), self.scan_qr),
            (t("New Text QR"), self.create_qr),
            (t("New Encrypted QR"), self.create_encrypted_qr),
        ]
        Menu(self.ctx, qr_tool_menu).run_loop()
        return MENU_CONTINUE

    def scan_qr(self):
        """Handler for the 'Scan a QR' menu item"""
        from .qr_capture import QRCodeCapture

        qr_scanner = QRCodeCapture(self.ctx)
        contents, fmt = qr_scanner.qr_capture_loop()
        print(
            "\nscanned raw contents: {} {}, format: {}".format(
                type(contents), repr(contents), fmt
            )
        )
        if isinstance(contents, str):
            if len(contents) != len(contents.encode()):
                contents = contents.encode("latin-1")
                print("must be on simulator, latin-1")
        print("calling view_contents({} {})...".format(type(contents), repr(contents)))
        return self.view_contents(contents, title="QR Contents")

    def create_qr(self):
        """Handler for the 'New Text QR' menu item"""
        if not self.prompt(
            t("Create QR code from text?"),
            self.ctx.display.height() // 2,
        ):
            return MENU_CONTINUE
        text = self.capture_from_keypad(
            t("Text"), [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2]
        )
        if text in ("", ESC_KEY):
            return MENU_CONTINUE
        return self.view_qr(contents=text, title=t("Text QR Code"))

    def create_encrypted_qr(self):
        """Handler for the 'New Encrypted QR' menu item"""
        if not self.prompt(
            t("Create QR code from text?"),
            self.ctx.display.height() // 2,
        ):
            return MENU_CONTINUE
        text = self.capture_from_keypad(
            t("Text"), [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2]
        )
        if text in ("", ESC_KEY):
            return MENU_CONTINUE

        # from krux.baseconv import base_encode, base_decode
        # text = base_encode(text, 43)
        from .encryption_ui import KEFEnvelope

        kef = KEFEnvelope(self.ctx)
        contents = kef.seal_ui(text.encode(), override_settings=True)
        return self.view_qr(contents=contents, title=t("Encrypted QR Code"))

    def view_qr(self, contents, title):
        """Reusable handler for viewing a QR code"""
        from .qr_view import SeedQRView

        print(contents, title)

        seed_qr_view = SeedQRView(self.ctx, data=contents, title=title)
        seed_qr_view.display_qr(allow_export=True)

        return MENU_CONTINUE

    def view_contents(self, contents, title):
        """Reusable handler for viewing text or binary contents"""

        was_decrypted = False
        while True:
            if isinstance(contents, str):
                break
            from .encryption_ui import KEFEnvelope

            kef = KEFEnvelope(self.ctx)
            decrypted = kef.unseal_ui(contents)
            print("decrypted", decrypted)
            if decrypted is None:
                break
            was_decrypted = True
            contents = decrypted

        if was_decrypted:
            title += ", " + t("decrypted")
        if isinstance(contents, bytes):
            try:
                contents = contents.decode()
            except:
                from binascii import hexlify

                contents = hexlify(contents).decode()
                title += ", " + t("binary hex")

        self.ctx.display.clear()
        print(title, repr(contents))
        self.ctx.display.draw_centered_text(title + ":\n\n" + contents)
        self.ctx.input.wait_for_button()
        return MENU_CONTINUE

    def descriptor_addresses(self):
        """Handler for the 'Descriptor Addresses' menu item"""
        from .home_pages.wallet_descriptor import WalletDescriptor
        from .home_pages.addresses import Addresses
        from ..wallet import Wallet

        self.ctx.wallet = Wallet(None)
        menu_result = WalletDescriptor(self.ctx).wallet()
        if self.ctx.wallet.is_loaded():
            menu_result = Addresses(self.ctx).addresses_menu()
        return menu_result
