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

from ...display import FONT_HEIGHT
from ...krux_settings import t, Settings, THERMAL_ADAFRUIT_TXT
from .. import (
    Page,
    Menu,
    MENU_CONTINUE,
)
from ...kboard import kboard


class MnemonicsView(Page):
    """UI to show mnemonic in different formats"""

    def mnemonic(self):
        """Menu with export mnemonic formats"""
        submenu = Menu(
            self.ctx,
            [
                (t("QR Code"), self.qr_code_backup),
                (t("Encrypted"), self.encrypt_mnemonic_menu),
                (t("Other Formats"), self.other_backup_formats),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def qr_code_backup(self):
        """Handler for the 'QR Code Backup' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("Plaintext QR"), self.display_standard_qr),
                ("Compact SeedQR", lambda: self.display_seed_qr(True)),
                ("SeedQR", self.display_seed_qr),
                (t("Encrypted QR Code"), self.encrypt_qr_code),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def other_backup_formats(self):
        """Handler for the 'Other Formats' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (
                    t("Words"),
                    lambda: self.show_mnemonic(
                        self.ctx.wallet.key.mnemonic, t("Mnemonic")
                    ),
                ),
                (t("Numbers"), self.display_mnemonic_numbers),
                ("Stackbit 1248", self.stackbit),
                ("Tinyseed", self.tiny_seed),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def encrypt_mnemonic_menu(self):
        """Handler for Mnemonic > Encrypt Mnemonic menu item"""
        from ..encryption_ui import EncryptMnemonic

        encrypt_mnemonic_menu = EncryptMnemonic(self.ctx)
        return encrypt_mnemonic_menu.encrypt_menu()

    def encrypt_qr_code(self):
        """Handler for Encrypted QR Code menu item"""
        from ..encryption_ui import EncryptMnemonic

        encrypt_qr_code = EncryptMnemonic(self.ctx)
        return encrypt_qr_code.encrypted_qr_code()

    def show_mnemonic(self, mnemonic, suffix="", display_mnemonic=None):
        """Displays only the mnemonic words or indexes"""
        self.display_mnemonic(
            mnemonic, suffix=suffix, display_mnemonic=display_mnemonic
        )
        self.ctx.input.wait_for_button()

        # Avoid printing text on a cnc
        if Settings().hardware.printer.driver == THERMAL_ADAFRUIT_TXT:
            self.ctx.display.clear()
            if self.prompt(
                t("Print?") + "\n\n" + Settings().hardware.printer.driver + "\n\n",
                self.ctx.display.height() // 2,
            ):
                from ..print_page import PrintPage

                print_page = PrintPage(self.ctx)
                mnemonic = display_mnemonic or mnemonic
                print_page.print_mnemonic_text(mnemonic, suffix)
        return MENU_CONTINUE

    def display_mnemonic_numbers(self):
        """Handler for the 'numbers' menu item"""
        from ..utils import Utils
        from .. import BASE_DEC_SUFFIX, BASE_HEX_SUFFIX, BASE_OCT_SUFFIX

        submenu = Menu(
            self.ctx,
            [
                (
                    t("Decimal"),
                    lambda: self.show_mnemonic(
                        self.ctx.wallet.key.mnemonic,
                        BASE_DEC_SUFFIX,
                        Utils.get_mnemonic_numbers(
                            self.ctx.wallet.key.mnemonic, Utils.BASE_DEC
                        ),
                    ),
                ),
                (
                    t("Hexadecimal"),
                    lambda: self.show_mnemonic(
                        self.ctx.wallet.key.mnemonic,
                        BASE_HEX_SUFFIX,
                        Utils.get_mnemonic_numbers(
                            self.ctx.wallet.key.mnemonic, Utils.BASE_HEX
                        ),
                    ),
                ),
                (
                    t("Octal"),
                    lambda: self.show_mnemonic(
                        self.ctx.wallet.key.mnemonic,
                        BASE_OCT_SUFFIX,
                        Utils.get_mnemonic_numbers(
                            self.ctx.wallet.key.mnemonic, Utils.BASE_OCT
                        ),
                    ),
                ),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def display_standard_qr(self):
        """Displays regular words QR code"""
        title = t("Plaintext QR")
        data = self.ctx.wallet.key.mnemonic
        self.display_qr_codes(data, title=title)

        from ..utils import Utils

        utils = Utils(self.ctx)
        utils.print_standard_qr(data, title=title)
        return MENU_CONTINUE

    def display_seed_qr(self, binary=False):
        """Display Seed QR with with different view modes"""

        from ..qr_view import SeedQRView

        seed_qr_view = SeedQRView(self.ctx, binary)
        return seed_qr_view.display_qr()

    def stackbit(self):
        """Displays which numbers 1248 user should punch on 1248 steel card"""
        from ..stack_1248 import Stackbit

        stackbit = Stackbit(self.ctx)
        word_index = 1
        words = self.ctx.wallet.key.mnemonic.split(" ")

        while word_index < len(words):
            y_offset = 2 * FONT_HEIGHT
            for _ in range(6):
                stackbit.export_1248(word_index, y_offset, words[word_index - 1])
                if not kboard.has_minimal_display:
                    y_offset += 3 * FONT_HEIGHT
                else:
                    y_offset += 5 + 2 * FONT_HEIGHT
                word_index += 1
            self.ctx.input.wait_for_button()
            self.ctx.display.clear()
        return MENU_CONTINUE

    def tiny_seed(self):
        """Displays the seed in Tinyseed format"""
        from ..tiny_seed import TinySeed

        tiny_seed = TinySeed(self.ctx)
        tiny_seed.export()

        # Allow to print on thermal printer only
        if (
            Settings().hardware.printer.driver == THERMAL_ADAFRUIT_TXT
            and self.ctx.camera.mode is not None
        ):
            # TinySeed printing requires a camera frame buffer to draw in.
            if self.print_prompt(t("Print Tinyseed?")):
                tiny_seed.print_tiny_seed()
        return MENU_CONTINUE
