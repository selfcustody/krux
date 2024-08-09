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
import lcd
import board
import time
from . import Page
from ..input import PRESSED
from ..themes import theme
from ..qr import QRPartParser, FORMAT_UR
from ..wdt import wdt
from ..krux_settings import t

ANTI_GLARE_WAIT_TIME = 500


class QRCodeCapture(Page):
    """UI to capture an encryption key"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def light_control(self):
        """Controls the light based on the user input"""
        if self.ctx.input.enter_value() == PRESSED:
            self.ctx.light.turn_on()
        else:
            self.ctx.light.turn_off()

    def anti_glare_control(self):
        """Controls the anti-glare based on the user input"""
        self.ctx.display.to_portrait()
        if self.ctx.camera.toggle_antiglare():
            self.ctx.display.draw_centered_text(t("Anti-glare enabled"))
        else:
            self.ctx.display.draw_centered_text(t("Anti-glare disabled"))
        time.sleep_ms(ANTI_GLARE_WAIT_TIME)
        self.ctx.display.to_landscape()
        self.ctx.input.reset_ios_state()

    def update_progress(self, parser, index, previous_index):
        """Updates the progress bar based on parts parsed"""
        self.ctx.display.to_portrait()
        height = {"cube": 225, "m5stickv": 210, "amigo": 380}.get(
            board.config["type"], 305
        )
        if parser.format == FORMAT_UR:
            filled = (
                self.ctx.display.width() * parser.parsed_count()
            ) // parser.total_count()
            self.ctx.display.fill_rectangle(0, height, filled, 15, theme.fg_color)
        else:
            block_size = self.ctx.display.width() // parser.total_count()
            x_offset = block_size * index
            self.ctx.display.fill_rectangle(
                x_offset, height, block_size, 15, theme.highlight_color
            )
            if previous_index is not None:
                x_offset = block_size * previous_index
                self.ctx.display.fill_rectangle(
                    x_offset, height, block_size, 15, theme.fg_color
                )

        self.ctx.display.to_landscape()

    def qr_capture_loop(self):
        """Captures either singular or animated QRs and parses their contents"""

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Loading Camera.."))
        self.ctx.display.to_landscape()
        self.ctx.camera.initialize_run()

        parser = QRPartParser()
        prev_parsed_count = 0
        new_part = None
        previous_part = None

        self.ctx.input.reset_ios_state()
        while True:
            wdt.feed()

            if self.ctx.light:
                self.light_control()
            elif self.ctx.input.enter_event():
                break

            # Anti-glare mode
            if self.ctx.input.page_event() or (
                board.config["type"] == "yahboom" and self.ctx.input.page_prev_event()
            ):
                if self.ctx.camera.has_antiglare():
                    self.anti_glare_control()
                else:
                    break

            # Exit the capture loop with PAGE_PREV or TOUCH
            if self.ctx.input.page_prev_event() or self.ctx.input.touch_event():
                break

            if new_part is not None and new_part != previous_part:
                self.update_progress(parser, new_part, previous_part)
                previous_part = new_part if parser.format != FORMAT_UR else None
                new_part = None

            img = self.ctx.camera.snapshot()
            res = img.find_qrcodes()

            if board.config["type"] == "m5stickv":
                img.lens_corr(strength=1.0, zoom=0.56)
                lcd.display(img, oft=(0, 0), roi=(68, 52, 185, 135))
            elif board.config["type"] == "amigo":
                x_offset = 40 if self.ctx.display.flipped_x_coordinates else 120
                lcd.display(img, oft=(x_offset, 40))
            elif board.config["type"] == "cube":
                lcd.display(img, oft=(0, 0), roi=(0, 0, 224, 240))
            else:
                lcd.display(img, oft=(0, 0), roi=(0, 0, 304, 240))

            if res:
                data = res[0].payload()
                new_part = parser.parse(data)

                if (
                    parser.format == FORMAT_UR
                    and parser.processed_parts_count() > prev_parsed_count
                ):
                    prev_parsed_count = parser.processed_parts_count()
                    new_part = True

            if parser.is_complete():
                break

        self.ctx.camera.stop_sensor()
        if self.ctx.light:
            self.ctx.light.turn_off()
        self.ctx.display.to_portrait()

        if parser.is_complete():
            return parser.result(), parser.format
        return None, None
