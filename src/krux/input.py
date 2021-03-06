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
import board
from Maix import GPIO
from fpioa_manager import fm
from .wdt import wdt

BUTTON_ENTER = 0
BUTTON_PAGE = 1

NONBLOCKING_CHECKS = 100000

PRESSED = 0
RELEASED = 1


class Input:
    """Input is a singleton interface for interacting with the device's buttons"""

    def __init__(self):
        self.entropy = 0
        fm.register(board.config["krux.pins"]["BUTTON_A"], fm.fpioa.GPIOHS21)
        self.enter = GPIO(GPIO.GPIOHS21, GPIO.IN, GPIO.PULL_UP)
        fm.register(board.config["krux.pins"]["BUTTON_B"], fm.fpioa.GPIOHS22)
        self.page = GPIO(GPIO.GPIOHS22, GPIO.IN, GPIO.PULL_UP)

    def wait_for_button(self, block=True):
        """Waits for any button to release, optionally blocking if block=True.
        Returns the button that was released, or None if nonblocking.
        """
        # Loop until all buttons are released (if currently pressed)
        while self.enter.value() == PRESSED or self.page.value() == PRESSED:
            wdt.feed()
            self.entropy += 1

        # Wait for first button press
        checks = 0
        while self.enter.value() == RELEASED and self.page.value() == RELEASED:
            wdt.feed()
            checks += 1
            if not block and checks > NONBLOCKING_CHECKS:
                break

        if self.enter.value() == PRESSED:
            # Wait for release
            while self.enter.value() == PRESSED:
                wdt.feed()
                self.entropy += 1
            return BUTTON_ENTER

        if self.page.value() == PRESSED:
            # Wait for release
            while self.page.value() == PRESSED:
                wdt.feed()
                self.entropy += 1
            return BUTTON_PAGE
        return None
