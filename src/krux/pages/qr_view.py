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

import qrcode
from embit.wordlists.bip39 import WORDLIST
from . import Page
from ..themes import theme, WHITE, BLACK
from ..krux_settings import t, Settings
from ..qr import get_size
from ..display import DEFAULT_PADDING
from . import MENU_CONTINUE
from ..printers.cnc import FilePrinter
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

STANDARD_MODE = 0
LINE_MODE = 1
ZOOMED_R_MODE = 2
REGION_MODE = 3
TRANSCRIBE_MODE = 4


class SeedQRView(Page):
    """Tools to visualize and transcript Seed QRs"""

    def __init__(self, ctx, binary=False, code=None, title=None):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.binary = binary
        if code:
            self.code = code
            self.title = title
        else:
            if self.binary:
                self.title = t("Compact SeedQR")
                self.code = self._binary_seed_qr()
            else:
                self.title = t("SeedQR")
                self.code = self._seed_qr()
        self.qr_size = get_size(self.code)
        self.region_size = 7 if self.qr_size == 21 else 5
        self.columns = (self.qr_size + self.region_size - 1) // self.region_size
        self.lr_index = 0

    def _seed_qr(self):
        words = self.ctx.wallet.key.mnemonic.split(" ")
        numbers = ""
        for word in words:
            numbers += str("%04d" % WORDLIST.index(word))
        # qr_size = 25 if len(words) == 12 else 29
        return qrcode.encode_to_string(numbers)  # , qr_size

    def _binary_seed_qr(self):
        binary_seed = self._to_compact_seed_qr(self.ctx.wallet.key.mnemonic)
        # qr_size = 21 if len(binary_seed) == 16 else 25
        return qrcode.encode_to_string(binary_seed)  # , qr_size

    def _to_compact_seed_qr(self, mnemonic):
        mnemonic = mnemonic.split(" ")
        checksum_bits = 8 if len(mnemonic) == 24 else 4
        indexes = [WORDLIST.index(word) for word in mnemonic]
        bitstring = "".join(["{:0>11}".format(bin(index)[2:]) for index in indexes])[
            :-checksum_bits
        ]
        return int(bitstring, 2).to_bytes((len(bitstring) + 7) // 8, "big")

    def highlight_qr_region(self, code, region=(0, 0, 0, 0), zoom=False):
        """Draws in white a highlighted region of the QR code"""
        reg_x, reg_y, reg_width, reg_height = region
        size, code = self.ctx.display.add_qr_frame(code)
        max_width = self.ctx.display.width()
        if zoom:
            max_width -= DEFAULT_PADDING
            if size == 23:  # 21 + 2(frame)
                qr_size = 7
            else:
                qr_size = 5
            offset_x = 0
            offset_y = 0
        else:
            qr_size = size
            offset_x = reg_x + 1
            offset_y = reg_y + 1

        scale = max_width // qr_size
        qr_width = qr_size * scale
        offset = (self.ctx.display.width() - qr_width) // 2
        for y in range(reg_height):  # vertical blocks loop
            for x in range(reg_width):  # horizontal blocks loop
                xy_index = (reg_y + y + 1) * (size + 1)
                xy_index += reg_x + x + 1
                if code[xy_index] == "0":
                    self.ctx.display.fill_rectangle(
                        offset + (offset_x + x) * scale,
                        offset + (offset_y + y) * scale,
                        scale,
                        scale,
                        WHITE,
                    )
                else:
                    self.ctx.display.fill_rectangle(
                        offset + (offset_x + x) * scale,
                        offset + (offset_y + y) * scale,
                        scale,
                        scale,
                        BLACK,
                    )

    def _region_legend(self, row, column):
        region_char = chr(65 + row)
        self.ctx.display.draw_hcentered_text(
            t("Region: ") + region_char + str(column + 1),
            self.ctx.display.qr_offset(),
            color=theme.highlight_color,
        )

    def draw_grided_qr(self, mode):
        """Draws grided QR"""
        self.ctx.display.clear()
        if self.ctx.display.width() > 140:
            grid_size = self.ctx.display.width() // 140
        else:
            grid_size = 1
        grid_offset = self.ctx.display.width() % (self.qr_size + 2)
        grid_offset //= 2
        grid_pad = self.ctx.display.width() // (self.qr_size + 2)
        grid_offset += grid_pad
        if mode == STANDARD_MODE:
            if theme.bg_color == WHITE:
                self.ctx.display.draw_qr_code(0, self.code, light_color=WHITE)
            else:
                self.ctx.display.draw_qr_code(0, self.code)
        elif mode == LINE_MODE:
            self.ctx.display.draw_qr_code(
                0, self.code, light_color=theme.disabled_color
            )
            self.highlight_qr_region(
                self.code, region=(0, self.lr_index, self.qr_size, 1)
            )
            line_offset = grid_pad * self.lr_index
            for i in range(2):
                self.ctx.display.fill_rectangle(
                    grid_offset,
                    grid_offset + i * grid_pad + line_offset,
                    self.qr_size * grid_pad + 1,
                    grid_size,
                    theme.highlight_color,
                )
            for i in range(self.qr_size + 1):
                self.ctx.display.fill_rectangle(
                    grid_offset + i * grid_pad,
                    grid_offset + line_offset,
                    grid_size,
                    grid_pad + 1,
                    theme.highlight_color,
                )
            self.ctx.display.draw_hcentered_text(
                t("Line: ") + str(self.lr_index + 1),
                self.ctx.display.qr_offset(),
                color=theme.highlight_color,
            )
        elif mode == ZOOMED_R_MODE:
            max_width = self.ctx.display.width() - DEFAULT_PADDING
            zoomed_grid_pad = max_width // self.region_size
            zoomed_grid_offset = (
                self.ctx.display.width() - self.region_size * zoomed_grid_pad
            )
            zoomed_grid_offset //= 2
            row = self.lr_index // self.columns
            column = self.lr_index % self.columns
            self.highlight_qr_region(
                self.code,
                region=(
                    column * self.region_size,
                    (row) * self.region_size,
                    self.region_size,
                    self.region_size,
                ),
                zoom=True,
            )
            for i in range(self.region_size + 1):
                self.ctx.display.fill_rectangle(
                    zoomed_grid_offset,
                    zoomed_grid_offset + i * zoomed_grid_pad,
                    self.region_size * zoomed_grid_pad + 1,
                    grid_size,
                    theme.highlight_color,
                )
            for i in range(self.region_size + 1):
                self.ctx.display.fill_rectangle(
                    zoomed_grid_offset + i * zoomed_grid_pad,
                    zoomed_grid_offset,
                    grid_size,
                    self.region_size * zoomed_grid_pad + 1,
                    theme.highlight_color,
                )
            self._region_legend(row, column)
        elif mode == REGION_MODE:
            row = self.lr_index // self.columns
            column = self.lr_index % self.columns
            self.ctx.display.draw_qr_code(
                0, self.code, light_color=theme.disabled_color
            )
            self.highlight_qr_region(
                self.code,
                region=(
                    column * self.region_size,
                    (row) * self.region_size,
                    self.region_size,
                    self.region_size,
                ),
            )
            line_offset = grid_pad * row * self.region_size
            colunm_offset = grid_pad * column * self.region_size
            for i in range(self.region_size + 1):
                x_position = grid_offset + colunm_offset
                x_lenght = self.region_size * grid_pad + 1
                display_transpose = x_position + x_lenght - self.ctx.display.width()
                if display_transpose > 0:
                    x_lenght -= display_transpose
                self.ctx.display.fill_rectangle(
                    x_position,
                    grid_offset + i * grid_pad + line_offset,
                    x_lenght,
                    grid_size,
                    theme.highlight_color,
                )
            for i in range(self.region_size + 1):
                x_position = grid_offset + i * grid_pad + colunm_offset
                if x_position > self.ctx.display.width():
                    break
                self.ctx.display.fill_rectangle(
                    x_position,
                    grid_offset + line_offset,
                    grid_size,
                    self.region_size * grid_pad + 1,
                    theme.highlight_color,
                )
            self._region_legend(row, column)
        else:  #  TRANSCRIBE_MODE
            self.ctx.display.draw_qr_code(0, self.code, light_color=WHITE)
            for i in range(self.qr_size + 1):
                self.ctx.display.fill_rectangle(
                    grid_offset,
                    grid_offset + i * grid_pad,
                    self.qr_size * grid_pad + 1,
                    grid_size,
                    theme.highlight_color,
                )
                self.ctx.display.fill_rectangle(
                    grid_offset + i * grid_pad,
                    grid_offset,
                    grid_size,
                    self.qr_size * grid_pad + 1,
                    theme.highlight_color,
                )

    def display_seed_qr(self):
        """Disables touch and displays compact SeedQR code with grid to help
        drawing"""
        if self.title:
            label = self.title
        else:
            label = ""
        label += "\n" + t("Swipe to change mode")
        mode = 0
        while True:
            button = None
            while button not in (SWIPE_DOWN, SWIPE_UP):
                self.draw_grided_qr(mode)
                if self.ctx.input.touch is not None:
                    self.ctx.display.draw_hcentered_text(
                        label,
                        self.ctx.display.qr_offset() + self.ctx.display.font_height,
                    )
                # # Avoid the need of double click
                # self.ctx.input.buttons_active = True
                button = self.ctx.input.wait_for_button()
                if button in (BUTTON_PAGE, SWIPE_LEFT):  # page, swipe
                    mode += 1
                    mode %= 5
                    self.lr_index = 0
                elif button in (BUTTON_PAGE_PREV, SWIPE_RIGHT):  # page, swipe
                    mode -= 1
                    mode %= 5
                    self.lr_index = 0
                elif button in (BUTTON_ENTER, BUTTON_TOUCH):
                    if mode in (LINE_MODE, REGION_MODE, ZOOMED_R_MODE):
                        self.lr_index += 1
                    else:
                        if not (button == BUTTON_TOUCH and mode == TRANSCRIBE_MODE):
                            button = SWIPE_DOWN  # leave
                if mode == LINE_MODE:
                    self.lr_index %= self.qr_size
                elif mode in (REGION_MODE, ZOOMED_R_MODE):
                    self.lr_index %= self.columns * self.columns
            self.ctx.display.clear()
            if self.prompt(t("Are you sure?"), self.ctx.display.height() // 2):
                break
        if self.ctx.printer is None:
            return MENU_CONTINUE
        self.ctx.display.clear()
        if self.prompt(
            t("Print to QR?\n\n%s\n\n") % Settings().printer.driver,
            self.ctx.display.height() // 2,
        ):
            self.ctx.display.clear()
            self.ctx.display.draw_hcentered_text(
                t("Printing ..."), self.ctx.display.height() // 2
            )
            if self.title:
                self.ctx.printer.print_string(self.title + "\n\n")

            # Warn of SD read here because Printer don't have access to display
            if isinstance(self.ctx.printer, FilePrinter):
                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(t("Checking for SD card.."))

            self.ctx.printer.print_qr_code(self.code)
        return MENU_CONTINUE
