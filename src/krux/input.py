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
from .touchscreen import Touch

BUTTON_ENTER = 0
BUTTON_PAGE = 1
BUTTON_PREVIOUS = 2
BUTTON_TOUCH = 3

QR_ANIM_PERIOD = 900  # miliseconds
NONBLOCKING_CHECKS = 100000

PRESSED = 0
RELEASED = 1
TOUCH_IDLE = 0
TOUCH_PRESSED = 1


class Input:
    """Input is a singleton interface for interacting with the device's buttons"""

    def __init__(self):
        self.entropy = 0
        fm.register(board.config["krux.pins"]["BUTTON_A"], fm.fpioa.GPIOHS21)
        self.enter = GPIO(GPIO.GPIOHS21, GPIO.IN, GPIO.PULL_UP)
        fm.register(board.config["krux.pins"]["BUTTON_B"], fm.fpioa.GPIOHS22)
        self.page = GPIO(GPIO.GPIOHS22, GPIO.IN, GPIO.PULL_UP)
        if "BUTTON_C" in board.config["krux.pins"]:
            fm.register(board.config["krux.pins"]["BUTTON_C"], fm.fpioa.GPIOHS0)
            self.previous = GPIO(GPIO.GPIOHS0, GPIO.IN, GPIO.PULL_UP)
        self.has_touch = board.config["lcd"]["touch"]
        self.touch = (
            Touch(board.config["lcd"]["width"], board.config["lcd"]["height"], 50)
            if self.has_touch
            else None
        )

    def get_button_c(self):
        """Intermediary method to pull button C state, if available"""
        if "BUTTON_C" in board.config["krux.pins"]:
            return self.previous.value()
        return RELEASED

    def get_touch_state(self):
        """Intermediary method to pull touch state, if touch available"""
        if self.has_touch:
            return self.touch.get_state()
        return TOUCH_IDLE

    def wait_for_release(self):
        """Loop until all buttons are released (if currently pressed)"""
        while (
            self.enter.value() == PRESSED
            or self.page.value() == PRESSED
            or self.get_button_c() == PRESSED
            or self.get_touch_state() == TOUCH_PRESSED
        ):
            self.entropy += 1

    def wait_for_press(self, block=True):
        """Wait for first button press"""
        time_frame = time.ticks_ms()
        while (
            self.enter.value() == RELEASED
            and self.page.value() == RELEASED
            and self.get_button_c() == RELEASED
            and self.get_touch_state() == TOUCH_IDLE
        ):
            wdt.feed() #here is were krux spend most of time
            if not block and time.ticks_ms() > time_frame + QR_ANIM_PERIOD:
                break

    def wait_for_button(self, block=True):
        """Waits for any button to release, optionally blocking if block=True.
        Returns the button that was released, or None if nonblocking.
        """
        self.wait_for_release()
        self.wait_for_press(block)

        if self.enter.value() == PRESSED:
            # Wait for release
            while self.enter.value() == PRESSED:
                self.entropy += 1
            return BUTTON_ENTER

        if self.page.value() == PRESSED:
            # Wait for release
            while self.page.value() == PRESSED:
                self.entropy += 1
            return BUTTON_PAGE

        if self.get_button_c() == PRESSED:
            # Wait for release
            while self.get_button_c() == PRESSED:
                self.entropy += 1
            return BUTTON_PREVIOUS

        if self.get_touch_state() == TOUCH_PRESSED:
            while self.get_touch_state() == TOUCH_PRESSED:
                self.entropy += 1
            return BUTTON_TOUCH

        return None
