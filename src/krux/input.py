# The MIT License (MIT)

# Copyright (c) 2021-2023 Krux contributors

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
from .wdt import wdt
from .buttons import PRESSED, RELEASED

BUTTON_ENTER = 0
BUTTON_PAGE = 1
BUTTON_PAGE_PREV = 2
BUTTON_TOUCH = 3
SWIPE_RIGHT = 4
SWIPE_LEFT = 5
SWIPE_UP = 6
SWIPE_DOWN = 7
ACTIVATING_BUTTONS = 8  # Won't trigger actions, just indicates buttons can used

QR_ANIM_PERIOD = 300  # milliseconds
LONG_PRESS_PERIOD = 1000  # milliseconds

BUTTON_WAIT_PRESS_DELAY = 10
DEBOUNCE = 100


class Input:
    """Input is a singleton interface for interacting with the device's buttons"""

    def __init__(self):
        self.entropy = 0
        self.debounce_time = 0
        self.flushed_flag = False

        self.enter = None
        if "BUTTON_A" in board.config["krux"]["pins"]:
            from .buttons import ButtonEnter

            self.enter = ButtonEnter(board.config["krux"]["pins"]["BUTTON_A"])

        self.page = None
        self.page_prev = None
        if "ENCODER" in board.config["krux"]["pins"]:
            from .rotary import EncoderPage, EncoderPagePrev

            self.page = EncoderPage()
            self.page_prev = EncoderPagePrev()
        else:
            if "BUTTON_B" in board.config["krux"]["pins"]:
                from .buttons import ButtonPage

                self.page = ButtonPage(board.config["krux"]["pins"]["BUTTON_B"])

            if "BUTTON_C" in board.config["krux"]["pins"]:
                from .buttons import ButtonPagePrev

                self.page_prev = ButtonPagePrev(
                    board.config["krux"]["pins"]["BUTTON_C"]
                )
            else:
                try:
                    from pmu import PMU_Button

                    self.page_prev = PMU_Button()
                except ImportError:
                    pass

        # This flag, used in selection outlines, is set if buttons are being used
        self.buttons_active = True
        self.touch = None
        if (
            "touch" in board.config["krux"]["display"]
            and board.config["krux"]["display"]["touch"]
        ):
            from .touch import Touch

            self.touch = Touch(
                board.config["lcd"]["width"],
                board.config["lcd"]["height"],
                board.config["krux"]["pins"]["TOUCH_IRQ"],
            )
            self.buttons_active = False

    def enter_value(self):
        """Intermediary method to pull button ENTER state"""
        if self.enter is not None:
            return self.enter.value()
        return RELEASED

    def page_value(self):
        """Intermediary method to pull button PAGE state"""
        if self.page is not None:
            return self.page.value()
        return RELEASED

    def page_prev_value(self):
        """Intermediary method to pull button PAGE_PREV state"""
        if self.page_prev is not None:
            return self.page_prev.value()
        return RELEASED

    def touch_value(self):
        """Intermediary method to pull touch state, if touch available"""
        if self.touch is not None:
            return self.touch.value()
        return RELEASED

    def enter_event(self):
        """Intermediary method to pull button ENTER event"""
        if self.enter is not None:
            return self.enter.event()
        return False

    def page_event(self):
        """Intermediary method to pull button PAGE event"""
        if self.page is not None:
            return self.page.event()
        return False

    def page_prev_event(self):
        """Intermediary method to pull button PAGE_PREV event"""
        if self.page_prev is not None:
            return self.page_prev.event()
        return False

    def touch_event(self):
        """Intermediary method to pull button TOUCH event"""
        if self.touch is not None:
            return self.touch.event()
        return False

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

    def swipe_up_value(self):
        """Intermediary method to pull touch gesture, if touch available"""
        if self.touch is not None:
            return self.touch.swipe_up_value()
        return RELEASED

    def swipe_down_value(self):
        """Intermediary method to pull touch gesture, if touch available"""
        if self.touch is not None:
            return self.touch.swipe_down_value()
        return RELEASED

    def wdt_feed_inc_entropy(self):
        """Feeds the watchdog and increments the input's entropy"""
        self.entropy += 1
        wdt.feed()

    def _wait_for_press(self, block=True, wait_duration=QR_ANIM_PERIOD):
        """
        Wait for first button press or for wait_duration ms.
        Use block to wait indefinitely
        Do not use this method outside of input module, use wait_for_button instead
        """
        start_time = time.ticks_ms()
        if self.flushed_flag:
            self.debounce_time = 0
        while time.ticks_ms() < self.debounce_time + DEBOUNCE:
            self.flush_events()
        if not self.flushed_flag or block:
            # Makes sure events that happened between pages load are cleared.
            # On animated pages, where block=False, intermediary events must be checked,
            # so events won't be cleared after flushed_flag is set
            self.flush_events()
            self.flushed_flag = not block

        while True:
            if self.enter_event():
                return BUTTON_ENTER
            if self.page_event():
                return BUTTON_PAGE
            if self.page_prev_event():
                return BUTTON_PAGE_PREV
            if self.touch_event():
                return BUTTON_TOUCH

            self.wdt_feed_inc_entropy()

            if not block and time.ticks_ms() > start_time + wait_duration:
                return None

            time.sleep_ms(BUTTON_WAIT_PRESS_DELAY)

    def wait_for_button(self, block=True, wait_duration=QR_ANIM_PERIOD):
        """Waits for any button to release, optionally blocking if block=True.
        Returns the button that was released, or None if non blocking.
        """
        btn = self._wait_for_press(block, wait_duration)

        if btn == BUTTON_ENTER:
            # Wait for release
            while self.enter_value() == PRESSED:
                self.wdt_feed_inc_entropy()
            if not self.buttons_active:
                self.buttons_active = True
                btn = ACTIVATING_BUTTONS

        elif btn == BUTTON_PAGE:
            start_time = time.ticks_ms()
            # Wait for release
            while self.page_value() == PRESSED:
                self.wdt_feed_inc_entropy()
                if time.ticks_ms() > start_time + LONG_PRESS_PERIOD:
                    btn = SWIPE_LEFT
                    break
            if not self.buttons_active:
                self.buttons_active = True
                btn = ACTIVATING_BUTTONS
        elif btn == BUTTON_PAGE_PREV:
            start_time = time.ticks_ms()
            # Wait for release
            while self.page_prev_value() == PRESSED:
                self.wdt_feed_inc_entropy()
                if time.ticks_ms() > start_time + LONG_PRESS_PERIOD:
                    btn = SWIPE_RIGHT
                    break
            if not self.buttons_active:
                self.buttons_active = True
                btn = ACTIVATING_BUTTONS
        elif btn == BUTTON_TOUCH:
            # Wait for release
            while self.touch_value() == PRESSED:
                self.wdt_feed_inc_entropy()
            self.buttons_active = False
            if self.swipe_right_value() == PRESSED:
                btn = SWIPE_RIGHT
            if self.swipe_left_value() == PRESSED:
                btn = SWIPE_LEFT
            if self.swipe_up_value() == PRESSED:
                btn = SWIPE_UP
            if self.swipe_down_value() == PRESSED:
                btn = SWIPE_DOWN
        self.debounce_time = time.ticks_ms()
        return btn

    def flush_events(self):
        """Clean eventual event flags unintentionally collected"""
        self.enter_event()
        self.page_event()
        self.page_prev_event()
        self.touch_event()
