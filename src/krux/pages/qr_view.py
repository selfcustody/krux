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
from . import Page, Menu, MENU_CONTINUE, MENU_EXIT
from ..sd_card import SDHandler
from ..themes import theme, WHITE, BLACK
from ..krux_settings import t
from ..qr import get_size, add_qr_frame
from ..display import DEFAULT_PADDING
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

    def __init__(self, ctx, binary=False, data=None, title=None):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.binary = binary
        if data:
            self.code = qrcode.encode_to_string(data)
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
        return qrcode.encode_to_string(numbers)

    def _binary_seed_qr(self):
        binary_seed = self._to_compact_seed_qr(self.ctx.wallet.key.mnemonic)
        return qrcode.encode_to_string(binary_seed)

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
        size, code = add_qr_frame(code)
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

    def save_pbm_image(self, file_name):
        """Saves QR code image as compact B&W bitmap format file"""
        from ..sd_card import PBM_IMAGE_EXTENSION

        size, code = add_qr_frame(self.code)
        qr_image_file = (
            "P4\n# Krux\n".encode()
            + str(size).encode()
            + (" ").encode()
            + str(size).encode()
            + ("\n").encode()
        )
        lines = code.strip().split("\n")
        for bit_string_line in lines:
            if size % 8:
                bit_string_line += "0" * (8 - size % 8)
            line = int(bit_string_line, 2).to_bytes((self.qr_size + 7) // 8, "big")
            qr_image_file += line
        file_name += PBM_IMAGE_EXTENSION
        with SDHandler() as sd:
            sd.write_binary(file_name, qr_image_file)
        self.flash_text(t("Saved to SD card:\n%s") % file_name)

    def save_bmp_image(self, file_name, resolution):
        """Save QR code image as .bmp file"""
        from ..sd_card import BMP_IMAGE_EXTENSION

        # TODO: Try Compression?
        import image
        import lcd

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Saving ..."))
        size, code = add_qr_frame(self.code)
        raw_image = image.Image(size=(size, size))
        x_index = 0
        y_index = 0
        for qr_char in code:
            if qr_char in ("0", "1"):
                if qr_char == "0":
                    raw_image.set_pixel((x_index, y_index), lcd.WHITE)
                if qr_char == "1":
                    raw_image.set_pixel((x_index, y_index), lcd.BLACK)
                if x_index == size - 1:
                    x_index = 0
                    y_index += 1
                else:
                    x_index += 1
        bmp_img = image.Image(size=(resolution, resolution), copy_to_fb=True)
        scale = resolution // size
        bmp_img.draw_image(
            raw_image,
            0,
            0,
            x_scale=scale,
            y_scale=scale,
        )
        file_name += BMP_IMAGE_EXTENSION
        bmp_img.save("/sd/" + file_name)
        self.flash_text(t("Saved to SD card:\n%s") % file_name)

    def save_qr_image_menu(self):
        """Options to save QR codes as images on SD card"""
        # TODO: Allow custom file name
        from .files_operations import SaveFile

        file_saver = SaveFile(self.ctx)
        file_name, filename_undefined = file_saver.set_filename(
            self.title.replace(" ", "_"),
        )
        if filename_undefined:
            return
        size = self.qr_size + 2
        bmp_resolutions = []
        resolution = size
        for _ in range(4):
            resolution *= 2
            if resolution <= 480:
                bmp_resolutions.append(resolution)
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(
            t("Resolution - Format"), self.ctx.display.font_height, info_box=True
        )
        qr_menu = []
        qr_menu.append(
            ("%dx%d - PBM" % (size, size), lambda: self.save_pbm_image(file_name))
        )
        for bmp_resolution in bmp_resolutions:
            qr_menu.append(
                (
                    "%dx%d - BMP" % (bmp_resolution, bmp_resolution),
                    lambda res=bmp_resolution: self.save_bmp_image(file_name, res),
                )
            )
        submenu = Menu(self.ctx, qr_menu, offset=2 * self.ctx.display.font_height)
        submenu.run_loop()
        # return MENU_EXIT  # Uncomment to exit QR Viewer after saving

    def print_qr(self):
        "Printer handler"
        from .utils import Utils

        utils = Utils(self.ctx)
        utils.print_standard_qr(self.code, title=self.title, is_qr=True)
        # return MENU_EXIT  # Uncomment to exit QR Viewer after printing

    def display_qr(self, allow_export=False):
        """Displays QR codes in multiple modes"""

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
            qr_menu = []
            qr_menu.append((t("Leave QR Viewer"), lambda: MENU_EXIT))
            if self.has_sd_card() and allow_export:
                qr_menu.append((t("Save QR Image to SD Card"), self.save_qr_image_menu))
            if self.has_printer():
                qr_menu.append((t("Print to QR"), self.print_qr))
            qr_menu.append((t("Back"), lambda: None))
            submenu = Menu(self.ctx, qr_menu)
            _, status = submenu.run_loop()
            if status == MENU_EXIT:
                return MENU_CONTINUE
