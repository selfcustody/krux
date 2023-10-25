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
from ..krux_settings import t
from ..sd_card import SDHandler


class Utils(Page):
    """Methods as subpages, shared by other pages"""

    def __init__(self, ctx):
        super().__init__(ctx, None)

    def print_standard_qr(self, data, qr_format=None, title="", width=33, is_qr=False):
        """Loads printer driver and UI"""
        # Only loads printer related modules if needed
        if self.print_qr_prompt():
            from .print_page import PrintPage

            print_page = PrintPage(self.ctx)
            print_page.print_qr(data, qr_format, title, width, is_qr)

    def load_file(self, file_ext=""):
        """Load a file from SD card"""
        if self.has_sd_card():
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
