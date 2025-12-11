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

import time

from .kboard import kboard
from .krux_settings import Settings

IDLE = 0
PRESSED = 1
RELEASED = 2

SWIPE_DURATION_MS = 750
SWIPE_THRESHOLD = 35
SWIPE_RIGHT = 1
SWIPE_LEFT = 2
SWIPE_UP = 3
SWIPE_DOWN = 4
SWIPE_NONE = 5

TOUCH_S_PERIOD = 20  # Touch sample period - Min = 10
EDGE_PIXELS = 1  # The ammount of pixels to determine the edges of a region


class Touch:
    """Touch is a singleton API to interact with touchscreen driver"""

    def __init__(self, width, height, irq_pin=None, res_pin=None):
        """Touch API init - width and height are in Landscape mode
        For Krux width = max_y, height = max_x
        """
        self.sample_time = 0
        self.pressed_time = 0
        self.y_regions = []
        self.x_regions = []
        self.index = 0
        self.press_point = []
        self.release_point = (0, 0)
        self.gesture = None
        self.state = IDLE
        self.width, self.height = width, height
        if kboard.is_embed_fire:
            from .touchscreens.cst816 import touch_control

            self.touch_driver = touch_control
            self.touch_driver.activate(irq_pin)
        elif res_pin is not None:
            from .touchscreens.gt911 import touch_control

            self.touch_driver = touch_control
            self.touch_driver.activate(irq_pin, res_pin)
        else:
            from .touchscreens.ft6x36 import touch_control

            self.touch_driver = touch_control
            self.touch_driver.activate_irq(irq_pin)

        self.touch_driver.threshold(Settings().hardware.touch.threshold)

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

    def valid_position(self, data):
        """Checks if touch position is within buttons area"""

        if hasattr(Settings().hardware, "display") and getattr(
            Settings().hardware.display, "flipped_orientation", False
        ):
            data = (self.height - data[0], self.width - data[1])

        if self.x_regions and data[0] < self.x_regions[0]:
            return False
        if self.x_regions and data[0] > self.x_regions[-1]:
            return False
        if self.y_regions and data[1] < self.y_regions[0]:
            return False
        if self.y_regions and data[1] > self.y_regions[-1]:
            return False
        return True

    # def highlight_region(self, x_index, y_index):
    #     """Outlines the region of the current index"""
    #     import lcd
    #     from .themes import theme

    #     # Draw outline delimiting the region
    #     if y_index >= 0 and x_index >= 0:
    #         y_start = self.y_regions[y_index] if y_index < len(self.y_regions) else 0
    #         y_start += 1
    #         y_end = (
    #             self.y_regions[y_index + 1]
    #             if y_index + 1 < len(self.y_regions)
    #             else self.height
    #         )
    #         y_end -= 1
    #         x_start = self.x_regions[x_index] if x_index < len(self.x_regions) else 0
    #         x_start += 1
    #         x_end = (
    #             self.x_regions[x_index + 1]
    #             if x_index + 1 < len(self.x_regions)
    #             else self.height
    #         )
    #         x_end -= 1

    #         lcd.draw_outline(
    #             x_start,
    #             y_start,
    #             x_end - x_start,
    #             y_end - y_start,
    #             theme.fg_color,
    #         )

    def _extract_index(self, data):
        """
        Gets an index from touched points, x and y delimiters.
        Return index or -1 if touching an edge.
        """
        x, y = data

        # Helper to deal with X/Y regions
        def _compute_axis_index(pos, regions):
            if not regions:
                return 0

            # Count how many region boundaries pos passed
            idx = sum(pos + EDGE_PIXELS >= r for r in regions)

            # # Check boundary at idx-1 (left-side)
            if 1 < idx < len(regions) and abs(pos - regions[idx - 1]) <= EDGE_PIXELS:
                return -1

            # Valid is 0<= idx <= len(regions) -2 [valid regions]
            return max(min(idx - 1, len(regions) - 2), 0)

        # Y index
        y_index = _compute_axis_index(y, self.y_regions)
        if y_index < 0:
            return -1

        # X index
        if self.x_regions:
            x_index = _compute_axis_index(x, self.x_regions)
            if x_index < 0:
                return -1
            # self.highlight_region(
            #     y_index * (len(self.x_regions) - 1) + x_index, y_index
            # )
            return y_index * (len(self.x_regions) - 1) + x_index

        # self.highlight_region(0, y_index)
        return y_index

    def set_regions(self, x_list=None, y_list=None):
        """Set buttons map regions x and y"""
        if x_list:
            if isinstance(x_list, list):
                self.x_regions = x_list
            else:
                raise ValueError("x_list must be a list")
        else:
            self.x_regions = []

        if y_list:
            if isinstance(y_list, list):
                self.y_regions = y_list
            else:
                raise ValueError("y_list must be a list")
        else:
            self.y_regions = []

    def _store_points(self, data):
        """Store pressed points and calculare an average pressed point"""

        if hasattr(Settings().hardware, "display") and getattr(
            Settings().hardware.display, "flipped_orientation", False
        ):
            new_y = max(0, self.height - data[0])
            new_y = min(new_y, self.height - 1)
            new_x = max(0, self.width - data[1])
            new_x = min(new_x, self.width - 1)
            data = (new_y, new_x)

        if self.state == IDLE:
            self.state = PRESSED
            self.press_point = [data]
            self.index = self._extract_index(self.press_point[0])
        # Calculare an average (max. 10 samples) pressed point to increase precision
        elif self.state == PRESSED and len(self.press_point) < 10:
            self.press_point.append(data)
            len_press = len(self.press_point)
            x = 0
            y = 0
            for n in range(len_press):
                x += self.press_point[n][0]
                y += self.press_point[n][1]
            x //= len_press
            y //= len_press
            self.index = self._extract_index((x, y))
        self.release_point = data

    def current_state(self):
        """Returns the touchscreen state"""
        self.sample_time = time.ticks_ms()
        data = self.touch_driver.current_point()
        if isinstance(data, tuple):
            self._store_points(data)
            return self.state

        if data is None:  # gets release then return to idle.
            if self.state == RELEASED:  # On touch release
                self.state = IDLE
                return self.state

            if self.state == PRESSED:
                self.state = RELEASED

                if self.release_point is not None:
                    dx = self.release_point[0] - self.press_point[0][0]
                    dy = self.release_point[1] - self.press_point[0][1]

                    if abs(dx) > SWIPE_THRESHOLD or abs(dy) > SWIPE_THRESHOLD:
                        # discard swipes that took more than ~1s
                        if self.sample_time - self.pressed_time < SWIPE_DURATION_MS:
                            # discards swipes with angle > 27 degrees
                            if abs(dx) > abs(dy) * 2:
                                self.gesture = SWIPE_LEFT if dx < 0 else SWIPE_RIGHT
                            elif abs(dy) > abs(dx) * 2:
                                self.gesture = SWIPE_UP if dy < 0 else SWIPE_DOWN
                            else:
                                self.gesture = SWIPE_NONE  # undetermined diagonal swipe
                        else:
                            self.gesture = (
                                SWIPE_NONE  # hold finger on screen for too long
                            )
            return self.state

        print("Touch error")
        return self.state

    def event(self, validate_position=True):
        """Checks if a touch happened and stores the point"""
        current_time = time.ticks_ms()
        if current_time > self.sample_time + TOUCH_S_PERIOD:
            if self.touch_driver.event():
                # Resets touch and gets irq point
                self.state = IDLE
                if not validate_position:
                    return True
                if isinstance(self.touch_driver.irq_point, tuple):
                    if self.valid_position(self.touch_driver.irq_point):
                        self._store_points(self.touch_driver.irq_point)
                        self.pressed_time = time.ticks_ms()
                        return True
        return False

    def value(self):
        """Wraps touch states to behave like a regular button"""
        return 1 if self.current_state() == IDLE else 0

    def _swipe_state_check(self, swipe_type):
        if self.gesture == swipe_type:
            self.gesture = None
            return 0
        return 1

    def swipe_none_value(self):
        """Returns detected gestures and clean respective variable"""
        return self._swipe_state_check(SWIPE_NONE)

    def swipe_right_value(self):
        """Returns detected gestures and clean respective variable"""
        return self._swipe_state_check(SWIPE_RIGHT)

    def swipe_left_value(self):
        """Returns detected gestures and clean respective variable"""
        return self._swipe_state_check(SWIPE_LEFT)

    def swipe_up_value(self):
        """Returns detected gestures and clean respective variable"""
        return self._swipe_state_check(SWIPE_UP)

    def swipe_down_value(self):
        """Returns detected gestures and clean respective variable"""
        return self._swipe_state_check(SWIPE_DOWN)

    def current_index(self):
        """Returns current index of last touched point"""
        return self.index
