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
import lcd
from ..krux_settings import t
from ..themes import theme
from ..input import (
    BUTTON_ENTER,
    BUTTON_PAGE,
    BUTTON_PAGE_PREV,
    SWIPE_RIGHT,
    SWIPE_LEFT,
    SWIPE_UP,
    SWIPE_DOWN,
    FAST_FORWARD,
    FAST_BACKWARD,
)
from ..display import DEFAULT_PADDING, MINIMAL_PADDING, FONT_HEIGHT, FONT_WIDTH
from ..kboard import kboard

FIXED_KEYS = 3  # 'More' key only appears when there are multiple keysets.

QR_GLYPH = (
    "11101100111",
    "10101000101",
    "11101010111",
    "00000010000",
    "10110110110",
    "01001101001",
    "10110010100",
    "00001001110",
    "11100101011",
    "10101011110",
    "11100110101",
)


class KeypadLayout:
    """Groups layout-related attributes for Keypad."""

    def __init__(self, ctx, max_keys_count):
        self.width = math.floor(math.sqrt(max_keys_count))
        self.height = math.ceil(max_keys_count / self.width)
        self.max_index = self.width * self.height

        key_h_spacing = ctx.display.width() - DEFAULT_PADDING
        key_h_spacing //= self.width
        key_v_spacing = (
            ctx.display.height() - DEFAULT_PADDING - (DEFAULT_PADDING + FONT_HEIGHT * 3)
        )
        key_v_spacing //= self.height
        self.key_h_spacing, self.key_v_spacing = key_h_spacing, key_v_spacing

        self.y_keypad_map = [
            y * key_v_spacing + (DEFAULT_PADDING + FONT_HEIGHT * 3)
            for y in range(self.height + 1)
        ]
        self.x_keypad_map = [0]
        for x in range(1, self.width):
            self.x_keypad_map.append(x * key_h_spacing + MINIMAL_PADDING)
        self.x_keypad_map.append(ctx.display.width())
        if kboard.has_touchscreen:
            ctx.input.touch.set_regions(self.x_keypad_map, self.y_keypad_map)


class Keypad:
    """Controls keypad creation and management."""

    def __init__(self, ctx, keysets, possible_keys_fn=None, has_scan_key=False):
        self.ctx = ctx
        self.keysets = keysets
        self.keyset_index = 0
        self._has_scan_key = has_scan_key
        max_keys_count = max(
            len(keyset)
            + FIXED_KEYS
            + (1 if len(keysets) > 1 else 0)
            + (1 if has_scan_key and index == len(keysets) - 1 else 0)
            for index, keyset in enumerate(keysets)
        )
        self.layout = KeypadLayout(ctx, max_keys_count)
        self.cur_key_index = 0
        self.moving_forward = True
        self.possible_keys_fn = possible_keys_fn
        self.possible_keys = self.keys
        self._qr_glyph_cache_key = None
        self._qr_glyph_image = None

    @property
    def keys(self):
        """Returns the current set of keys being displayed"""
        return self.keysets[self.keyset_index]

    @property
    def total_keys(self):
        """Returns the total number of keys in the current keyset, including fixed"""
        return (
            len(self.keys) + FIXED_KEYS + self.count_more_key() + self.count_scan_key()
        )

    def has_scan_key(self):
        """Whether the QR scan key is available in the current keyset."""
        return self._has_scan_key and self.keyset_index == len(self.keysets) - 1

    def count_scan_key(self):
        """Count 1 if the QR scan key is available in the current keyset."""
        return 1 if self.has_scan_key() else 0

    @property
    def more_index(self):
        """Returns the index of the "More" key"""
        if self.has_more_key():
            return self.del_index - 1
        return None

    @property
    def scan_index(self):
        """Returns the index of the QR scan key."""
        if self.has_scan_key():
            return self.del_index - self.count_more_key() - 1
        return None

    @property
    def del_index(self):
        """Returns the index of the "Del" key"""
        return (
            len(self.keys)
            + self.empty_keys
            + self.count_more_key()
            + self.count_scan_key()
        )

    def has_more_key(self):
        """If keypad has "ABC" key"""
        return len(self.keysets) > 1

    def count_more_key(self):
        """Count 1 if has the more key"""
        return 1 if self.has_more_key() else 0

    @property
    def esc_index(self):
        """Returns the index of the "Esc" key"""
        return self.del_index + 1

    @property
    def go_index(self):
        """Returns the index of the "Go" key"""
        return self.esc_index + 1

    @property
    def empty_keys(self):
        """Returns dummy keys space needed to always position fixed keys at bottom right"""
        return self.layout.max_index - self.total_keys

    def reset(self):
        """Reset parameters when switching a multi-keypad"""
        self.cur_key_index = 0
        self.possible_keys = self.keys
        self.moving_forward = True

    def compute_possible_keys(self, buffer):
        """Computes the possible keys for the current keypad"""
        if self.possible_keys_fn is not None:
            self.possible_keys = self.possible_keys_fn(buffer)

    def draw_keys(self):
        """Draws keypad on the screen"""
        key_index = 0
        for y in self.layout.y_keypad_map[:-1]:
            offset_y = y + (self.layout.key_v_spacing - FONT_HEIGHT) // 2
            for x in self.layout.x_keypad_map[:-1]:
                x = MINIMAL_PADDING if x == 0 else x
                key = None
                is_scan_key = False
                custom_color = None
                if key_index < len(self.keys):
                    key = self.keys[key_index]
                elif key_index == self.scan_index:
                    is_scan_key = True
                elif key_index == self.del_index:
                    key = "<"
                    custom_color = theme.del_color
                elif key_index == self.esc_index:
                    key = t("Esc")
                    custom_color = theme.no_esc_color
                elif key_index == self.go_index:
                    key = t("Go")
                    custom_color = theme.go_color
                elif self.has_more_key() and key_index == self.more_index:
                    key = self.keysets[self._move_keyset_index()][:3]
                    custom_color = theme.toggle_color

                if key is not None or is_scan_key:
                    offset_x = x
                    key_offset_x = offset_x
                    if key is not None:
                        key_offset_x = (
                            self.layout.key_h_spacing - lcd.string_width_px(key)
                        ) // 2 + offset_x
                    if (
                        key_index < len(self.keys)
                        and self.keys[key_index] not in self.possible_keys
                    ):
                        # faded text
                        self.ctx.display.draw_string(
                            key_offset_x, offset_y, key, theme.disabled_color
                        )
                    else:
                        if kboard.has_touchscreen:
                            self.ctx.display.outline(
                                offset_x + 1,
                                y + 1,
                                self.layout.key_h_spacing - 2,
                                self.layout.key_v_spacing - 2,
                                theme.frame_color,
                            )
                        if is_scan_key:
                            self.draw_qr_glyph(offset_x, y)
                        elif custom_color:
                            self.ctx.display.draw_string(
                                key_offset_x, offset_y, key, custom_color
                            )
                        else:
                            self.ctx.display.draw_string(key_offset_x, offset_y, key)
                    if (
                        key_index == self.cur_key_index
                        and self.ctx.input.buttons_active
                    ):
                        if kboard.has_touchscreen:
                            self.ctx.display.outline(
                                offset_x + 1,
                                y + 1,
                                self.layout.key_h_spacing - 2,
                                self.layout.key_v_spacing - 2,
                            )
                        else:
                            self.ctx.display.outline(
                                offset_x - 2,
                                y,
                                self.layout.key_h_spacing + 1,
                                self.layout.key_v_spacing - 1,
                            )
                key_index += 1

    def draw_qr_glyph(self, key_x, key_y):
        """Draws the QR scan glyph centered in a keypad cell."""
        import image

        module_size = max(1, FONT_HEIGHT // len(QR_GLYPH))
        glyph_size = len(QR_GLYPH) * module_size
        offset_x = key_x + (self.layout.key_h_spacing - glyph_size) // 2
        offset_y = key_y + (self.layout.key_v_spacing - glyph_size) // 2
        cache_key = (module_size, theme.fg_color, theme.bg_color)
        if getattr(self, "_qr_glyph_cache_key", None) != cache_key:
            glyph_image = image.Image(size=(glyph_size, glyph_size), copy_to_fb=False)
            glyph_image.draw_rectangle(
                0,
                0,
                glyph_size,
                glyph_size,
                theme.bg_color,
                fill=True,
            )
            for row, modules in enumerate(QR_GLYPH):
                column = 0
                while column < len(modules):
                    if modules[column] == "0":
                        column += 1
                        continue
                    run_start = column
                    while column < len(modules) and modules[column] == "1":
                        column += 1
                    glyph_image.draw_rectangle(
                        run_start * module_size,
                        row * module_size,
                        (column - run_start) * module_size,
                        module_size,
                        theme.fg_color,
                        fill=True,
                    )
            self._qr_glyph_cache_key = cache_key
            self._qr_glyph_image = glyph_image
        lcd.display(self._qr_glyph_image, oft=(offset_x, offset_y))

    def draw_keyset_index(self):
        """Indicates the current keyset index with a small rectangle"""
        if not self.has_more_key():
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
                self.layout.y_keypad_map[-1] + 2,
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
                self.cur_key_index = (self.cur_key_index + 1) % self.layout.max_index
                # Jump over empty keys
                if 0 <= (self.cur_key_index - len(self.keys)) < self.empty_keys:
                    self.cur_key_index += self.empty_keys
            else:
                if self.cur_key_index:
                    self.cur_key_index -= 1
                else:
                    self.cur_key_index = self.layout.max_index - 1
        return self.cur_key_index

    def touch_to_physical(self):
        """Convert a touch press in button press"""
        self.cur_key_index = self.ctx.input.touch.current_index()
        actual_button = None
        if self.cur_key_index < len(self.keys):
            if self.keys[self.cur_key_index] in self.possible_keys:
                actual_button = BUTTON_ENTER
        elif self.cur_key_index < self.layout.max_index:
            actual_button = BUTTON_ENTER
        else:
            self.cur_key_index = 0
        return actual_button

    def navigate(self, btn):
        """Groups navigation methods in one place"""
        if btn in (BUTTON_PAGE, FAST_FORWARD):
            self._next_key()
        elif btn in (BUTTON_PAGE_PREV, FAST_BACKWARD):
            self._previous_key()
        elif btn in (SWIPE_UP, SWIPE_LEFT):
            self.next_keyset()
        elif btn in (SWIPE_DOWN, SWIPE_RIGHT):
            self.previous_keyset()

    def _next_key(self):
        """Increments cursor when page button is pressed"""
        self.moving_forward = True
        self.cur_key_index = (self.cur_key_index + 1) % self.layout.max_index
        if self.cur_key_index == len(self.keys):
            self.cur_key_index += self.empty_keys

    def _previous_key(self):
        """Decrements cursor when page_prev button is pressed"""
        self.moving_forward = False
        if self.cur_key_index == len(self.keys) + self.empty_keys:
            self.cur_key_index = len(self.keys) - 1
        else:
            self.cur_key_index = (self.cur_key_index - 1) % self.layout.max_index

    def next_keyset(self):
        """Change keys for the next keyset"""
        if self.has_more_key():
            self.keyset_index = self._move_keyset_index()
            self.reset()

    def previous_keyset(self):
        """Change keys for the previous keyset"""
        if self.has_more_key():
            self.keyset_index = self._move_keyset_index(False)
            self.reset()

    def _move_keyset_index(self, forward=True):
        """Calc the index of keyset forward or backwards"""
        i = 1 if forward else -1
        return (self.keyset_index + i) % len(self.keysets)
