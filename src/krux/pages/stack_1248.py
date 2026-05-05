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

from embit.wordlists.bip39 import WORDLIST
from . import Page
from ..themes import theme
from ..krux_settings import t
from ..display import DEFAULT_PADDING, MINIMAL_PADDING, FONT_HEIGHT, FONT_WIDTH
from ..input import (
    BUTTON_ENTER,
    BUTTON_PAGE,
    BUTTON_PAGE_PREV,
    BUTTON_TOUCH,
    FAST_FORWARD,
    FAST_BACKWARD,
)
from ..kboard import kboard

STACKBIT_GO_INDEX = 38
STACKBIT_ESC_INDEX = 35
STACKBIT_MAX_INDEX = 13
BIT_WEIGHTS = (1, 2, 4, 8)
BIT_LABELS = ("1", "2", "4", "8")

# Vertical 1248 input grid dimensions
VERT_N_DIGITS = 4  # columns — one per BIP39 digit
VERT_N_BITS = 4  # rows — one per bit weight (1, 2, 4, 8)
VERT_N_CELLS = VERT_N_DIGITS * VERT_N_BITS  # 16 selectable grid cells
VERT_ESC_INDEX = VERT_N_CELLS  # 16 — first touch index of Esc button
VERT_GO_INDEX = VERT_N_CELLS + 2  # 18 — first touch index of Go button
# The first digit of a BIP39 index is at most 2; bit weights 4 and 8 are
# therefore unreachable for column 0.  Those cells are shaded and skipped.
VERT_INVALID_CELLS = frozenset({VERT_N_DIGITS * 2, VERT_N_DIGITS * 3})  # {8, 12}


class Stackbit(Page):
    """Class for handling Stackbit 1248 fomat"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.x_offset = DEFAULT_PADDING
        self.x_pad = 2 * FONT_WIDTH
        self.y_offset = 2 * FONT_HEIGHT
        self.y_pad = FONT_HEIGHT

    def _draw_labels(self, y_offset, word_index):
        """Draws labels for import and export Stackbit 1248 UI"""
        index_x_offset = self.x_offset + self.x_pad // 2 - 1
        y_offset += (self.y_pad - FONT_HEIGHT) // 2
        if len(str(word_index)) > 1:
            index_x_offset -= FONT_WIDTH
        self.ctx.display.draw_string(
            index_x_offset,
            y_offset + self.y_pad // 2,
            str(word_index),
            theme.fg_color,
            theme.disabled_color,
        )
        numbers_offset = self.x_offset + self.x_pad
        numbers_offset += (self.x_pad - FONT_WIDTH) // 2
        upper_numbers = [1, 1, 2, 1, 2, 1, 2]
        lower_numbers = [2, 4, 8, 4, 8, 4, 8]
        for x in range(len(upper_numbers)):
            self.ctx.display.draw_string(
                numbers_offset,
                y_offset,
                str(upper_numbers[x]),
                theme.fg_color,
            )
            self.ctx.display.draw_string(
                numbers_offset,
                y_offset + self.y_pad,
                str(lower_numbers[x]),
                theme.fg_color,
            )
            numbers_offset += self.x_pad

    def _draw_grid(self, y_offset):
        """Draws grid for import and export Stackbit 1248 UI"""
        y_offset -= 2
        x_bar_offset = self.x_offset
        # Horizontal lines
        width = 8 * self.x_pad + FONT_WIDTH // 2
        height = 2 * self.y_pad + 2
        grid_x_offset = x_bar_offset - FONT_WIDTH // 2

        # Word_num background
        self.ctx.display.fill_rectangle(
            grid_x_offset,
            y_offset,
            self.x_pad + FONT_WIDTH // 2,
            height,
            theme.disabled_color,
        )

        # top line
        self.ctx.display.draw_line(
            grid_x_offset,
            y_offset,
            grid_x_offset + width,
            y_offset,
            theme.frame_color,
        )
        # bottom line
        self.ctx.display.draw_line(
            grid_x_offset,
            y_offset + height,
            grid_x_offset + width,
            y_offset + height,
            theme.frame_color,
        )
        # Vertical lines
        # Left v line
        self.ctx.display.draw_line(
            grid_x_offset,
            y_offset,
            grid_x_offset,
            y_offset + height,
            theme.frame_color,
        )
        # Second left vertical line
        x_bar_offset += self.x_pad
        self.ctx.display.draw_line(
            x_bar_offset,
            y_offset,
            x_bar_offset,
            y_offset + height,
            theme.frame_color,
        )
        x_bar_offset += self.x_pad
        # Next 4 vertical lines
        for _ in range(4):
            self.ctx.display.draw_line(
                x_bar_offset,
                y_offset,
                x_bar_offset,
                y_offset + height,
                theme.frame_color,
            )
            x_bar_offset += 2 * self.x_pad

    def _word_to_digits(self, word):
        """Converts words to its dictionary position as 4 digit numbers"""
        word_list_index = WORDLIST.index(word) + 1
        word_list_index_str = str(word_list_index)
        while len(word_list_index_str) < 4:
            word_list_index_str = "0" + word_list_index_str
        return [int(x) for x in str(word_list_index_str)], word_list_index_str

    def _draw_punched(self, digits, y_offset):
        """Draws punched bits for import and export Stackbit UI"""
        outline_width = self.x_pad - 6
        outline_height = self.y_pad - 4
        outline_x_offset = self.x_offset + self.x_pad + 3

        if digits[0] == 2:
            self.ctx.display.outline(
                outline_x_offset,
                y_offset + self.y_pad + 1,
                outline_width,
                outline_height,
                theme.highlight_color,
            )
        elif digits[0] == 1:
            self.ctx.display.outline(
                outline_x_offset,
                y_offset + 1,
                outline_width,
                outline_height,
                theme.highlight_color,
            )
        outline_x_offset += self.x_pad
        for x in range(3):
            if (digits[x + 1] >> 3) & 1:
                self.ctx.display.outline(
                    outline_x_offset + self.x_pad,
                    y_offset + self.y_pad + 1,
                    outline_width,
                    outline_height,
                    theme.highlight_color,
                )
            if (digits[x + 1] >> 2) & 1:
                self.ctx.display.outline(
                    outline_x_offset,
                    y_offset + self.y_pad + 1,
                    outline_width,
                    outline_height,
                    theme.highlight_color,
                )
            if (digits[x + 1] >> 1) & 1:
                self.ctx.display.outline(
                    outline_x_offset + self.x_pad,
                    y_offset + 1,
                    outline_width,
                    outline_height,
                    theme.highlight_color,
                )
            if digits[x + 1] & 1:
                self.ctx.display.outline(
                    outline_x_offset,
                    y_offset + 1,
                    outline_width,
                    outline_height,
                    theme.highlight_color,
                )
            outline_x_offset += 2 * self.x_pad

    def export_1248(self, word_index, y_offset, word):
        """Draws punch pattern for Stackbit 1248 seed layout"""

        self.x_offset = DEFAULT_PADDING if not kboard.is_m5stickv else MINIMAL_PADDING
        self.x_pad = 2 * FONT_WIDTH
        self.y_offset = 2 * FONT_HEIGHT
        self.y_pad = FONT_HEIGHT

        self.ctx.display.draw_hcentered_text("Stackbit 1248")
        self._draw_grid(y_offset)
        self._draw_labels(y_offset, word_index)
        digits, digits_str = self._word_to_digits(word)
        self._draw_punched(digits, y_offset)
        if not kboard.is_m5stickv:
            self.ctx.display.draw_string(
                self.x_offset + 17 * FONT_WIDTH,
                y_offset,
                digits_str,
                theme.highlight_color,
            )
            self.ctx.display.draw_string(
                self.x_offset + 17 * FONT_WIDTH,
                y_offset + self.y_pad,
                word,
                theme.disabled_color,
            )

    def _toggle_bit(self, digits, index):
        """Toggle bit state according to pressed index"""
        index_to_digit_bit = [
            [0, 0],
            [1, 0],
            [1, 1],
            [2, 0],
            [2, 1],
            [3, 0],
            [3, 1],
            [0, 1],
            [1, 2],
            [1, 3],
            [2, 2],
            [2, 3],
            [3, 2],
            [3, 3],
        ]
        if index < 14:
            digit, bit = index_to_digit_bit[index]
            digits[digit] = digits[digit] ^ (1 << bit)

            # sanity check
            if digit == 0 and digits[0] > 2:
                digits[0] = 1 << bit
            elif digit != 0 and digits[digit] > 9:
                digits[digit] = 1 << bit

        return digits

    def _draw_index(self, index):
        """Outline index respective"""
        x_offset = self.x_offset + self.x_pad + 1
        width = 3 * self.x_pad
        y_position = index // 7
        y_position *= self.y_pad
        y_position += self.y_offset - 1
        color = theme.fg_color
        if index >= STACKBIT_GO_INDEX:
            x_position = x_offset + 3 * self.x_pad
            y_position += 1
            color = theme.go_color
        elif index >= STACKBIT_ESC_INDEX:
            x_position = x_offset
            y_position += 1
            color = theme.no_esc_color
        else:
            x_position = index % 7
            x_position *= self.x_pad
            x_position += x_offset
            width = self.x_pad - 2
        self.ctx.display.outline(
            x_position,
            y_position,
            width,
            self.y_pad,
            color,
        )

    def _draw_menu(self):
        """Draws options to leave and proceed"""
        y_offset = self.y_offset + 5 * self.y_pad
        label_y_offset = (self.y_pad - FONT_HEIGHT) // 2
        x_offset = self.x_offset + self.x_pad
        self.ctx.display.draw_string(
            x_offset + 1 * self.x_pad,
            y_offset + label_y_offset,
            t("Esc"),
            theme.no_esc_color,
        )
        self.ctx.display.draw_string(
            round(x_offset + 4.2 * self.x_pad),
            y_offset + label_y_offset,
            t("Go"),
            theme.go_color,
        )
        # print border around buttons only on touch devices
        if kboard.has_touchscreen:
            self.ctx.display.draw_line(
                x_offset,
                y_offset,
                x_offset + 6 * self.x_pad,
                y_offset,
                theme.frame_color,
            )
            self.ctx.display.draw_line(
                x_offset,
                y_offset + self.y_pad,
                x_offset + 6 * self.x_pad,
                y_offset + self.y_pad,
                theme.frame_color,
            )
            for _ in range(3):
                self.ctx.display.draw_line(
                    x_offset,
                    y_offset,
                    x_offset,
                    y_offset + self.y_pad,
                    theme.frame_color,
                )
                x_offset += 3 * self.x_pad

    def export_1248_vertical_compact(
        self, words_list, y_start
    ):  # pylint: disable=too-many-locals
        """Draws compact Stackbit 1248 grids for minimal displays, 2 words per row"""
        n_word_cols = 2
        n_cols_per_word = 4
        word_col_gap = 4
        row_gap = 3
        header_h = FONT_HEIGHT

        label_w = FONT_WIDTH
        x_start = MINIMAL_PADDING
        right_pad = MINIMAL_PADDING

        available_w = (
            self.ctx.display.width() - x_start - label_w - word_col_gap - right_pad
        )
        cell_w = available_w // (n_word_cols * n_cols_per_word)

        n_rows = (len(words_list) + n_word_cols - 1) // n_word_cols
        available_h = self.ctx.display.height() - y_start
        cell_h = (available_h - n_rows * header_h - (n_rows - 1) * row_gap) // (
            n_rows * 4
        )
        cell_h = min(cell_h, FONT_HEIGHT)

        grid_w = n_cols_per_word * cell_w
        row_total_h = header_h + 4 * cell_h

        dot_size = max(min(cell_w, cell_h) - 6, 1)
        radius = dot_size // 2

        x_label = x_start
        x_grid_left = x_label + label_w
        x_grid_right = x_grid_left + grid_w + word_col_gap

        for row_idx in range(n_rows):
            word_pair = words_list[row_idx * n_word_cols : (row_idx + 1) * n_word_cols]
            y_row = y_start + row_idx * (row_total_h + row_gap)
            y_grid = y_row + header_h  # grid starts below the header
            grid_h = 4 * cell_h

            # Word-number headers
            for col_idx, (word_idx, _) in enumerate(word_pair):
                x_grid = x_grid_left if col_idx == 0 else x_grid_right
                self.ctx.display.fill_rectangle(
                    x_grid, y_row, grid_w, header_h, theme.disabled_color
                )
                x_num = x_grid + (grid_w - 2 * FONT_WIDTH) // 2
                self.ctx.display.draw_string(
                    x_num,
                    y_row,
                    "%02d" % word_idx,
                    theme.fg_color,
                    theme.disabled_color,
                )

            # Row labels
            for bit_row, label in enumerate(BIT_LABELS):
                self.ctx.display.draw_string(
                    x_label,
                    y_grid + bit_row * cell_h,
                    label,
                    theme.fg_color,
                )

            for col_idx, (_, word) in enumerate(word_pair):
                x_grid = x_grid_left if col_idx == 0 else x_grid_right

                # Outer grid border
                self.ctx.display.draw_line(
                    x_grid, y_grid, x_grid + grid_w, y_grid, theme.frame_color
                )
                self.ctx.display.draw_line(
                    x_grid,
                    y_grid + grid_h,
                    x_grid + grid_w,
                    y_grid + grid_h,
                    theme.frame_color,
                )
                self.ctx.display.draw_line(
                    x_grid, y_grid, x_grid, y_grid + grid_h, theme.frame_color
                )
                self.ctx.display.draw_line(
                    x_grid + grid_w,
                    y_grid,
                    x_grid + grid_w,
                    y_grid + grid_h,
                    theme.frame_color,
                )

                # Internal vertical column dividers
                for c in range(1, n_cols_per_word):
                    x_line = x_grid + c * cell_w
                    self.ctx.display.draw_line(
                        x_line, y_grid, x_line, y_grid + grid_h, theme.frame_color
                    )

                # Internal horizontal row dividers
                for r in range(1, 4):
                    y_line = y_grid + r * cell_h
                    self.ctx.display.draw_line(
                        x_grid, y_line, x_grid + grid_w, y_line, theme.frame_color
                    )

                # Punched marks
                digits, _ = self._word_to_digits(word)
                for col, d in enumerate(digits):
                    x_col = x_grid + col * cell_w
                    for bit_row, bit_val in enumerate(BIT_WEIGHTS):
                        if d & bit_val:
                            x_dot = x_col + (cell_w - dot_size) // 2
                            y_dot = y_grid + bit_row * cell_h + (cell_h - dot_size) // 2
                            self.ctx.display.fill_rectangle(
                                x_dot,
                                y_dot,
                                dot_size,
                                dot_size,
                                theme.highlight_color,
                                radius,
                            )

    def export_1248_vertical_grouped(
        self, y_offset, words_group
    ):  # pylint: disable=too-many-locals
        """Draws grouped Stackbit 1248 grids with individual bordered sections per word"""
        if kboard.is_m5stickv:
            self.x_offset = MINIMAL_PADDING
        else:
            self.x_offset = DEFAULT_PADDING

        n_words = len(words_group)
        n_cols_per_word = 4
        n_gaps = n_words - 1
        word_gap = 4

        label_w = FONT_WIDTH + 2
        available = self.ctx.display.width() - self.x_offset - DEFAULT_PADDING - label_w
        cell_w = (available - n_gaps * word_gap) // (n_words * n_cols_per_word)
        cell_h = FONT_HEIGHT
        header_h = FONT_HEIGHT

        word_block_w = n_cols_per_word * cell_w
        word_stride = word_block_w + word_gap

        x_label = self.x_offset
        x_grid0 = x_label + label_w
        grid_h = 4 * cell_h
        y_grid = y_offset + header_h

        # Row labels
        for i, label in enumerate(BIT_LABELS):
            self.ctx.display.draw_string(
                x_label, y_grid + i * cell_h, label, theme.fg_color
            )

        # Per-word header and grid
        for i, (word_idx, _) in enumerate(words_group):
            x_sec = x_grid0 + i * word_stride

            # Header background with centred word number
            self.ctx.display.fill_rectangle(
                x_sec, y_offset, word_block_w, header_h, theme.disabled_color
            )
            x_num = x_sec + (word_block_w - 2 * FONT_WIDTH) // 2
            self.ctx.display.draw_string(
                x_num, y_offset, "%02d" % word_idx, theme.fg_color, theme.disabled_color
            )

            # Outer border of this word's grid
            self.ctx.display.draw_line(
                x_sec, y_grid, x_sec + word_block_w, y_grid, theme.frame_color
            )
            self.ctx.display.draw_line(
                x_sec,
                y_grid + grid_h,
                x_sec + word_block_w,
                y_grid + grid_h,
                theme.frame_color,
            )
            self.ctx.display.draw_line(
                x_sec, y_grid, x_sec, y_grid + grid_h, theme.frame_color
            )
            self.ctx.display.draw_line(
                x_sec + word_block_w,
                y_grid,
                x_sec + word_block_w,
                y_grid + grid_h,
                theme.frame_color,
            )

            # Vertical column dividers
            for col in range(1, n_cols_per_word):
                x_line = x_sec + col * cell_w
                self.ctx.display.draw_line(
                    x_line, y_grid, x_line, y_grid + grid_h, theme.frame_color
                )

            # Horizontal row dividers
            if i == 0:
                for row in range(1, 4):
                    y_line = y_grid + row * cell_h
                    for j in range(n_words):
                        xs = x_grid0 + j * word_stride
                        self.ctx.display.draw_line(
                            xs, y_line, xs + word_block_w, y_line, theme.frame_color
                        )

        # Punched marks
        dot_size = max(min(cell_w, cell_h) - 6, 1)
        radius = dot_size // 2

        for w_i, (_, word) in enumerate(words_group):
            x_sec = x_grid0 + w_i * word_stride
            digits, _ = self._word_to_digits(word)
            for col, d in enumerate(digits):
                x_col = x_sec + col * cell_w
                for row_idx, bit_val in enumerate(BIT_WEIGHTS):
                    if d & bit_val:
                        x_dot = x_col + (cell_w - dot_size) // 2
                        y_dot = y_grid + row_idx * cell_h + (cell_h - dot_size) // 2
                        self.ctx.display.fill_rectangle(
                            x_dot,
                            y_dot,
                            dot_size,
                            dot_size,
                            theme.highlight_color,
                            radius,
                        )

        # Code and word name below each section
        y_text = y_grid + grid_h + 2
        for i, (_, word) in enumerate(words_group):
            x_sec = x_grid0 + i * word_stride
            _, digits_str = self._word_to_digits(word)
            self.ctx.display.draw_string(
                x_sec, y_text, digits_str, theme.highlight_color
            )
            self.ctx.display.draw_string(
                x_sec, y_text + FONT_HEIGHT, word, theme.disabled_color
            )

    def digits_to_word(self, digits):
        """Returns seed word respective to digits BIP39 dictionaty position"""
        word_number = int("".join(str(num) for num in digits))
        if 0 < word_number <= 2048:
            return WORDLIST[word_number - 1]
        return None

    def preview_word(self, digits):
        """Draws word respective to current state"""
        preview_string = "".join(str(num) for num in digits)
        color = theme.error_color
        word = self.digits_to_word(digits)
        if word is not None:
            preview_string += ": " + word
            color = theme.fg_color
        y_offset = self.y_offset + 3 * self.y_pad
        self.ctx.display.draw_hcentered_text(
            preview_string, y_offset, color=color, highlight_prefix=":"
        )

    def _map_keys_array(self):
        """Maps an array of regions for keys to be placed in"""
        if kboard.has_touchscreen:
            self.ctx.input.touch.clear_regions()
            x_region = self.x_offset + self.x_pad
            for _ in range(8):
                self.ctx.input.touch.x_regions.append(x_region)
                x_region += self.x_pad
            y_region = self.y_offset
            for _ in range(7):
                self.ctx.input.touch.y_regions.append(y_region)
                y_region += self.y_pad

    def index(self, index, btn):
        """Calculates new index according to button press"""
        page_move = [7, 2, 8, 4, 10, 6, 12, 1, 9, 3, 11, 5, 13]
        page_prev_move = [STACKBIT_GO_INDEX, 7, 1, 9, 3, 11, 5, 0, 2, 8, 4, 10, 6, 12]
        if btn in (BUTTON_PAGE, FAST_FORWARD):
            if index >= STACKBIT_GO_INDEX:
                return 0
            if index >= STACKBIT_ESC_INDEX:
                return STACKBIT_GO_INDEX
            if index >= STACKBIT_MAX_INDEX:
                return STACKBIT_ESC_INDEX
            return page_move[index]
        if btn in (BUTTON_PAGE_PREV, FAST_BACKWARD):
            if index <= 0:
                return STACKBIT_GO_INDEX
            if index <= STACKBIT_MAX_INDEX:
                return page_prev_move[index]
            if index <= STACKBIT_ESC_INDEX:
                return STACKBIT_MAX_INDEX
        return STACKBIT_ESC_INDEX

    def enter_1248(self):
        """UI to manually enter a Stackbit 1248"""
        if not kboard.is_m5stickv:
            self.x_pad = 3 * FONT_WIDTH
        else:
            self.x_pad = 2 * FONT_WIDTH
        self.x_offset = self.ctx.display.width()
        self.x_offset -= 8 * self.x_pad
        self.x_offset = max(self.x_offset, DEFAULT_PADDING)
        self.x_offset //= 2
        self.y_offset = 3 * FONT_HEIGHT
        self.y_pad = 2 * FONT_HEIGHT
        index = 0
        digits = [0, 0, 0, 0]
        word_index = 1
        words = []
        while word_index <= 24:
            self._map_keys_array()
            self.ctx.display.draw_hcentered_text("Stackbit 1248")
            y_offset = self.y_offset
            self._draw_grid(y_offset)
            self._draw_labels(y_offset, word_index)
            self._draw_menu()
            if self.ctx.input.buttons_active:
                self._draw_index(index)
            self.preview_word(digits)
            self._draw_punched(digits, y_offset)
            btn = self.ctx.input.wait_for_fastnav_button()
            if btn == BUTTON_TOUCH:
                btn = BUTTON_ENTER
                index = self.ctx.input.touch.current_index()
            if btn == BUTTON_ENTER:
                if index >= STACKBIT_GO_INDEX:  # go
                    word = self.digits_to_word(digits)
                    if word is not None:
                        prompt_str = (
                            str(word_index)
                            + ".\n\n"
                            + "".join(str(num) for num in digits)
                            + ": "
                            + str(word)
                            + "\n\n"
                        )
                        digits = [0, 0, 0, 0]
                        index = 0
                        self.ctx.display.clear()
                        if self.prompt(
                            prompt_str,
                            self.ctx.display.height() // 2,
                            highlight_prefix=":",
                        ):
                            words.append(word)
                        else:
                            self.ctx.display.clear()
                            continue
                        if word_index == 12:
                            self.ctx.display.clear()
                            if self.prompt(t("Done?"), self.ctx.display.height() // 2):
                                break
                            # self._map_keys_array() #can be removed?
                        word_index += 1
                elif index >= STACKBIT_ESC_INDEX:  # ESC
                    self.ctx.display.clear()
                    if self.prompt(t("Are you sure?"), self.ctx.display.height() // 2):
                        break
                    # self._map_keys_array()
                elif index < 14:
                    digits = self._toggle_bit(digits, index)
            else:
                index = self.index(index, btn)
            self.ctx.display.clear()
        if len(words) in (12, 24):
            return words
        return None

    # ------------------------------------------------------------------
    # Vertical 1248 input — 4 × 4 grid (digits × bit-weights)
    # ------------------------------------------------------------------

    def _layout_vertical(self):
        """Return geometry constants for the vertical input grid.

        All positions are derived from two base measures so the layout
        scales cleanly across Amigo (320×480), Dock (240×320) and
        M5StickV (135×240).
        """
        pad = DEFAULT_PADDING
        label_w = (
            FONT_WIDTH + DEFAULT_PADDING
        )  # breathing room between border and labels
        gap = FONT_HEIGHT // 2

        # Cell size: widest square that fits the available width, capped at
        # 2 × FONT_HEIGHT so cells don't become oversized on tall screens.
        available_w = self.ctx.display.width() - 2 * pad - label_w
        cell_w = available_w // VERT_N_DIGITS
        max_cell_h = (self.ctx.display.height() - 4 * FONT_HEIGHT - pad - gap) // (
            VERT_N_BITS + 1
        )
        cell_size = min(cell_w, max(max_cell_h, FONT_HEIGHT), 2 * FONT_HEIGHT)

        grid_w = VERT_N_DIGITS * cell_size
        grid_h = VERT_N_BITS * cell_size

        # Center the full block (labels + grid) horizontally on the display
        total_w = label_w + grid_w
        x_label = max(pad, (self.ctx.display.width() - total_w) // 2)
        x_grid = x_label + label_w

        # Layout order (top → bottom):
        #   title line · word-number badge · grid · gap · preview line · menu row
        # Single preview line mirrors the standard horizontal mode style:
        # "1244: opinion" with highlight_prefix=":" coloring the word.
        total_h = 2 * FONT_HEIGHT + grid_h + gap + FONT_HEIGHT + cell_size
        y_start = max(pad, (self.ctx.display.height() - total_h) // 2)
        y_grid = y_start + 2 * FONT_HEIGHT
        y_preview = y_grid + grid_h + gap
        y_menu = y_preview + FONT_HEIGHT

        return (
            x_grid,
            y_grid,
            y_start,
            y_menu,
            cell_size,
            cell_size,
            grid_w,
            x_label,
            y_preview,
        )

    def _map_keys_array_vertical(self, x_grid, y_grid, cell_w, cell_h, y_menu):
        """Set touch regions for the 4 × 4 grid plus the Esc / Go menu row."""
        if not kboard.has_touchscreen:
            return
        self.ctx.input.touch.clear_regions()
        x = x_grid
        for _ in range(VERT_N_DIGITS + 1):
            self.ctx.input.touch.x_regions.append(x)
            x += cell_w
        y = y_grid
        for _ in range(VERT_N_BITS):
            self.ctx.input.touch.y_regions.append(y)
            y += cell_h
        self.ctx.input.touch.y_regions.append(y_menu)
        self.ctx.input.touch.y_regions.append(y_menu + cell_h)

    def _draw_grid_vertical(self, x_grid, y_grid, cell_w, cell_h, grid_w):
        """Draw the 4 × 4 cell borders, shading invalid cells in column 0."""
        grid_h = VERT_N_BITS * cell_h
        # Outer border
        self.ctx.display.draw_line(
            x_grid, y_grid, x_grid + grid_w, y_grid, theme.frame_color
        )
        self.ctx.display.draw_line(
            x_grid, y_grid + grid_h, x_grid + grid_w, y_grid + grid_h, theme.frame_color
        )
        self.ctx.display.draw_line(
            x_grid, y_grid, x_grid, y_grid + grid_h, theme.frame_color
        )
        self.ctx.display.draw_line(
            x_grid + grid_w, y_grid, x_grid + grid_w, y_grid + grid_h, theme.frame_color
        )
        # Internal column dividers
        for col in range(1, VERT_N_DIGITS):
            x = x_grid + col * cell_w
            self.ctx.display.draw_line(x, y_grid, x, y_grid + grid_h, theme.frame_color)
        # Internal row dividers
        for row in range(1, VERT_N_BITS):
            y = y_grid + row * cell_h
            self.ctx.display.draw_line(x_grid, y, x_grid + grid_w, y, theme.frame_color)
        # Shade cells that are structurally unreachable (first digit, rows 2-3)
        for row in range(2, VERT_N_BITS):
            self.ctx.display.fill_rectangle(
                x_grid, y_grid + row * cell_h, cell_w, cell_h, theme.disabled_color
            )

    def _draw_punched_vertical(self, digits, x_grid, y_grid, cell_w, cell_h):
        """Draw filled squares for every bit that is set in the current digits."""
        dot_size = max(min(cell_w, cell_h) * 2 // 3, 1)
        radius = dot_size // 2
        for col, digit in enumerate(digits):
            x_col = x_grid + col * cell_w
            for row, bit_val in enumerate(BIT_WEIGHTS):
                if digit & bit_val:
                    x_dot = x_col + (cell_w - dot_size) // 2
                    y_dot = y_grid + row * cell_h + (cell_h - dot_size) // 2
                    self.ctx.display.fill_rectangle(
                        x_dot, y_dot, dot_size, dot_size, theme.highlight_color, radius
                    )

    def _draw_menu_vertical(self, x_grid, y_menu, grid_w, cell_h):
        """Draw the Esc and Go buttons below the grid."""
        label_y = y_menu + (cell_h - FONT_HEIGHT) // 2
        half_w = grid_w // 2
        esc_label = t("Esc")
        go_label = t("Go")
        esc_x = x_grid + (half_w - len(esc_label) * FONT_WIDTH) // 2
        go_x = x_grid + half_w + (half_w - len(go_label) * FONT_WIDTH) // 2
        self.ctx.display.draw_string(esc_x, label_y, esc_label, theme.no_esc_color)
        self.ctx.display.draw_string(go_x, label_y, go_label, theme.go_color)
        if kboard.has_touchscreen:
            mid = x_grid + half_w
            self.ctx.display.draw_line(
                x_grid, y_menu, x_grid + grid_w, y_menu, theme.frame_color
            )
            self.ctx.display.draw_line(
                x_grid,
                y_menu + cell_h,
                x_grid + grid_w,
                y_menu + cell_h,
                theme.frame_color,
            )
            self.ctx.display.draw_line(
                x_grid, y_menu, x_grid, y_menu + cell_h, theme.frame_color
            )
            self.ctx.display.draw_line(
                mid, y_menu, mid, y_menu + cell_h, theme.frame_color
            )
            self.ctx.display.draw_line(
                x_grid + grid_w,
                y_menu,
                x_grid + grid_w,
                y_menu + cell_h,
                theme.frame_color,
            )

    def _draw_index_vertical(
        self, index, x_grid, y_grid, cell_w, cell_h, y_menu, grid_w
    ):
        """Outline the currently focused cell or menu button."""
        if index >= VERT_GO_INDEX:
            x = x_grid + grid_w // 2
            self.ctx.display.outline(x, y_menu, grid_w // 2, cell_h, theme.go_color)
        elif index >= VERT_ESC_INDEX:
            self.ctx.display.outline(
                x_grid, y_menu, grid_w // 2, cell_h, theme.no_esc_color
            )
        else:
            col = index % VERT_N_DIGITS
            row = index // VERT_N_DIGITS
            self.ctx.display.outline(
                x_grid + col * cell_w,
                y_grid + row * cell_h,
                cell_w,
                cell_h,
                theme.fg_color,
            )

    def _toggle_bit_vertical(self, digits, index):
        """Toggle the bit addressed by *index*, enforcing first-digit constraints.

        The first BIP39 digit is 0-2, so bit weights 4 (row 2) and 8 (row 3)
        are invalid for column 0 and are silently ignored.
        """
        if index in VERT_INVALID_CELLS:
            return digits
        col = index % VERT_N_DIGITS
        row = index // VERT_N_DIGITS
        bit_val = BIT_WEIGHTS[row]
        new_val = digits[col] ^ bit_val
        if col == 0 and new_val > 2:
            # Clamp: keep only the toggled bit, drop the rest
            new_val = bit_val if digits[col] == 0 else 0
        elif col != 0 and new_val > 9:
            new_val = bit_val if digits[col] == 0 else 0
        digits[col] = new_val
        return digits

    def _index_vertical(self, index, btn):
        """Advance or rewind the focused cell index, skipping invalid cells."""
        if btn in (BUTTON_PAGE, FAST_FORWARD):
            index = 0 if index >= VERT_GO_INDEX else index + 1
            if index in VERT_INVALID_CELLS:
                index += 1
        elif btn in (BUTTON_PAGE_PREV, FAST_BACKWARD):
            index = VERT_GO_INDEX if index <= 0 else index - 1
            if index in VERT_INVALID_CELLS:
                index -= 1
        return index

    def enter_1248_vertical(self):
        """UI to manually enter a seed from a vertical Stackbit 1248 card."""
        x_grid, y_grid, y_start, y_menu, cell_w, cell_h, grid_w, x_label, y_preview = (
            self._layout_vertical()
        )
        index = 0
        digits = [0, 0, 0, 0]
        word_index = 1
        words = []
        while word_index <= 24:
            self._map_keys_array_vertical(x_grid, y_grid, cell_w, cell_h, y_menu)
            self.ctx.display.draw_hcentered_text("Stackbit 1248", y_start)
            self.ctx.display.fill_rectangle(
                x_grid, y_start + FONT_HEIGHT, grid_w, FONT_HEIGHT, theme.disabled_color
            )
            self.ctx.display.draw_string(
                x_grid + (grid_w - 2 * FONT_WIDTH) // 2,
                y_start + FONT_HEIGHT,
                "%02d" % word_index,
                theme.fg_color,
                theme.disabled_color,
            )
            for i, label in enumerate(BIT_LABELS):
                self.ctx.display.draw_string(
                    x_label, y_grid + i * cell_h, label, theme.fg_color
                )
            self._draw_grid_vertical(x_grid, y_grid, cell_w, cell_h, grid_w)
            self._draw_menu_vertical(x_grid, y_menu, grid_w, cell_h)
            if self.ctx.input.buttons_active:
                self._draw_index_vertical(
                    index, x_grid, y_grid, cell_w, cell_h, y_menu, grid_w
                )
            digits_str = "".join(str(d) for d in digits)
            word = self.digits_to_word(digits)
            if word is not None:
                preview_str = digits_str + ": " + word
                color = theme.fg_color
            else:
                preview_str = digits_str
                color = theme.error_color
            self.ctx.display.draw_hcentered_text(
                preview_str, y_preview, color=color, highlight_prefix=":"
            )
            self._draw_punched_vertical(digits, x_grid, y_grid, cell_w, cell_h)
            btn = self.ctx.input.wait_for_fastnav_button()
            if btn == BUTTON_TOUCH:
                btn = BUTTON_ENTER
                index = self.ctx.input.touch.current_index()
            if btn == BUTTON_ENTER:
                if index >= VERT_GO_INDEX:
                    word = self.digits_to_word(digits)
                    if word is not None:
                        prompt_str = (
                            str(word_index)
                            + ".\n\n"
                            + "".join(str(d) for d in digits)
                            + ": "
                            + str(word)
                            + "\n\n"
                        )
                        digits = [0, 0, 0, 0]
                        index = 0
                        self.ctx.display.clear()
                        if self.prompt(
                            prompt_str,
                            self.ctx.display.height() // 2,
                            highlight_prefix=":",
                        ):
                            words.append(word)
                        else:
                            self.ctx.display.clear()
                            continue
                        if word_index == 12:
                            self.ctx.display.clear()
                            if self.prompt(t("Done?"), self.ctx.display.height() // 2):
                                break
                        word_index += 1
                elif index >= VERT_ESC_INDEX:
                    self.ctx.display.clear()
                    if self.prompt(t("Are you sure?"), self.ctx.display.height() // 2):
                        break
                else:
                    digits = self._toggle_bit_vertical(digits, index)
            else:
                index = self._index_vertical(index, btn)
            self.ctx.display.clear()
        if len(words) in (12, 24):
            return words
        return None
