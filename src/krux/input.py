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
import time
import board
from .wdt import wdt
from .auto_shutdown import auto_shutdown
from .buttons import PRESSED, RELEASED
from .krux_settings import Settings
from .kboard import kboard

BUTTON_ENTER = 0
BUTTON_PAGE = 1
BUTTON_PAGE_PREV = 2
BUTTON_TOUCH = 3
SWIPE_RIGHT = 4
SWIPE_LEFT = 5
SWIPE_UP = 6
SWIPE_DOWN = 7
FAST_FORWARD = 8
FAST_BACKWARD = 9

# A button was pressed, but the previous state was a touch (sometimes prevents triggering an action)
ACTIVATING_BUTTONS = 999

# Release must be confirmed X times
BUTTON_RELEASE_FILTER = 10 if kboard.need_release_filter else 1

QR_ANIM_PERIOD = 300  # milliseconds
LONG_PRESS_PERIOD = 1000  # milliseconds
KEY_REPEAT_DELAY_MS = 100

BUTTON_WAIT_PRESS_DELAY = 10
ONE_MINUTE = 60000


class Input:
    """Input is a singleton interface for interacting with the device's buttons"""

    def __init__(self):
        self.entropy = 0  # used only to pick a random final word
        self.debounce_value = Settings().hardware.buttons.debounce
        self.debounce_time = 0
        self.flushed_flag = False

        self.enter = None
        if "BUTTON_A" in board.config["krux"]["pins"]:
            from .buttons import ButtonEnter

            self.enter = ButtonEnter(board.config["krux"]["pins"]["BUTTON_A"])

        self.page = None
        self.page_prev = None
        if kboard.has_encoder:
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
        if kboard.has_touchscreen:
            from .touch import Touch

            self.touch = Touch(
                board.config["lcd"]["width"],
                board.config["lcd"]["height"],
                board.config["krux"]["pins"]["TOUCH_IRQ"],
                board.config["krux"]["pins"].get("TOUCH_RESET", None),
            )
            self.buttons_active = False
        self.button_integrity_check()

    def button_integrity_check(self):
        """
        Check buttons state, if one of them is pressed at boot time it will assume it is
        damaged and will disable it to avoid a single button to freeze the interface.
        """
        if self.enter and self.enter_value() == PRESSED:
            self.enter = None
        if self.page and self.page_value() == PRESSED:
            self.page = None
        if self.page_prev and self.page_prev_value() == PRESSED:
            self.page_prev = None
        if self.touch and self.touch_value() == PRESSED:
            self.touch = None
            kboard.has_touchscreen = None

    def enter_value(self):
        """Intermediary method to pull button ENTER state"""
        if self.enter is not None:
            wdt.feed()
            return self.enter.value()
        return RELEASED

    def page_value(self):
        """Intermediary method to pull button PAGE state"""
        if self.page is not None:
            wdt.feed()
            return self.page.value()
        return RELEASED

    def page_prev_value(self):
        """Intermediary method to pull button PAGE_PREV state"""
        if self.page_prev is not None:
            wdt.feed()
            return self.page_prev.value()
        return RELEASED

    def touch_value(self):
        """Intermediary method to pull touch state, if touch available"""
        if kboard.has_touchscreen:
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

    def touch_event(self, validate_position=True):
        """Intermediary method to pull button TOUCH event"""
        if kboard.has_touchscreen:
            return self.touch.event(validate_position)
        return False

    def swipe_right_value(self):
        """Intermediary method to pull touch gesture, if touch available"""
        if kboard.has_touchscreen:
            return self.touch.swipe_right_value()
        return RELEASED

    def swipe_left_value(self):
        """Intermediary method to pull touch gesture, if touch available"""
        if kboard.has_touchscreen:
            return self.touch.swipe_left_value()
        return RELEASED

    def swipe_up_value(self):
        """Intermediary method to pull touch gesture, if touch available"""
        if kboard.has_touchscreen:
            return self.touch.swipe_up_value()
        return RELEASED

    def swipe_down_value(self):
        """Intermediary method to pull touch gesture, if touch available"""
        if kboard.has_touchscreen:
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
        # Disable debounce if in animated pages, except menu
        disable_debounce = (
            self.flushed_flag and not block and wait_duration < ONE_MINUTE
        )
        if disable_debounce:
            self.debounce_time = 0
        while time.ticks_ms() < self.debounce_time + self.debounce_value:
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
                if kboard.is_yahboom:
                    return BUTTON_PAGE
                return BUTTON_PAGE_PREV
            if self.touch_event():
                return BUTTON_TOUCH

            self.wdt_feed_inc_entropy()

            if not block and time.ticks_ms() > start_time + wait_duration:
                return None

            time.sleep_ms(BUTTON_WAIT_PRESS_DELAY)

    def wait_for_release(self):
        """Waits for all buttons to be released"""
        while (
            self.enter_value() == PRESSED
            or self.page_value() == PRESSED
            or self.page_prev_value() == PRESSED
            or self.touch_value() == PRESSED
        ):
            time.sleep_ms(BUTTON_WAIT_PRESS_DELAY)
            self.wdt_feed_inc_entropy()

    def _detect_press_type(self, btn):
        """Detects the type of press and returns the appropriate button value"""

        def _handle_button_press(btn):
            press_start_time = time.ticks_ms()
            if kboard.is_cube:
                time.sleep_ms(200)  # Stabilization time for cube
            release_filter = _get_release_filter(btn)
            while release_filter:
                if _button_still_pressed(btn):
                    release_filter = _get_release_filter(btn)
                else:
                    release_filter -= 1
                self.wdt_feed_inc_entropy()
                if time.ticks_ms() > press_start_time + LONG_PRESS_PERIOD:
                    if not self.buttons_active:
                        self.buttons_active = True
                    return _map_long_press(btn)
                time.sleep_ms(BUTTON_WAIT_PRESS_DELAY)

            if not self.buttons_active:
                self.buttons_active = True
                return ACTIVATING_BUTTONS
            return btn

        def _get_release_filter(btn):
            """Returns the appropriate release filter for the button"""
            if btn in [BUTTON_PAGE, BUTTON_PAGE_PREV] and kboard.has_encoder:
                return 0
            return BUTTON_RELEASE_FILTER

        def _button_still_pressed(btn):
            if btn == BUTTON_ENTER:
                return self.enter_value() == PRESSED
            if btn == BUTTON_PAGE:
                val = self.page_value() == PRESSED
                if kboard.is_yahboom and self.page_prev_value() == PRESSED:
                    return True
                return val
            # if btn == BUTTON_PAGE_PREV:
            return self.page_prev_value() == PRESSED

        def _map_long_press(btn):
            if btn == BUTTON_ENTER:
                return SWIPE_LEFT
            if btn == BUTTON_PAGE:
                return FAST_FORWARD
            # if btn == BUTTON_PAGE_PREV:
            return FAST_BACKWARD

        def _handle_touch_input():
            while self.touch_value() == PRESSED:
                self.wdt_feed_inc_entropy()
            self.buttons_active = False
            if self.swipe_right_value() == PRESSED:
                return SWIPE_RIGHT
            if self.swipe_left_value() == PRESSED:
                return SWIPE_LEFT
            if self.swipe_up_value() == PRESSED:
                return SWIPE_UP
            if self.swipe_down_value() == PRESSED:
                return SWIPE_DOWN
            return BUTTON_TOUCH

        if btn in [BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV]:
            btn = _handle_button_press(btn)
        elif btn == BUTTON_TOUCH:
            btn = _handle_touch_input()

        return btn

    def wait_for_button(self, block=True, wait_duration=QR_ANIM_PERIOD):
        """Waits for any button to release, optionally blocking if block=True.
        Returns the button that was released, or None if non blocking.
        """
        self.wait_for_release()
        btn = self._wait_for_press(block, wait_duration)
        if btn is not None:
            auto_shutdown.feed()
        btn = self._detect_press_type(btn)
        self.debounce_time = time.ticks_ms()
        return btn

    def wait_for_fastnav_button(self, block=True, wait_duration=QR_ANIM_PERIOD):
        """Wait for a button press, with support for fast navigation."""
        if self.page_value() == PRESSED:
            time.sleep_ms(KEY_REPEAT_DELAY_MS)
            return FAST_FORWARD
        if self.page_prev_value() == PRESSED:
            time.sleep_ms(KEY_REPEAT_DELAY_MS)
            if kboard.is_yahboom:
                return FAST_FORWARD
            return FAST_BACKWARD
        return self.wait_for_button(block, wait_duration)

    def flush_events(self):
        """Clean eventual event flags unintentionally collected"""
        self.enter_event()
        self.page_event()
        self.page_prev_event()
        self.touch_event()

    def reset_ios_state(self):
        """Clears all events and reset debounce time"""
        self.flush_events()
        self.debounce_time = time.ticks_ms()
