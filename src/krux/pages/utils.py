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

from . import Page, DIGITS, ESC_KEY
from ..krux_settings import t
from ..qr import FORMAT_NONE


class Utils(Page):
    """Methods as subpages, shared by other pages"""

    BASE_DEC = 10
    BASE_HEX = 16
    BASE_OCT = 8

    def __init__(self, ctx):
        super().__init__(ctx, None)

    def print_standard_qr(
        self,
        data,
        qr_format=FORMAT_NONE,
        title="",
        width=33,
        is_qr=False,
        check_printer=True,
    ):
        """Loads printer driver and UI"""
        # Only loads printer related modules if needed
        if self.print_prompt(t("Print as QR?"), check_printer):
            from .print_page import PrintPage

            print_page = PrintPage(self.ctx)
            print_page.print_qr(data, qr_format, title, width, is_qr)

    def load_file(self, file_ext="", prompt=True, only_get_filename=False):
        """Load a file from SD card"""
        from ..sd_card import SDHandler

        if self.has_sd_card():
            with SDHandler() as sd:
                self.ctx.display.clear()
                if not prompt or self.prompt(
                    t("Load from SD card?") + "\n\n", self.ctx.display.height() // 2
                ):
                    from .file_manager import FileManager

                    file_manager = FileManager(self.ctx)
                    filename = file_manager.select_file(
                        select_file_handler=file_manager.load_file,
                        file_extension=file_ext,
                    )

                    if filename:
                        filename = filename[4:]  # remove "/sd/" prefix
                        if only_get_filename:
                            return filename, None
                        return filename, sd.read_binary(filename)
        return "", None

    @staticmethod
    def get_mnemonic_numbers(mnemonic: str, base=BASE_DEC):
        """Returns the mnemonic as indexes in decimal, hexadecimal, or octal"""
        from embit.wordlists.bip39 import WORDLIST

        word_numbers = []
        for word in mnemonic.split(" "):
            word_numbers.append(WORDLIST.index(word) + 1)

        if base == Utils.BASE_HEX:
            for i, number in enumerate(word_numbers):
                word_numbers[i] = hex(number)[2:].upper()

        if base == Utils.BASE_OCT:
            for i, number in enumerate(word_numbers):
                word_numbers[i] = oct(number)[2:]

        numbers_str = [str(value) for value in word_numbers]
        return " ".join(numbers_str)

    def display_addr_highlighted(
        self, y_offset, x_offset, line, line_index, highlight, addr_prefix=None
    ):
        """Local helper function to highlight addresses"""
        from ..display import FONT_HEIGHT
        from ..themes import theme
        import lcd

        x_addr_offset = 0
        if addr_prefix is not None:
            x_addr_offset = lcd.string_width_px(addr_prefix)
            line = line[len(addr_prefix) :]

        line = line.split(" ")
        for part in line:
            if highlight:
                self.ctx.display.draw_string(
                    x_offset + x_addr_offset,
                    y_offset + (line_index * (FONT_HEIGHT)),
                    part,
                    theme.highlight_color,
                )
            x_addr_offset += lcd.string_width_px(part + " ")
            highlight = not highlight
        return highlight

    def capture_index_from_keypad(
        self, title, initial_val=None, range_min=0, range_max=None
    ):
        """Reusable capture from keyboard for index number"""

        if range_max is None:
            from embit.bip32 import HARDENED_INDEX

            range_max = HARDENED_INDEX - 1

        val = self.capture_from_keypad(
            title,
            [DIGITS],
            starting_buffer=(str(initial_val) if initial_val is not None else ""),
        )
        if val == ESC_KEY:
            return None

        try:
            val = int(val)
        except:  # Empty input
            return ""

        if val < range_min or val > range_max:
            self.flash_error(
                t("Value %s out of range: [%s, %s]") % (val, range_min, range_max)
            )
            return ""
        return val

    def generate_wallet_info(self, network, policy, script, derivation, is_login=False):
        """Helper to create wallet details infobox"""
        from ..key import (
            Key,
            P2TR,
            TYPE_SINGLESIG,
            TYPE_MULTISIG,
            TYPE_MINISCRIPT,
        )
        from ..key import NAME_SINGLE_SIG, NAME_MULTISIG, NAME_MINISCRIPT

        wallet_info = network + "\n"

        if policy == TYPE_SINGLESIG:
            wallet_info += NAME_SINGLE_SIG
        elif policy == TYPE_MULTISIG:
            wallet_info += NAME_MULTISIG
        elif policy == TYPE_MINISCRIPT:
            if is_login and script == P2TR:
                wallet_info += "TR "
            wallet_info += NAME_MINISCRIPT

        wallet_info += "\n"

        if not is_login:
            wallet_info += str(script).upper() + "\n"

        wallet_info += self.fit_to_line(
            Key.format_derivation(derivation, True), crop_middle=False
        )

        return wallet_info

    @staticmethod
    def get_network_color(network_name: str):
        """Returns the correct theme color to write network"""
        from ..themes import TEST_TXT_COLOR, MAIN_TXT_COLOR

        return MAIN_TXT_COLOR if network_name == "Mainnet" else TEST_TXT_COLOR
