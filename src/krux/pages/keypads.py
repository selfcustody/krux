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

        # Pre-compute cell pixel positions for fast drawing
        self.cell_positions = []
        for row_y in self.y_keypad_map[:-1]:
            for col_x in self.x_keypad_map[:-1]:
                cx = MINIMAL_PADDING if col_x == 0 else col_x
                cy = row_y + (key_v_spacing - FONT_HEIGHT) // 2
                self.cell_positions.append((cx, cy))


class Keypad:
    """Controls keypad creation and management."""

    def __init__(self, ctx, keysets, possible_keys_fn=None):
        self.ctx = ctx
        self.keysets = keysets
        self.keyset_index = 0
        max_keys_count = (
            max(len(keyset) for keyset in keysets)
            + FIXED_KEYS
            + (1 if len(keysets) > 1 else 0)
        )
        self.layout = KeypadLayout(ctx, max_keys_count)
        self.cur_key_index = 0
        self.moving_forward = True
        self.possible_keys_fn = possible_keys_fn
        self.possible_keys = self.keys

        # Pre-compute key labels, x-offsets, and colors for each cell
        self._key_labels = [None] * self.layout.max_index
        self._key_offsets_x = [0] * self.layout.max_index
        self._key_colors = [None] * self.layout.max_index
        self._key_is_letter = [False] * self.layout.max_index
        self._build_key_cache()

    def _build_key_cache(self):
        """Pre-compute key labels, x-offsets, and colors for all cells."""
        keys = self.keys
        layout = self.layout
        for idx in range(layout.max_index):
            key = None
            custom_color = None
            is_letter = False

            if idx < len(keys):
                key = keys[idx]
                is_letter = True
            elif idx == self.del_index:
                key = "<"
                custom_color = theme.del_color
            elif idx == self.esc_index:
                key = t("Esc")
                custom_color = theme.no_esc_color
            elif idx == self.go_index:
                key = t("Go")
                custom_color = theme.go_color
            elif self.has_more_key() and idx == self.more_index:
                key = self.keysets[self._move_keyset_index()][:3]
                custom_color = theme.toggle_color

            self._key_labels[idx] = key
            self._key_is_letter[idx] = is_letter
            self._key_colors[idx] = custom_color
            if key is not None:
                cx, cy = layout.cell_positions[idx]
                self._key_offsets_x[idx] = (
                    layout.key_h_spacing - lcd.string_width_px(key)
                ) // 2 + cx

    @property
    def keys(self):
        """Returns the current set of keys being displayed"""
        return self.keysets[self.keyset_index]

    @property
    def total_keys(self):
        """Returns the total number of keys in the current keyset, including fixed"""
        return len(self.keys) + FIXED_KEYS + self.count_more_key()

    @property
    def more_index(self):
        """Returns the index of the "More" key"""
        if self.has_more_key():
            return self.del_index - 1
        return None

    @property
    def del_index(self):
        """Returns the index of the "Del" key"""
        return len(self.keys) + self.empty_keys + self.count_more_key()

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
        self._build_key_cache()

    def compute_possible_keys(self, buffer):
        """Computes the possible keys for the current keypad"""
        if self.possible_keys_fn is not None:
            self.possible_keys = self.possible_keys_fn(buffer)

    def draw_keys(self):
        """Draws keypad with clean contour style and pre-computed cache."""
        layout = self.layout
        display = self.ctx.display
        cell_w = layout.key_h_spacing
        cell_h = layout.key_v_spacing
        text_half = FONT_HEIGHT // 2
        margin = 2
        radius = min(4, (cell_h - margin * 2) // 4)

        for idx in range(layout.max_index):
            key = self._key_labels[idx]
            if key is None:
                continue

            cx, cy = layout.cell_positions[idx]
            off_x = self._key_offsets_x[idx]
            is_disabled = self._key_is_letter[idx] and key not in self.possible_keys
            is_selected = (
                idx == self.cur_key_index and self.ctx.input.buttons_active
            )

            # Key rectangle position (centered in cell with margin)
            kx = cx - margin
            ky = cy - text_half - margin
            kw = cell_w - margin * 2
            kh = cell_h - margin * 2

            if is_disabled:
                display.outline(kx, ky, kw, kh, theme.disabled_color)
                display.draw_string(off_x, cy, key, theme.disabled_color)
            elif is_selected:
                if kboard.has_touchscreen:
                    display.fill_rectangle(
                        kx, ky, kw, kh, theme.highlight_color, radius
                    )
                    display.draw_string(off_x, cy, key, theme.bg_color)
                else:
                    display.outline(
                        kx - 1, ky - 1, kw + 2, kh + 2, theme.highlight_color
                    )
                    display.outline(kx, ky, kw, kh, theme.highlight_color)
                    display.draw_string(off_x, cy, key, theme.highlight_color)
            else:
                frame_color = (
                    self._key_colors[idx]
                    if self._key_colors[idx]
                    else theme.frame_color
                )
                display.outline(kx, ky, kw, kh, frame_color)
                label_color = (
                    self._key_colors[idx]
                    if self._key_colors[idx]
                    else theme.fg_color
                )
                display.draw_string(off_x, cy, key, label_color)

    def draw_keyset_index(self):
        """Draws keyset indicator with larger, more visible bars."""
        if not self.has_more_key():
            return
        bar_h = FONT_HEIGHT // 4
        bar_w = FONT_WIDTH * 2
        bar_pad = FONT_WIDTH // 2
        n = len(self.keysets)
        x_start = (
            self.ctx.display.width() - (bar_w + bar_pad) * n + bar_pad
        ) // 2
        bar_y = self.layout.y_keypad_map[-1] + 2
        for i in range(n):
            color = theme.fg_color if i == self.keyset_index else theme.frame_color
            self.ctx.display.fill_rectangle(
                x_start + (bar_w + bar_pad) * i,
                bar_y,
                bar_w,
                bar_h,
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
        """Switch to next number/symbol keyset (skipping letter keysets)."""
        if len(self.keysets) > 2:
            if self.keyset_index < 2:
                self.keyset_index = 2
            else:
                self.keyset_index = (self.keyset_index + 1) % len(self.keysets)
                if self.keyset_index < 2:
                    self.keyset_index = 2
            self.reset()

    def previous_keyset(self):
        """Switch to previous number/symbol keyset (skipping letter keysets)."""
        if len(self.keysets) > 2:
            if self.keyset_index < 2:
                self.keyset_index = len(self.keysets) - 1
            else:
                self.keyset_index -= 1
                if self.keyset_index < 2:
                    self.keyset_index = len(self.keysets) - 1
            self.reset()

    def toggle_case(self):
        """Toggle between first two keysets (lowercase <-> uppercase)."""
        if len(self.keysets) >= 2:
            self.keyset_index = 1 if self.keyset_index == 0 else 0
            self.reset()

    def _move_keyset_index(self, forward=True):
        """Calc the index of keyset forward or backwards"""
        i = 1 if forward else -1
        return (self.keyset_index + i) % len(self.keysets)
