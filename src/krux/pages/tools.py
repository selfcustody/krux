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

from ..sd_card import SDHandler
import uos
from ..krux_settings import t
from ..themes import theme
from ..qr import FORMAT_NONE
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
    ESC_KEY,
    LETTERS,
    UPPERCASE_LETTERS,
    NUM_SPECIAL_1,
    NUM_SPECIAL_2,
)
from .files_manager import SD_ROOT_PATH, THOUSANDS_SEPARATOR


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
                    (t("Create QR Code"), self.create_qr),
                    (t("Delete Mnemonic"), self.del_stored_mnemonic),
                    (t("Wipe Device"), self.wipe_device),
                    (t("Back"), lambda: MENU_EXIT),
                ],
            ),
        )
        self.ctx = ctx

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
                    + t("Size: ")
                    + "{:,}".format(sd_total_MB).replace(",", THOUSANDS_SEPARATOR)
                    + " MB"
                    + "\n\n"
                    + t("Used: ")
                    + "{:,}".format(sd_total_MB - sd_free_MB).replace(
                        ",", THOUSANDS_SEPARATOR
                    )
                    + " MB"
                    + "\n\n"
                    + t("Free: ")
                    + "{:,}".format(sd_free_MB).replace(",", THOUSANDS_SEPARATOR)
                    + " MB"
                )
                if self.prompt(
                    t("Explore files?"), self.ctx.display.bottom_prompt_line
                ):
                    from .files_manager import FileManager

                    file_manager = FileManager(self.ctx)
                    file_manager.select_file(
                        select_file_handler=file_manager.show_file_details
                    )
        except OSError:
            self.flash_text(t("SD card not detected"), theme.error_color)

        return MENU_CONTINUE

    def del_stored_mnemonic(self):
        """Lists and allow deletion of stored mnemonics"""
        from .encryption_ui import LoadEncryptedMnemonic

        encrypted_mnemonics = LoadEncryptedMnemonic(self.ctx)
        while True:
            ret = encrypted_mnemonics.load_from_storage(delete_opt=True)
            if ret == MENU_CONTINUE:
                del encrypted_mnemonics
                return ret

    def erase_spiffs(self):
        """Erase all SPIFFS, removing all saved configs and mnemonics"""

        import flash
        from ..firmware import FLASH_SIZE, SPIFFS_ADDR, ERASE_BLOCK_SIZE

        empty_buf = b"\xff" * ERASE_BLOCK_SIZE
        for address in range(SPIFFS_ADDR, FLASH_SIZE, ERASE_BLOCK_SIZE):
            if flash.read(address, ERASE_BLOCK_SIZE) == empty_buf:
                continue
            flash.erase(address, ERASE_BLOCK_SIZE)

    def wipe_device(self):
        """Fully formats SPIFFS memory"""
        self.ctx.display.clear()
        if self.prompt(
            t(
                "Permanently remove all stored encrypted mnemonics and settings from flash?"
            ),
            self.ctx.display.height() // 2,
        ):
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Wiping Device.."))
            self.erase_spiffs()
            # Reboot so default settings take place and SPIFFS is formatted.
            self.ctx.power_manager.reboot()

    def print_test(self):
        """Handler for the 'Print Test QR' menu item"""
        title = t("Krux Printer Test QR")
        self.display_qr_codes(title, FORMAT_NONE, title)
        from .print_page import PrintPage

        print_page = PrintPage(self.ctx)
        print_page.print_qr(title, title=title)
        return MENU_CONTINUE

    def create_qr(self):
        """Handler for the 'Create QR Code' menu item"""
        if self.prompt(
            t("Create QR code from text?"),
            self.ctx.display.height() // 2,
        ):
            text = self.capture_from_keypad(
                t("Text"), [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2]
            )
            if text in ("", ESC_KEY):
                return MENU_CONTINUE

            from .qr_view import SeedQRView

            title = t("Custom QR Code")
            seed_qr_view = SeedQRView(self.ctx, data=text, title=title)
            return seed_qr_view.display_qr(allow_export=True)
        return MENU_CONTINUE
