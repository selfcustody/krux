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

import math
import time
import lcd
from ..krux_settings import t
from ..themes import theme
from ..input import (
    BUTTON_ENTER,
    BUTTON_PAGE,
    BUTTON_PAGE_PREV,
    SWIPE_RIGHT,
    SWIPE_LEFT,
    FAST_FORWARD,
    FAST_BACKWARD,
    PRESSED,
)
from ..display import DEFAULT_PADDING, MINIMAL_PADDING, FONT_HEIGHT, FONT_WIDTH

FIXED_KEYS = 3  # 'More' key only appears when there are multiple keysets


class Keypad:
    """Controls keypad creation and management"""

    def __init__(self, ctx, keysets, possible_keys_fn=None):
        self.ctx = ctx
        self.keysets = keysets
        self.keyset_index = 0
        self.key_h_spacing, self.key_v_spacing = self.map_keys_array(
            self.width, self.height
        )
        self.cur_key_index = 0
        self.moving_forward = True
        self.possible_keys_fn = possible_keys_fn
        self.possible_keys = self.keys

    @property
    def keys(self):
        """Returns the current set of keys being displayed"""
        return self.keysets[self.keyset_index]

    @property
    def total_keys(self):
        """Returns the total number of keys in the current keyset, including fixed"""
        return len(self.keys) + FIXED_KEYS + (1 if len(self.keysets) > 1 else 0)

    @property
    def more_index(self):
        """Returns the index of the "More" key"""
        if len(self.keysets) > 1:
            return self.del_index - 1
        return None

    @property
    def del_index(self):
        """Returns the index of the "Del" key"""
        return len(self.keys) + self.empty_keys + (1 if len(self.keysets) > 1 else 0)

    @property
    def esc_index(self):
        """Returns the index of the "Esc" key"""
        return self.del_index + 1

    @property
    def go_index(self):
        """Returns the index of the "Go" key"""
        return self.esc_index + 1

    @property
    def width(self):
        """Returns the needed width for the current keyset"""
        return math.floor(math.sqrt(self.total_keys))

    @property
    def height(self):
        """Returns the needed height for the current keyset"""
        return math.ceil((self.total_keys) / self.width)

    @property
    def max_index(self):
        """Returns last possible key index"""
        return self.width * self.height

    @property
    def empty_keys(self):
        """Returns dummy keys space needed to always position fixed keys at bottom right"""
        return self.max_index - self.total_keys

    def reset(self):
        """Reset parameters when switching a multi-keypad"""
        self.key_h_spacing, self.key_v_spacing = self.map_keys_array(
            self.width, self.height
        )
        self.cur_key_index = 0
        self.possible_keys = self.keys
        self.moving_forward = True

    def map_keys_array(self, width, height):
        """Maps an array of regions for keys to be placed in
        Returns horizontal and vertical spacing of keys
        """
        self.y_keypad_map = []
        self.x_keypad_map = []
        key_h_spacing = self.ctx.display.width() - DEFAULT_PADDING
        key_h_spacing //= width
        key_v_spacing = (
            self.ctx.display.height() - DEFAULT_PADDING - self.keypad_offset()
        )
        key_v_spacing //= height
        for y in range(height + 1):
            region = y * key_v_spacing + self.keypad_offset()
            self.y_keypad_map.append(region)
        for x in range(width + 1):
            region = x * key_h_spacing + MINIMAL_PADDING
            self.x_keypad_map.append(region)
        if self.ctx.input.touch is not None:
            self.ctx.input.touch.y_regions = self.y_keypad_map
            self.ctx.input.touch.x_regions = self.x_keypad_map
        return key_h_spacing, key_v_spacing

    def keypad_offset(self):
        """Returns keypad start position"""
        return DEFAULT_PADDING + FONT_HEIGHT * 3

    def compute_possible_keys(self, buffer):
        """Computes the possible keys for the current keypad"""
        if self.possible_keys_fn is not None:
            self.possible_keys = self.possible_keys_fn(buffer)

    def draw_keys(self):
        """Draws keypad on the screen"""
        key_index = 0
        for y in self.y_keypad_map[:-1]:
            offset_y = y + (self.key_v_spacing - FONT_HEIGHT) // 2
            for x in self.x_keypad_map[:-1]:
                key = None
                custom_color = None
                if key_index < len(self.keys):
                    key = self.keys[key_index]
                elif key_index == self.del_index:
                    key = "<"
                    custom_color = theme.del_color
                elif key_index == self.esc_index:
                    key = t("Esc")
                    custom_color = theme.no_esc_color
                elif key_index == self.go_index:
                    key = t("Go")
                    custom_color = theme.go_color
                elif key_index == self.more_index and len(self.keysets) > 1:
                    key = "ABC"
                    custom_color = theme.toggle_color
                if key is not None:
                    offset_x = x
                    key_offset_x = (self.key_h_spacing - lcd.string_width_px(key)) // 2
                    key_offset_x += offset_x
                    if (
                        key_index < len(self.keys)
                        and self.keys[key_index] not in self.possible_keys
                    ):
                        # faded text
                        self.ctx.display.draw_string(
                            key_offset_x, offset_y, key, theme.disabled_color
                        )
                    else:
                        if self.ctx.input.touch is not None:
                            self.ctx.display.outline(
                                offset_x + 1,
                                y + 1,
                                self.key_h_spacing - 2,
                                self.key_v_spacing - 2,
                                theme.frame_color,
                            )
                        if custom_color:
                            self.ctx.display.draw_string(
                                key_offset_x, offset_y, key, custom_color
                            )
                        else:
                            self.ctx.display.draw_string(key_offset_x, offset_y, key)
                    if (
                        key_index == self.cur_key_index
                        and self.ctx.input.buttons_active
                    ):
                        if self.ctx.input.touch is not None:
                            self.ctx.display.outline(
                                offset_x + 1,
                                y + 1,
                                self.key_h_spacing - 2,
                                self.key_v_spacing - 2,
                            )
                        else:
                            self.ctx.display.outline(
                                offset_x - 2,
                                y,
                                self.key_h_spacing + 1,
                                self.key_v_spacing - 1,
                            )
                key_index += 1

    def draw_keyset_index(self):
        """Indicates the current keyset index with a small circle"""
        if len(self.keysets) == 1:
            return
        bar_height = FONT_HEIGHT // 6
        bar_length = FONT_WIDTH
        bar_padding = FONT_WIDTH // 3
        x_offset = (
            self.ctx.display.width() - (bar_length + bar_padding) * len(self.keysets)
        ) // 2
        for i in range(len(self.keysets)):
            color = theme.fg_color if i == self.keyset_index else theme.frame_color
            self.ctx.display.fill_rectangle(
                x_offset + (bar_length + bar_padding) * i,
                self.y_keypad_map[-1] + 2,
                bar_length,
                bar_height,
                color,
            )

    def get_valid_index(self):
        """Moves current index to a valid position"""
        while (
            self.cur_key_index < len(self.keys)
            and self.keys[self.cur_key_index] not in self.possible_keys
        ):
            if self.moving_forward:
                self.cur_key_index = (self.cur_key_index + 1) % self.max_index
                # Jump over empty keys
                if 0 <= (self.cur_key_index - len(self.keys)) < self.empty_keys:
                    self.cur_key_index += self.empty_keys
            else:
                if self.cur_key_index:
                    self.cur_key_index -= 1
                else:
                    self.cur_key_index = self.max_index - 1
        return self.cur_key_index

    def touch_to_physical(self):
        """Convert a touch press in button press"""
        self.cur_key_index = self.ctx.input.touch.current_index()
        actual_button = None
        if self.cur_key_index < len(self.keys):
            if self.keys[self.cur_key_index] in self.possible_keys:
                actual_button = BUTTON_ENTER
        elif self.cur_key_index < self.max_index:
            actual_button = BUTTON_ENTER
        else:
            self.cur_key_index = 0
        return actual_button

    def navigate(self, btn):
        """Groups navigation methods in one place"""
        if btn == BUTTON_PAGE:
            self._next_key()
        elif btn == BUTTON_PAGE_PREV:
            self._previous_key()
        elif btn == SWIPE_LEFT:
            self.next_keyset()
        elif btn == SWIPE_RIGHT:
            self.previous_keyset()
        elif btn == FAST_FORWARD:
            while self.ctx.input.page_value() == PRESSED:
                self._next_key()
                self.get_valid_index()
                self._clean_keypad_area()
                self.draw_keys()
                time.sleep_ms(100)
        elif btn == FAST_BACKWARD:
            while self.ctx.input.page_prev_value() == PRESSED:
                self._previous_key()
                self.get_valid_index()
                self._clean_keypad_area()
                self.draw_keys()
                time.sleep_ms(100)

    def _clean_keypad_area(self):
        self.ctx.display.fill_rectangle(
            0,
            self.keypad_offset(),
            self.ctx.display.width(),
            self.ctx.display.height() - self.keypad_offset(),
            theme.bg_color,
        )

    def _next_key(self):
        """Increments cursor when page button is pressed"""
        self.moving_forward = True
        self.cur_key_index = (self.cur_key_index + 1) % self.max_index
        if self.cur_key_index == len(self.keys):
            self.cur_key_index += self.empty_keys

    def _previous_key(self):
        """Decrements cursor when page_prev button is pressed"""
        self.moving_forward = False
        if self.cur_key_index == len(self.keys) + self.empty_keys:
            self.cur_key_index = len(self.keys) - 1
        else:
            self.cur_key_index = (self.cur_key_index - 1) % self.max_index

    def next_keyset(self):
        """Change keys for the next keyset"""
        if len(self.keysets) > 1:
            self.keyset_index = (self.keyset_index + 1) % len(self.keysets)
            self.reset()

    def previous_keyset(self):
        """Change keys for the previous keyset"""
        if len(self.keysets) > 1:
            self.keyset_index = (self.keyset_index - 1) % len(self.keysets)
            self.reset()
