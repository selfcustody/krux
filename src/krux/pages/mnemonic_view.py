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

from .utils import Utils
from ..qr import FORMAT_NONE
from ..krux_settings import t, Settings, THERMAL_ADAFRUIT_TXT
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
)


class MnemonicsView(Page):
    """UI to show mnemonic in different formats"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.utils = Utils(self.ctx)

    def mnemonic(self):
        """Menu with export mnemonic formats"""
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

    def show_mnemonic(self, mnemonic, suffix=""):
        """Displays only the mnemonic words or indexes"""
        self.display_mnemonic(mnemonic, suffix)
        self.ctx.input.wait_for_button()

        # Avoid printing text on a cnc
        if Settings().hardware.printer.driver == THERMAL_ADAFRUIT_TXT:
            self.ctx.display.clear()
            if self.prompt(
                t("Print?\n\n%s\n\n") % Settings().hardware.printer.driver,
                self.ctx.display.height() // 2,
            ):
                from .print_page import PrintPage

                print_page = PrintPage(self.ctx)
                print_page.print_mnemonic_text(mnemonic, suffix)
        return MENU_CONTINUE

    def display_mnemonic_numbers(self):
        """Handler for the 'numbers' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (
                    t("Decimal"),
                    lambda: self.show_mnemonic(
                        Utils.get_mnemonic_numbers(
                            self.ctx.wallet.key.mnemonic, Utils.BASE_DEC
                        ),
                        Utils.BASE_DEC_SUFFIX,
                    ),
                ),
                (
                    t("Hexadecimal"),
                    lambda: self.show_mnemonic(
                        Utils.get_mnemonic_numbers(
                            self.ctx.wallet.key.mnemonic, Utils.BASE_HEX
                        ),
                        Utils.BASE_HEX_SUFFIX,
                    ),
                ),
                (
                    t("Octal"),
                    lambda: self.show_mnemonic(
                        Utils.get_mnemonic_numbers(
                            self.ctx.wallet.key.mnemonic, Utils.BASE_OCT
                        ),
                        Utils.BASE_OCT_SUFFIX,
                    ),
                ),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def display_standard_qr(self):
        """Displays regular words QR code"""
        title = t("Plaintext QR")
        data = self.ctx.wallet.key.mnemonic
        self.display_qr_codes(data, FORMAT_NONE, title)
        self.utils.print_standard_qr(data, FORMAT_NONE, title)
        return MENU_CONTINUE

    def display_seed_qr(self, binary=False):
        """Display Seed QR with with different view modes"""

        from .qr_view import SeedQRView

        seed_qr_view = SeedQRView(self.ctx, binary)
        return seed_qr_view.display_qr()

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
        if Settings().hardware.printer.driver == THERMAL_ADAFRUIT_TXT:
            if self.print_qr_prompt():
                tiny_seed.print_tiny_seed()
        return MENU_CONTINUE
