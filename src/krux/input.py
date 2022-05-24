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
import time
import board
from Maix import GPIO
from fpioa_manager import fm
from .wdt import wdt
from .touch import Touch

BUTTON_ENTER = 0
BUTTON_PAGE = 1
BUTTON_PAGE_PREV = 2
BUTTON_TOUCH = 3
SWIPE_RIGHT = 4
SWIPE_LEFT = 5

QR_ANIM_PERIOD = 900  # miliseconds
LONG_PRESS_T = 1000 #miliseconds
NONBLOCKING_CHECKS = 100000

PRESSED = 0
RELEASED = 1


class Input:
    """Input is a singleton interface for interacting with the device's buttons"""

    def __init__(self):
        self.entropy = 0
        if "BUTTON_A" in board.config["krux"]["pins"]:
            fm.register(board.config["krux"]["pins"]["BUTTON_A"], fm.fpioa.GPIOHS21)
            self.enter = GPIO(GPIO.GPIOHS21, GPIO.IN, GPIO.PULL_UP)
        else:
            self.enter = None
        if "BUTTON_B" in board.config["krux"]["pins"]:
            fm.register(board.config["krux"]["pins"]["BUTTON_B"], fm.fpioa.GPIOHS22)
            self.page = GPIO(GPIO.GPIOHS22, GPIO.IN, GPIO.PULL_UP)
        else:
            self.page = None
        if "BUTTON_C" in board.config["krux"]["pins"]:
            fm.register(board.config["krux"]["pins"]["BUTTON_C"], fm.fpioa.GPIOHS0)
            self.page_prev = GPIO(GPIO.GPIOHS0, GPIO.IN, GPIO.PULL_UP)
        else:
            if board.config["type"] == "m5stickv":
                from pmu import PMU_Button
                self.page_prev = PMU_Button()
            else:
                self.page_prev = None
        self.has_touch = board.config["krux"]["display"]["touch"]
        self.touch = (
            Touch(board.config["lcd"]["width"], board.config["lcd"]["height"])
            if self.has_touch
            else None
        )

        # This flag, used in slection outlines, is set if buttons are being used
        if self.has_touch:
            self.buttons_active = False
        else:
            self.buttons_active = True

    def enter_value(self):
        """Intermediary method to pull button A state, if available"""
        if self.enter is not None:
            return self.enter.value()
        return RELEASED

    def page_value(self):
        """Intermediary method to pull button B state, if available"""
        if self.page is not None:
            return self.page.value()
        return RELEASED

    def page_prev_value(self):
        """Intermediary method to pull button C state, if available"""
        if self.page_prev is not None:
            return self.page_prev.value()
        return RELEASED

    def touch_value(self):
        """Intermediary method to pull touch state, if touch available"""
        if self.touch is not None:
            return self.touch.value()
        return RELEASED

    def swipe_right_value(self):
        """Intermediary method to pull touch gesture, if touch available"""
        if self.touch is not None:
            return self.touch.swipe_right_value()
        return RELEASED

    def swipe_left_value(self):
        """Intermediary method to pull touch gesture, if touch available"""
        if self.touch is not None:
            return self.touch.swipe_left_value()
        return RELEASED

    def wait_for_release(self):
        """Loop until all buttons are released (if currently pressed)"""
        while (
            self.enter_value() == PRESSED
            or self.page_value() == PRESSED
            or self.page_prev_value() == PRESSED
            or self.touch_value() == PRESSED
        ):
            self.entropy += 1
            wdt.feed()

    def wait_for_press(self, block=True):
        """Wait for first button press"""
        time_frame = time.ticks_ms()
        while (
            self.enter_value() == RELEASED
            and self.page_value() == RELEASED
            and self.page_prev_value() == RELEASED
            and self.touch_value() == RELEASED
        ):
            self.entropy += 1
            wdt.feed()  # here is were krux spend most of time
            if not block and time.ticks_ms() > time_frame + QR_ANIM_PERIOD:
                break

    def wait_for_button(self, block=True):
        """Waits for any button to release, optionally blocking if block=True.
        Returns the button that was released, or None if nonblocking.
        """
        self.wait_for_release()
        self.wait_for_press(block)

        if self.enter_value() == PRESSED:
            # Wait for release
            while self.enter_value() == PRESSED:
                self.entropy += 1
                wdt.feed()
            if self.buttons_active:
                return BUTTON_ENTER
            self.buttons_active = True

        if self.page_value() == PRESSED:
            # Wait for release
            time_frame = time.ticks_ms()
            while self.page_value() == PRESSED:
                self.entropy += 1
                wdt.feed()
                if time.ticks_ms() > time_frame + LONG_PRESS_T:
                    return SWIPE_LEFT
            if self.buttons_active:
                return BUTTON_PAGE
            self.buttons_active = True

        if self.page_prev_value() == PRESSED:
            # Wait for release
            while self.page_prev_value() == PRESSED:
                self.entropy += 1
                wdt.feed()
            if self.buttons_active:
                return BUTTON_PAGE_PREV
            self.buttons_active = True

        if self.touch_value() == PRESSED:
            # Wait for release
            while self.touch_value() == PRESSED:
                self.entropy += 1
                wdt.feed()
            self.buttons_active = False
            if self.swipe_right_value() == PRESSED:
                return SWIPE_RIGHT
            if self.swipe_left_value() == PRESSED:
                return SWIPE_LEFT
            return BUTTON_TOUCH

        return None
