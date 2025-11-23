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
# pylint: disable=R0902
import board


class KBoard:
    """A simple class to organize and cache board related information"""

    def __init__(self):
        self.is_amigo = board.config["type"] == "amigo"
        self.is_bit = board.config["type"] == "bit"
        self.is_cube = board.config["type"] == "cube"
        self.is_embed_fire = board.config["type"] == "embed_fire"
        self.is_yahboom = board.config["type"] == "yahboom"
        self.is_wonder_mv = board.config["type"] == "wonder_mv"
        self.is_tzt = board.config["type"] == "tzt"
        self.is_wonder_k = board.config["type"] == "wonder_k"
        self.is_m5stickv = board.config["type"] == "m5stickv"
        self.has_battery = False  # Variable to be set in Login Page
        self.has_touchscreen = board.config["krux"]["display"].get("touch", False)
        self.has_minimal_display = self.is_m5stickv or self.is_cube
        self.can_control_brightness = any(
            [self.is_cube, self.is_m5stickv, self.is_wonder_mv, self.is_wonder_k]
        )
        self.can_flip_orientation = (
            self.is_yahboom or self.is_wonder_mv or self.is_wonder_k
        )
        self.has_light = "LED_W" in board.config["krux"]["pins"]
        self.has_backlight = "BACKLIGHT" in board.config["krux"]["pins"]
        self.has_encoder = "ENCODER" in board.config["krux"]["pins"]
        self.need_release_filter = self.has_encoder or self.is_cube


kboard = KBoard()
