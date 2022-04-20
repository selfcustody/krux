# The MIT License (MIT)

# Copyright (c) 2022 Eduardo Schoenknecht

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

import time
from .touchscreens.ft6x36 import FT6X36

TOUCH_R_PERIOD = 50  # 1000/50 = 20 samples/second


class Touch:
    """Touch is a singleton API to interact with touchscreen driver"""

    idle, press, release = 0, 1, 2

    def __init__(self, width, height):
        """Touch API init - width and height are in Landscape mode
        For Krux width = max_y, height = max_x
        """
        self.cycle = TOUCH_R_PERIOD
        self.last_time = 0
        self.y_regions = []
        self.x_regions = []
        self.index = 0
        self.state = Touch.idle
        self.width, self.height = width, height
        self.touch_driver = FT6X36()

    def clear_regions(self):
        """Remove previously stored buttons map"""
        self.y_regions = []
        self.x_regions = []

    def add_y_delimiter(self, region):
        """Adds a y button delimiter to be mapped as a array by touchscreen"""
        if region > self.width:
            raise ValueError("Touch region added outside display area")
        self.y_regions.append(region)

    def add_x_delimiter(self, region):
        """Adds a x button delimiter to be mapped as a array by touchscreen"""
        if region > self.height:
            raise ValueError("Touch region added outside display area")
        self.x_regions.append(region)

    def extract_index(self, data):
        """Gets an index from touched points, y and x delimiters"""
        if self.state != Touch.press:
            self.state = Touch.press
            self.index = 0
            if self.y_regions:
                for region in self.y_regions:
                    if data[1] > region:
                        self.index += 1
                if self.index == 0 or self.index >= len(
                    self.y_regions
                ):  # outside y areas
                    self.state = Touch.idle
                else:
                    self.index -= 1
                    if self.x_regions:  # if 2D array
                        self.index *= len(self.x_regions) - 1
                        x_index = 0
                        for x_region in self.x_regions:
                            if data[0] > x_region:
                                x_index += 1
                        if x_index == 0 or x_index >= len(
                            self.x_regions
                        ):  # outside x areas
                            self.state = Touch.idle
                        else:
                            x_index -= 1
                        self.index += x_index
            else:
                self.index = 0

    def current_state(self):
        """Returns the touchscreen state"""
        if time.ticks_ms() > self.last_time + self.cycle:
            self.last_time = time.ticks_ms()
            data = self.touch_driver.current_point()
            if data is not None:
                self.extract_index(data)
            else:  # gets realease than return to ilde.
                if self.state == Touch.release:
                    self.state = Touch.idle
                elif self.state == Touch.press:
                    self.state = Touch.release
        return self.state

    def value(self):
        """wraps touch states to behave like a regular button"""
        return 0 if self.current_state() == Touch.press else 1
