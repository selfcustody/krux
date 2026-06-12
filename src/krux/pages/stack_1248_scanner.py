# The MIT License (MIT)
#
# Copyright (c) 2021-2024 Krux contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import lcd
import sensor
import time
from embit.wordlists.bip39 import WORDLIST
from . import Page
from ..krux_settings import t
from ..themes import theme
from ..display import DEFAULT_PADDING, FONT_HEIGHT, FONT_WIDTH
from ..camera import BINARY_GRID_MODE
from ..wdt import wdt
from ..input import (
    BUTTON_ENTER,
    BUTTON_PAGE,
    BUTTON_PAGE_PREV,
    BUTTON_TOUCH,
    FAST_FORWARD,
    FAST_BACKWARD,
)
from ..kboard import kboard
from .stack_1248 import Stackbit, STACKBIT_GO_INDEX, STACKBIT_ESC_INDEX


class StackbitScanner(Page):
    """Uses camera sensor to detect punch pattern on Stackbit 1248 metal plate

    Stackbit 1248 is a metal backup plate for BIP39 seed phrases using
    binary-coded decimal (1-2-4-8) encoding. Each word is represented as
    a 4-digit number (0001-2048).

    Plate specifications:
    - Full plate: 85mm x 54mm (aspect ratio = 1.574), 16x12 grid, 12 words
    - Mini plate: 42.5mm x 54mm (aspect ratio = 0.787), 8x12 grid, 6 words

    Grid layout:
    - Columns 0 (and 8 on full): Word index numbers (skipped during reading)
    - Columns 1 (and 9 on full): Milhar digit (1 or 2)
    - Columns 2-7 (and 10-15 on full): Three pairs of 1-2-4-8 encoding
    """

    # Plate type constants
    PLATE_FULL = "full"  # 85x54mm, 16x12 grid, 12 words
    PLATE_MINI = "mini"  # 42.5x54mm, 8x12 grid, 6 words

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.x_regions = []
        self.y_regions = []
        self.blob_otsu = 0x80
        self.debug_mode = True  # Show visual markers for detected punches
        self.plate_type = self.PLATE_FULL  # Detected plate type

    # pylint: disable=R0914
    def _detect_plate(self, img, force_type=None):
        """Detect the Stackbit 1248 plate as a bright blob

        Args:
            force_type: If set, only detect plates of this type (PLATE_FULL or PLATE_MINI)

        Returns tuple: (rect, plate_type) or (None, None)
        """
        try:
            self.blob_otsu = img.get_histogram().get_threshold().value()
        except:
            pass

        # Use threshold that separates bright plate from dark background
        blob_threshold = [(max(self.blob_otsu - 20, 50), 255)]

        # Use smaller strides for more accurate edge detection
        blobs = img.find_blobs(
            blob_threshold,
            x_stride=5,
            y_stride=5,
            area_threshold=2000,
            pixels_threshold=1500,
            merge=True,
        )

        best_rect = None
        best_score = 0
        best_type = None

        # Aspect ratios for different plate types
        # Full plate: 85 / 54 = 1.574 (landscape)
        # Mini plate: 42.5 / 54 = 0.787 (portrait)
        full_aspect = 1.574
        mini_aspect = 0.787
        aspect_tolerance = 0.35

        img_center_x = img.width() // 2
        img_center_y = img.height() // 2

        for blob in blobs:
            rect = blob.rect()
            if rect[3] == 0 or rect[2] == 0:
                continue

            aspect = rect[2] / rect[3]

            # Check which plate type matches
            plate_type = None
            aspect_diff = 999

            if force_type == self.PLATE_FULL or force_type is None:
                if abs(aspect - full_aspect) < aspect_tolerance:
                    plate_type = self.PLATE_FULL
                    aspect_diff = abs(aspect - full_aspect)

            if force_type == self.PLATE_MINI or force_type is None:
                mini_diff = abs(aspect - mini_aspect)
                if mini_diff < aspect_tolerance and mini_diff < aspect_diff:
                    plate_type = self.PLATE_MINI
                    aspect_diff = mini_diff

            if plate_type is None:
                continue

            # Score based on aspect ratio match
            aspect_score = 1.0 / (1.0 + aspect_diff * 3)

            # Score based on area
            area_score = min(1.0, blob.area() / 15000)

            # Score based on centering
            blob_center_x = rect[0] + rect[2] // 2
            blob_center_y = rect[1] + rect[3] // 2
            dist_from_center = (
                (blob_center_x - img_center_x) ** 2
                + (blob_center_y - img_center_y) ** 2
            ) ** 0.5
            max_dist = (img_center_x**2 + img_center_y**2) ** 0.5
            center_score = 1.0 - (dist_from_center / max_dist)

            # Combined score
            score = aspect_score * 0.5 + area_score * 0.35 + center_score * 0.15

            if score > best_score:
                best_score = score
                best_rect = rect
                best_type = plate_type

        if best_rect:
            self.plate_type = best_type

        return best_rect, best_type

    def _create_grid_over_rect(self, rect, plate_type=None):
        """Create grid regions over detected rectangle

        Args:
            plate_type: PLATE_FULL (16x12) or PLATE_MINI (8x12)
        """
        self.x_regions = []
        self.y_regions = []

        if plate_type is None:
            plate_type = self.plate_type

        x, y, w, h = rect

        # Number of columns depends on plate type
        num_cols = 16 if plate_type == self.PLATE_FULL else 8
        col_width = w / num_cols
        for i in range(num_cols + 1):
            self.x_regions.append(int(x + i * col_width))

        # 12 rows for both plate types
        row_height = h / 12
        for i in range(13):
            self.y_regions.append(int(y + i * row_height))

    def _draw_grid(self, img, rect, plate_type=None):
        """Draw grid overlay on detected rectangle"""
        if plate_type is None:
            plate_type = self.plate_type

        # Draw rectangle outline
        img.draw_rectangle(rect, lcd.WHITE, thickness=2)

        # Draw vertical lines
        for i, x in enumerate(self.x_regions):
            # Thicker lines for word separators
            if plate_type == self.PLATE_FULL:
                thickness = 2 if i in (0, 8) else 1
            else:
                thickness = 2 if i == 0 else 1
            img.draw_line(
                x, rect[1], x, rect[1] + rect[3], lcd.WHITE, thickness=thickness
            )

        # Draw horizontal lines (12 rows)
        for y in self.y_regions:
            img.draw_line(rect[0], y, rect[0] + rect[2], y, lcd.WHITE, thickness=1)

    def _read_cell(self, img, x, y, w, h, draw_debug=False):
        """Read a single cell and return True if punched

        Uses multiple detection methods:
        1. Adaptive threshold (luminance-based)
        2. Circular blob detection (shape-based)
        3. Contrast detection (dark vs light)
        """
        if x < 0 or y < 0 or w <= 0 or h <= 0:
            return False
        if x + w > img.width() or y + h > img.height():
            return False

        try:
            stats = img.get_statistics(roi=(x, y, w, h))
            cell_lum = stats.l_mean()

            is_punched = False

            # Method 1: Adaptive threshold
            relative_threshold = self.blob_otsu - 30
            if cell_lum < relative_threshold:
                is_punched = True

            # Method 2: Circular blob detection
            if not is_punched:
                try:
                    dark_threshold = max(20, cell_lum - 40)
                    blob_threshold = [(0, dark_threshold)]
                    blobs = img.find_blobs(
                        blob_threshold,
                        roi=(x, y, w, h),
                        pixels_threshold=int(w * h * 0.1),
                        area_threshold=int(w * h * 0.08),
                        merge=True,
                    )
                    for blob in blobs:
                        if blob.roundness() > 0.3:
                            is_punched = True
                            break
                except:
                    pass

            # Method 3: High contrast detection
            if not is_punched:
                try:
                    std = stats.l_stdev()
                    if std > 25:
                        is_punched = True
                except:
                    pass

            # Draw debug marker if requested
            if draw_debug and is_punched:
                img.draw_rectangle((x, y, w, h), lcd.BLACK, thickness=2)

            return is_punched
        except:
            return False

    def _create_grid_regions(self, rect, plate_type=None):
        """Create grid over the detected plate

        Args:
            plate_type: PLATE_FULL (16x12) or PLATE_MINI (8x12)

        Returns: (x_regions, y_regions)
        """
        if plate_type is None:
            plate_type = self.plate_type

        x_regions = []
        y_regions = []

        num_cols = 16 if plate_type == self.PLATE_FULL else 8

        x_step = rect[2] / num_cols
        for i in range(num_cols + 1):
            x_regions.append(int(rect[0] + i * x_step))

        y_step = rect[3] / 12
        for i in range(13):
            y_regions.append(int(rect[1] + i * y_step))

        return x_regions, y_regions

    def _read_all_grid_cells(self, img, rect, plate_type=None):
        """Read all grid cells and return a 2D boolean array

        Args:
            plate_type: PLATE_FULL (16x12) or PLATE_MINI (8x12)

        Returns: (grid, x_regions, y_regions)
        """
        if plate_type is None:
            plate_type = self.plate_type

        x_regions, y_regions = self._create_grid_regions(rect, plate_type)
        num_cols = 16 if plate_type == self.PLATE_FULL else 8
        grid = []

        for row_idx in range(12):
            row = []
            y = y_regions[row_idx]
            h = y_regions[row_idx + 1] - y

            # Use centered sampling (70% width, 60% height)
            sample_h = int(h * 0.6)
            sample_y = y + int(h * 0.2)

            for col_idx in range(num_cols):
                x = x_regions[col_idx]
                w = x_regions[col_idx + 1] - x
                sample_w = int(w * 0.7)
                sample_x = x + int(w * 0.15)

                is_punched = self._read_cell(
                    img, sample_x, sample_y, sample_w, sample_h, draw_debug=False
                )
                row.append(is_punched)

            grid.append(row)

        # Filter rounded corner cells (3mm radius causes false detections)
        # Affects the 4 physical corners of the plate
        last_col = num_cols - 1
        grid[0][0] = False
        grid[0][last_col] = False
        grid[11][0] = False
        grid[11][last_col] = False

        return grid, x_regions, y_regions

    def _decode_6_words_from_half(self, grid, col_offset=0):
        """Decode 6 word numbers from one half of the grid

        Args:
            grid: 2D boolean array of punched cells
            col_offset: 0 for left half (cols 0-7), 8 for right half (cols 8-15)

        Returns list of 6 integers (word numbers 1-2048)
        """
        numbers = []

        for word_idx in range(6):
            row_upper = word_idx * 2
            row_lower = word_idx * 2 + 1

            # Column 1 (or 9): Milhar (skip col 0/8 indexer)
            milhar_col = col_offset + 1
            milhar = 0
            if grid[row_upper][milhar_col]:
                milhar = 1
            elif grid[row_lower][milhar_col]:
                milhar = 2

            # Columns 2-7 (or 10-15): Three pairs of 1-2-4-8 encoding
            digits = [milhar]
            for pair_idx in range(3):
                col_left = col_offset + 2 + pair_idx * 2
                col_right = col_offset + 3 + pair_idx * 2

                # Left column: upper=1, lower=4
                # Right column: upper=2, lower=8
                val_1 = 1 if grid[row_upper][col_left] else 0
                val_4 = 4 if grid[row_lower][col_left] else 0
                val_2 = 2 if grid[row_upper][col_right] else 0
                val_8 = 8 if grid[row_lower][col_right] else 0

                digit = val_1 + val_2 + val_4 + val_8
                digits.append(digit)

            number = digits[0] * 1000 + digits[1] * 100 + digits[2] * 10 + digits[3]
            numbers.append(number)

        return numbers

    def _decode_numbers_from_grid(self, grid, plate_type=None):
        """Decode word numbers from the grid

        Args:
            plate_type: PLATE_FULL (12 words) or PLATE_MINI (6 words)

        Returns list of integers (word numbers 1-2048)
        """
        if plate_type is None:
            plate_type = self.plate_type

        if plate_type == self.PLATE_MINI:
            # Mini plate: 8 columns, 6 words (same layout as left half)
            return self._decode_6_words_from_half(grid, col_offset=0)
        # Full plate: 16 columns, 12 words
        numbers = []
        # Left half (words 1-6, columns 0-7)
        numbers.extend(self._decode_6_words_from_half(grid, col_offset=0))
        # Right half (words 7-12, columns 8-15)
        numbers.extend(self._decode_6_words_from_half(grid, col_offset=8))
        return numbers

    # pylint: disable=W0212
    def _edit_single_word(self, word_index, number):
        """Edit a single word using the Stackbit 1248 editor UI

        Reuses the existing Stackbit class for proven input handling.

        Args:
            word_index: Display index of the word (1-based)
            number: Current word number (1-2048)

        Returns:
            New word number if confirmed (Go), or None if cancelled (Esc)
        """
        sb = Stackbit(self.ctx)

        # Setup editor layout (same as enter_1248)
        if not kboard.is_m5stickv:
            sb.x_pad = 3 * FONT_WIDTH
        else:
            sb.x_pad = 2 * FONT_WIDTH
        sb.x_offset = self.ctx.display.width() - 8 * sb.x_pad
        sb.x_offset = max(sb.x_offset, DEFAULT_PADDING) // 2
        sb.y_offset = 3 * FONT_HEIGHT
        sb.y_pad = 2 * FONT_HEIGHT

        index = 0
        # Convert number to digits
        num_str = "{:04d}".format(number)
        digits = [int(c) for c in num_str]

        self.ctx.display.clear()
        while True:
            sb._map_keys_array()
            self.ctx.display.draw_hcentered_text("Edit Word " + str(word_index))
            y_offset = sb.y_offset
            sb._draw_grid(y_offset)
            sb._draw_labels(y_offset, word_index)
            sb._draw_menu()
            if self.ctx.input.buttons_active:
                sb._draw_index(index)
            sb.preview_word(digits)
            sb._draw_punched(digits, y_offset)

            btn = self.ctx.input.wait_for_fastnav_button()
            if btn == BUTTON_TOUCH:
                btn = BUTTON_ENTER
                index = self.ctx.input.touch.current_index()
            if btn == BUTTON_ENTER:
                if index >= STACKBIT_GO_INDEX:
                    word = sb.digits_to_word(digits)
                    if word is not None:
                        return (
                            digits[0] * 1000
                            + digits[1] * 100
                            + digits[2] * 10
                            + digits[3]
                        )
                elif index >= STACKBIT_ESC_INDEX:
                    return None
                elif index < 14:
                    digits = sb._toggle_bit(digits, index)
            else:
                index = sb.index(index, btn)
            self.ctx.display.clear()

    # pylint: disable=R0914,R0912,R0915
    def _show_stackbit_words(self, grid, word_offset=0, plate_type=None):
        """Show decoded words with editing support and Back/Next navigation

        Touch a word to edit it with the 1248 editor.
        Back/Next buttons at footer to navigate pages.

        Args:
            word_offset: Starting word index offset
            plate_type: PLATE_FULL or PLATE_MINI

        Returns:
            List of word numbers (possibly edited) or None if cancelled
        """
        if plate_type is None:
            plate_type = self.plate_type

        numbers = self._decode_numbers_from_grid(grid, plate_type)

        x_offset = DEFAULT_PADDING
        x_pad = 2 * FONT_WIDTH
        y_pad = FONT_HEIGHT
        row_spacing = 6
        row_height = 2 * y_pad + row_spacing

        def draw_word_row(word_idx, number, y_offset):
            """Draw one word row with Stackbit 1248 visual representation"""
            digits = [
                (number // 1000) % 10,
                (number // 100) % 10,
                (number // 10) % 10,
                number % 10,
            ]
            digits_str = "{:04d}".format(number)

            if 1 <= number <= 2048:
                word = WORDLIST[number - 1]
            else:
                word = "????"

            grid_x_offset = x_offset - FONT_WIDTH // 2
            index_x_offset = x_offset + x_pad // 2 - 1
            if len(str(word_idx)) > 1:
                index_x_offset -= FONT_WIDTH

            self.ctx.display.fill_rectangle(
                grid_x_offset,
                y_offset - 2,
                x_pad + FONT_WIDTH // 2,
                2 * y_pad + 2,
                theme.disabled_color,
            )
            self.ctx.display.draw_string(
                index_x_offset,
                y_offset + y_pad // 2,
                str(word_idx),
                theme.fg_color,
                theme.disabled_color,
            )

            numbers_offset = x_offset + x_pad + (x_pad - FONT_WIDTH) // 2
            upper_numbers = [1, 1, 2, 1, 2, 1, 2]
            lower_numbers = [2, 4, 8, 4, 8, 4, 8]
            label_y_offset = y_offset + (y_pad - FONT_HEIGHT) // 2
            for i in range(len(upper_numbers)):
                self.ctx.display.draw_string(
                    numbers_offset,
                    label_y_offset,
                    str(upper_numbers[i]),
                    theme.fg_color,
                )
                self.ctx.display.draw_string(
                    numbers_offset,
                    label_y_offset + y_pad,
                    str(lower_numbers[i]),
                    theme.fg_color,
                )
                numbers_offset += x_pad

            width = 8 * x_pad + FONT_WIDTH // 2
            height = 2 * y_pad + 2
            self.ctx.display.draw_line(
                grid_x_offset,
                y_offset - 2,
                grid_x_offset + width,
                y_offset - 2,
                theme.frame_color,
            )
            self.ctx.display.draw_line(
                grid_x_offset,
                y_offset - 2 + height,
                grid_x_offset + width,
                y_offset - 2 + height,
                theme.frame_color,
            )
            x_bar = x_offset
            self.ctx.display.draw_line(
                grid_x_offset,
                y_offset - 2,
                grid_x_offset,
                y_offset - 2 + height,
                theme.frame_color,
            )
            x_bar += x_pad
            self.ctx.display.draw_line(
                x_bar, y_offset - 2, x_bar, y_offset - 2 + height, theme.frame_color
            )
            x_bar += x_pad
            for _ in range(4):
                self.ctx.display.draw_line(
                    x_bar, y_offset - 2, x_bar, y_offset - 2 + height, theme.frame_color
                )
                x_bar += 2 * x_pad

            outline_width = x_pad - 6
            outline_height = y_pad - 4
            outline_x = x_offset + x_pad + 3
            if digits[0] == 2:
                self.ctx.display.outline(
                    outline_x,
                    y_offset + y_pad + 1,
                    outline_width,
                    outline_height,
                    theme.highlight_color,
                )
            elif digits[0] == 1:
                self.ctx.display.outline(
                    outline_x,
                    y_offset + 1,
                    outline_width,
                    outline_height,
                    theme.highlight_color,
                )
            outline_x += x_pad
            for d in range(3):
                digit = digits[d + 1]
                if (digit >> 3) & 1:
                    self.ctx.display.outline(
                        outline_x + x_pad,
                        y_offset + y_pad + 1,
                        outline_width,
                        outline_height,
                        theme.highlight_color,
                    )
                if (digit >> 2) & 1:
                    self.ctx.display.outline(
                        outline_x,
                        y_offset + y_pad + 1,
                        outline_width,
                        outline_height,
                        theme.highlight_color,
                    )
                if (digit >> 1) & 1:
                    self.ctx.display.outline(
                        outline_x + x_pad,
                        y_offset + 1,
                        outline_width,
                        outline_height,
                        theme.highlight_color,
                    )
                if digit & 1:
                    self.ctx.display.outline(
                        outline_x,
                        y_offset + 1,
                        outline_width,
                        outline_height,
                        theme.highlight_color,
                    )
                outline_x += 2 * x_pad

            self.ctx.display.draw_string(
                x_offset + 17 * FONT_WIDTH, y_offset, digits_str, theme.highlight_color
            )
            self.ctx.display.draw_string(
                x_offset + 17 * FONT_WIDTH, y_offset + y_pad, word, theme.disabled_color
            )

        # Split numbers into pages of 6
        num_words = len(numbers)
        if num_words <= 6:
            title = "Stackbit 1248 Mini"
            pages = [list(numbers)]
            page_offsets = [word_offset]
        else:
            title = "Stackbit 1248"
            pages = [list(numbers[:6]), list(numbers[6:])]
            page_offsets = [word_offset, word_offset + 6]

        current_page = 0

        while True:
            is_first = current_page == 0
            is_last = current_page == len(pages) - 1
            page_nums = pages[current_page]
            num_on_page = len(page_nums)

            # Draw page
            self.ctx.display.clear()
            self.ctx.display.draw_hcentered_text(title)

            y_positions = []
            y_pos = 2 * FONT_HEIGHT
            for i in range(num_on_page):
                draw_word_row(page_offsets[current_page] + i + 1, page_nums[i], y_pos)
                y_positions.append(y_pos)
                y_pos += row_height

            # Draw footer: Back / Next (or Go)
            footer_y = self.ctx.display.height() - FONT_HEIGHT - 4
            if not is_first:
                self.ctx.display.draw_string(
                    x_offset, footer_y, "< " + t("Back"), theme.no_esc_color
                )
            next_label = t("Next") + " >" if not is_last else t("Go") + " >"
            next_color = theme.fg_color if not is_last else theme.go_color
            next_x = self.ctx.display.width() - len(next_label) * FONT_WIDTH - x_offset
            self.ctx.display.draw_string(next_x, footer_y, next_label, next_color)

            # Setup touch regions: 2 columns x (num_on_page + 1) rows
            # Indices: 0..2*num_on_page-1 = word rows, 2*num_on_page = Back, 2*num_on_page+1 = Next
            if kboard.has_touchscreen:
                self.ctx.input.touch.clear_regions()
                mid_x = self.ctx.display.width() // 2
                self.ctx.input.touch.x_regions.append(0)
                self.ctx.input.touch.x_regions.append(mid_x)
                self.ctx.input.touch.x_regions.append(self.ctx.display.width())
                for yp in y_positions:
                    self.ctx.input.touch.y_regions.append(yp - 2)
                self.ctx.input.touch.y_regions.append(footer_y - 4)
                self.ctx.input.touch.y_regions.append(self.ctx.display.height())

            # Wait for input
            btn = self.ctx.input.wait_for_fastnav_button()

            if btn == BUTTON_TOUCH:
                idx = self.ctx.input.touch.current_index()
                row = idx // 2
                col = idx % 2

                if row < num_on_page:
                    # Touch on word row → edit it
                    edited = self._edit_single_word(
                        page_offsets[current_page] + row + 1, page_nums[row]
                    )
                    if edited is not None:
                        pages[current_page][row] = edited
                    # Redraw page (continue loop)
                elif row == num_on_page:
                    # Footer row
                    if col == 0 and not is_first:
                        current_page -= 1
                    else:
                        if is_last:
                            result = []
                            for p in pages:
                                result.extend(p)
                            return result
                        current_page += 1
            elif btn == BUTTON_ENTER:
                if is_last:
                    result = []
                    for p in pages:
                        result.extend(p)
                    return result
                current_page += 1
            elif btn in (BUTTON_PAGE, FAST_FORWARD):
                if is_last:
                    result = []
                    for p in pages:
                        result.extend(p)
                    return result
                current_page += 1
            elif btn in (BUTTON_PAGE_PREV, FAST_BACKWARD):
                if not is_first:
                    current_page -= 1

    def _numbers_to_words(self, numbers):
        """Convert list of word numbers to BIP39 words

        Returns list of words if all valid, None otherwise
        """
        words = []
        for number in numbers:
            if 1 <= number <= 2048:
                words.append(WORDLIST[number - 1])
            else:
                return None
        return words

    # pylint: disable=R0914,R0912,R0915
    def scanner(self, w24=False):
        """Scans the Stackbit 1248 plate with manual trigger

        Automatically detects plate type:
        - Full plate (85x54mm): 12 words at once
        - Mini plate (42.5x54mm): 6 words, requires 2 scans for 12 words

        Args:
            w24: If True, scans for 24 words (front + back of full plate)

        Returns:
            List of 12 or 24 BIP39 words if successfully read, None otherwise
        """
        page = 0  # 0 = first scan, 1 = second scan (for mini or 24-word mode)
        all_words = []
        detected_plate_type = None  # Will be set on first successful detection
        mini_mode = False  # True if using mini plate for 12 words

        self.ctx.display.clear()
        if w24:
            message = (
                t("Position plate") + "\n" + t("Words 1-12") + "\n" + t("Click to read")
            )
        else:
            message = t("Position plate") + "\n" + t("Click to read")
        self.ctx.display.draw_centered_text(message)
        time.sleep(2)

        self.ctx.camera.initialize_run(mode=BINARY_GRID_MODE)
        self.ctx.camera.zoom_mode()
        self.ctx.display.to_landscape()
        self.ctx.display.clear()

        while True:
            wdt.feed()
            img = self.ctx.camera.snapshot()

            # Detect plate - for 24-word mode, force full plate detection
            force_type = self.PLATE_FULL if w24 else None
            rect, plate_type = self._detect_plate(img, force_type)

            if rect and plate_type:
                self._create_grid_over_rect(rect, plate_type)
                self._draw_grid(img, rect, plate_type)

                # Mark detected punches in real-time
                num_cols = 16 if plate_type == self.PLATE_FULL else 8
                for row_idx in range(12):
                    y = self.y_regions[row_idx]
                    h = self.y_regions[row_idx + 1] - y
                    sample_h = int(h * 0.6)
                    sample_y = y + int(h * 0.2)

                    for col_idx in range(num_cols):
                        # Skip indexer columns
                        if plate_type == self.PLATE_FULL and col_idx in (0, 8):
                            continue
                        if plate_type == self.PLATE_MINI and col_idx == 0:
                            continue

                        x = self.x_regions[col_idx]
                        w = self.x_regions[col_idx + 1] - x
                        sample_w = int(w * 0.7)
                        sample_x = x + int(w * 0.15)

                        self._read_cell(
                            img, sample_x, sample_y, sample_w, sample_h, True
                        )

            # Display image
            lcd.display(img)

            # Check for click/touch to perform final reading
            if self.ctx.input.enter_event() or self.ctx.input.touch_event(
                validate_position=False
            ):
                if rect and plate_type:
                    sensor.run(0)
                    self.ctx.display.to_portrait()

                    # Remember plate type from first scan
                    if detected_plate_type is None:
                        detected_plate_type = plate_type
                        mini_mode = plate_type == self.PLATE_MINI and not w24

                    grid, _, _ = self._read_all_grid_cells(img, rect, plate_type)

                    # Calculate word offset for display
                    if w24 and page == 1:
                        word_offset = 12  # Second scan of 24-word mode: words 13-24
                    elif mini_mode and page == 1:
                        word_offset = 6  # Second scan of mini plate: words 7-12
                    else:
                        word_offset = 0  # First scan: words 1-6 or 1-12

                    edited_numbers = self._show_stackbit_words(
                        grid, word_offset, plate_type
                    )

                    if edited_numbers is not None:
                        words = self._numbers_to_words(edited_numbers)
                    else:
                        words = None

                    if words:
                        if w24:
                            # 24-word mode: always uses full plate, 2 scans
                            if page == 0:
                                all_words = words[:]
                                page = 1

                                self.ctx.display.clear()
                                self.flash_text(
                                    t("Flip plate")
                                    + "\n"
                                    + t("Words 13-24")
                                    + "\n\n"
                                    + t("Click to read")
                                )

                                self.ctx.camera.initialize_run(mode=BINARY_GRID_MODE)
                                self.ctx.camera.zoom_mode()
                                self.ctx.display.to_landscape()
                                self.ctx.display.clear()
                                continue
                            all_words.extend(words)
                            return all_words
                        if mini_mode:
                            # Mini plate 12-word mode: 2 scans of 6 words each
                            if page == 0:
                                all_words = words[:]
                                page = 1

                                self.ctx.display.clear()
                                self.flash_text(
                                    t("Flip plate")
                                    + "\n"
                                    + t("Words 7-12")
                                    + "\n\n"
                                    + t("Click to read")
                                )

                                self.ctx.camera.initialize_run(mode=BINARY_GRID_MODE)
                                self.ctx.camera.zoom_mode()
                                self.ctx.display.to_landscape()
                                self.ctx.display.clear()
                                continue
                            all_words.extend(words)
                            return all_words
                        # Full plate 12-word mode: single scan
                        return words

                    # Invalid words - return to scanning
                    self.ctx.display.to_landscape()
                    self.ctx.camera.initialize_run(mode=BINARY_GRID_MODE)
                    self.ctx.camera.zoom_mode()
                    continue

            # Check for exit
            if self.ctx.input.page_event() or self.ctx.input.page_prev_event():
                break

        sensor.run(0)
        self.ctx.display.to_portrait()
        return None
