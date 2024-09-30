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

import flash
import sensor
from . import Page, MENU_CONTINUE
from .capture_entropy import CameraEntropy, POOR_VARIANCE_TH
from ..themes import theme
from ..krux_settings import t
from ..display import BOTTOM_LINE
from ..wdt import wdt
from ..firmware import FLASH_SIZE

FLASH_ROWS = 64
BLOCK_SIZE = 0x1000
TOTAL_BLOCKS = FLASH_SIZE // BLOCK_SIZE
IMAGE_BYTES_SIZE = 0x25800
MAX_CHUNK_INDEX = IMAGE_BYTES_SIZE // BLOCK_SIZE


class FillFlash(Page):
    """Sweep the flash memory and draw a map of the used regions"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def fill_flash_with_camera_entropy(self):
        """Draw the flash map"""

        if not self.prompt(
            t("Fill the flash with entropy from camera?"),
            self.ctx.display.height() // 2,
        ):
            return MENU_CONTINUE
        blocks_per_line = TOTAL_BLOCKS + self.ctx.display.width()
        blocks_per_line //= self.ctx.display.width()
        empty_buf = b"\xff" * BLOCK_SIZE
        counter = 0
        offset_x = self.ctx.display.width()
        offset_x -= TOTAL_BLOCKS // blocks_per_line
        offset_x //= 2
        offset_y = BOTTOM_LINE
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(t("Filling Flash"))
        self.ctx.camera.initialize_run()
        entropy_measurement = CameraEntropy(self.ctx)
        chunk_index = MAX_CHUNK_INDEX
        color = theme.fg_color
        # Draw a map of the flash memory
        for address in range(0, FLASH_SIZE, BLOCK_SIZE):
            wdt.feed()
            # checks if a new image is needed
            if chunk_index == MAX_CHUNK_INDEX:
                chunk_index = 0
                while True:
                    self.ctx.display.to_landscape()
                    img = sensor.snapshot()
                    self.ctx.display.render_image(img)
                    entropy_measurement.entropy_measurement_update(
                        img, all_at_once=True
                    )
                    if entropy_measurement.stdev_index > POOR_VARIANCE_TH:
                        img_bytes = img.to_bytes()
                        break
                self.ctx.display.to_portrait()

            if flash.read(address, BLOCK_SIZE) == empty_buf:
                flash.write(
                    address,
                    img_bytes[
                        chunk_index * BLOCK_SIZE : (chunk_index + 1) * BLOCK_SIZE
                    ],
                )
                chunk_index += 1
                color = theme.highlight_color
            if counter % blocks_per_line == 0:
                self.ctx.display.draw_vline(
                    offset_x,
                    offset_y,
                    10,
                    color,
                )
                color = theme.fg_color
                offset_x += 1
            counter += 1
        self.ctx.camera.stop_sensor()
        self.flash_text(t("Flash filled with camera entropy"))

        return MENU_CONTINUE
