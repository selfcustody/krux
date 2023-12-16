# The MIT License (MIT)

# Copyright (c) 2021-2022 Krux contributors

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

import math
from . import Page
from ..input import PRESSED

LABEL_Y_POSITION = 400
POOR_VARIANCE_TH = 10
INSUFFICIENT_VARIANCE_TH = 5  # %
INSUFFICIENT_SHANNONS_ENTROPY_TH = 3  # bits per pixel
SHANNONS_BLOCK_SIZE = 0x4000  # 16384B, result in ~10 blocks for a QVGA img


class CameraEntropy(Page):
    """Class for capturing entropy from a snapshot"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def _callback(self):
        # Accepted
        if self.ctx.input.enter_event() or self.ctx.input.touch_event():
            return 1

        # Exited
        if self.ctx.input.page_event() or self.ctx.input.page_prev_event():
            return 2
        return 0

    def shannons_entropy_16bit(self, image_bytes):
        """Function to calculate Shannon's entropy.
        Will return average number of bits required to encode each pixel,
        based on the probability distribution of the pixel values, ranging from 0 to 16.
        The entropy value is a theoretical lower bound on the number of bits needed to
        encode the image without loss, under an ideal compression algorithm.
        This means that in the best-case scenario, you can't compress the image to
        fewer bits per pixel than the entropy value without losing information"""

        # Calculate frequency of each pixel value
        pixel_counts = {}
        for i in range(0, len(image_bytes), 2):
            pixel_value = int.from_bytes(image_bytes[i : i + 2], "little")
            if pixel_value in pixel_counts:
                pixel_counts[pixel_value] += 1
            else:
                pixel_counts[pixel_value] = 1

        # Total number of pixels (half the number of bytes)
        total_pixels = len(image_bytes) // 2

        # Calculate entropy
        entropy = 0
        for count in pixel_counts.values():
            probability = count / total_pixels
            entropy -= probability * (probability and math.log2(probability))

        return entropy

    def capture(self):
        """Captures camera's entropy as the hash of image buffer"""
        import hashlib
        import board
        import gc
        import sensor
        import lcd
        from ..wdt import wdt
        from ..krux_settings import t
        from ..themes import theme

        def rms_value(data):
            if not data:
                return 0
            square_sum = sum(x**2 for x in data)
            mean_square = square_sum / len(data)
            rms = math.sqrt(mean_square)
            return int(rms)

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("TOUCH or ENTER to capture"))
        self.ctx.display.to_landscape()
        self.ctx.camera.initialize_sensor()
        sensor.run(1)
        self.ctx.display.clear()
        command = 0
        while True:
            wdt.feed()
            img = sensor.snapshot()
            l_stdev = img.get_statistics().l_stdev()
            a_stdev = img.get_statistics().a_stdev()
            b_stdev = img.get_statistics().b_stdev()
            variance_index = rms_value([l_stdev, a_stdev, b_stdev])
            if self.ctx.display.height() > 320:
                self.ctx.display.to_portrait()
                self.ctx.display.fill_rectangle(
                    0,
                    LABEL_Y_POSITION,
                    320,
                    self.ctx.display.font_height,
                    theme.bg_color,
                )
                if variance_index > POOR_VARIANCE_TH:
                    self.ctx.display.draw_hcentered_text(
                        "Good entropy", LABEL_Y_POSITION, theme.go_color
                    )
                elif variance_index > INSUFFICIENT_VARIANCE_TH:
                    self.ctx.display.draw_hcentered_text(
                        "Poor entropy", LABEL_Y_POSITION, theme.del_color
                    )
                else:
                    self.ctx.display.draw_hcentered_text(
                        "Insufficient entropy", LABEL_Y_POSITION, theme.error_color
                    )
                self.ctx.display.to_landscape()
            command = self._callback()
            if command > 0:
                break

            if board.config["type"] == "m5stickv":
                img.lens_corr(strength=1.0, zoom=0.56)
            elif board.config["type"].startswith("amigo"):
                lcd.display(img, oft=(40, 40))
            else:
                lcd.display(img, oft=(0, 0), roi=(0, 0, 304, 240))

        self.ctx.display.to_portrait()
        gc.collect()
        sensor.run(0)

        # User cancelled
        if command == 2:
            self.flash_text(t("Capture cancelled"))
            return None
        
        self.ctx.display.draw_centered_text(t("Calculating Shannon's entropy"))

        img_bytes = img.to_bytes()
        del img

        # Calculate Shannon's entropy:
        # Ideally Shannon's entropy should be calculated at once,
        # but as we don't have enough RAM let's calculate it in blocks and do the average.
        # 320px * 240px * 2 Bytes = 153600 Bytes
        shannon_16b = 0.0
        blocks = 0
        for s_index in range(0, len(img_bytes), SHANNONS_BLOCK_SIZE):
            shannon_16b += self.shannons_entropy_16bit(
                img_bytes[s_index : s_index + SHANNONS_BLOCK_SIZE]
            )
            blocks += 1
        shannon_16b /= blocks

        entropy_msg = "Shannon's entropy: "
        entropy_msg += str(round(shannon_16b, 2)) + " bits per pixel\n\n"
        entropy_msg += "Pixels variance: "
        entropy_msg += str(variance_index) + "%"
        self.ctx.display.clear()
        if (
            shannon_16b < INSUFFICIENT_SHANNONS_ENTROPY_TH
            or variance_index < INSUFFICIENT_VARIANCE_TH
        ):
            error_msg = t("Insufficient Entropy!")
            error_msg += "\n\n"
            error_msg += entropy_msg
            self.ctx.display.draw_centered_text(error_msg, theme.error_color)
            self.ctx.input.wait_for_button()
            return None
        self.ctx.display.draw_centered_text(entropy_msg)
        self.ctx.input.wait_for_button()
        hasher = hashlib.sha256()
        image_len = len(img_bytes)
        hasher_index = 0
        while hasher_index < image_len:
            hasher.update(img_bytes[hasher_index : hasher_index + 128])
            hasher_index += 128
        return hasher.digest()
