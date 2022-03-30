# The MIT License (MIT)

# Copyright (c) 2021 Tom J. Sun

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
import gc
import sensor
import lcd
from .qr import QRPartParser


class Camera:
    """Camera is a singleton interface for interacting with the device's camera"""

    def __init__(self, wdt):
        self.wdt = wdt
        self.initialize_sensor()

    def initialize_sensor(self):
        """Initializes the camera"""
        sensor.reset()
        sensor.set_pixformat(sensor.GRAYSCALE)
        sensor.set_framesize(sensor.QVGA)
        sensor.skip_frames()

    def capture_qr_code_loop(self, callback):
        """Captures either singular or animated QRs and parses their contents until
        all parts of the message have been captured. The part data are then ordered
        and assembled into one message and returned.
        """
        self.initialize_sensor()
        sensor.run(1)

        parser = QRPartParser()

        prev_parsed_count = 0
        new_part = False
        while True:
            self.wdt.feed()
            stop = callback(parser.total_count(), parser.parsed_count(), new_part)
            if stop:
                break

            new_part = False

            img = sensor.snapshot()
            gc.collect()
            hist = img.get_histogram()
            if "histogram" not in str(type(hist)):
                continue
            # Convert the image to black and white by using Otsu's thresholding.
            # This is done to account for spots, blotches, and streaks in the code
            # that may cause issues for the decoder.
            img.binary([(0, hist.get_threshold().value())], invert=True)
            lcd.display(img)

            res = img.find_qrcodes()
            if len(res) > 0:
                data = res[0].payload()

                parser.parse(data)

                if parser.parsed_count() > prev_parsed_count:
                    prev_parsed_count = parser.parsed_count()
                    new_part = True

            if parser.is_complete():
                break

        sensor.run(0)

        if parser.is_complete():
            return (parser.result(), parser.format)
        return (None, None)
