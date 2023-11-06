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

from . import Page
from ..themes import theme
from ..krux_settings import t, Settings
from ..qr import to_qr_codes, FORMAT_NONE
from ..printers import create_printer


class PrintPage(Page):
    """Printing user interface"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Loading printer.."))
        self.printer = create_printer()

    def _send_qr_to_printer(self, qr_code, i=0, count=1):
        self.ctx.display.clear()
        if Settings().hardware.printer.driver == "cnc/file":
            self.ctx.display.draw_centered_text(t("Exporting to SD card.."))
        else:
            self.ctx.display.draw_centered_text(t("Printing\n%d / %d") % (i + 1, count))

        self.printer.print_qr_code(qr_code)

    def print_qr(self, data, qr_format=FORMAT_NONE, title="", width=33, is_qr=False):
        """Prompts the user to print a QR code in the specified format
        if a printer is connected
        """
        if self.printer is None:
            self.flash_text(t("Printer Driver not set!"), theme.error_color)
            return
        self.ctx.display.clear()
        if title:
            self.printer.print_string(title + "\n\n")
        i = 0
        if is_qr:
            self._send_qr_to_printer(data)
        else:
            for qr_code, count in to_qr_codes(data, width, qr_format):
                if i == count:
                    break
                self._send_qr_to_printer(qr_code, i, count)
                i += 1

    def print_mnemonic_text(self, mnemonic, suffix=""):
        """Prints Mnemonics words as text"""
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(
            t("Printing ..."), self.ctx.display.height() // 2
        )
        self.printer.print_string(t("BIP39") + " " + suffix + "\n\n")
        words = mnemonic.split(" ")
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
            self.printer.print_string(string)
        self.printer.feed(4)
