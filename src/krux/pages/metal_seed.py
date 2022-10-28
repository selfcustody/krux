# The MIT License (MIT)

# Copyright (c) 2021-2022 Krux contributors

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

import hashlib
import lcd
from embit.wordlists.bip39 import WORDLIST
from . import Page
from ..krux_settings import t
from ..display import DEFAULT_PADDING
from ..input import (
    BUTTON_ENTER,
    BUTTON_PAGE,
    BUTTON_PAGE_PREV,
    BUTTON_TOUCH,
)

STACKBIT_GO_INDEX = 38
STACKBIT_ESC_INDEX = 35
STACKBIT_MAX_INDEX = 13


class TinySeed(Page):
    """Class for handling Tinyseed fomat"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.x_offset = DEFAULT_PADDING // 2 + 2 * self.ctx.display.font_width
        if self.ctx.display.width() > 135:
            self.y_offset = DEFAULT_PADDING + 3 * self.ctx.display.font_height
            self.x_pad = self.ctx.display.font_height
            self.y_pad = self.ctx.display.font_height
            self.y_pad += self.ctx.display.height() // 120
        else:
            self.y_offset = 2 * self.ctx.display.font_height
            self.x_pad = self.ctx.display.font_width + 1
            self.y_pad = self.ctx.display.font_height

    def _draw_grid(self):
        """Draws grid for import and export Tinyseed UI"""
        y_var = self.y_offset
        x_offset = self.x_offset
        for _ in range(13):
            self.ctx.display.fill_rectangle(
                x_offset,
                self.y_offset,
                1,
                12 * self.y_pad,
                lcd.DARKGREY,
            )
            x_offset += self.x_pad
            self.ctx.display.fill_rectangle(
                self.x_offset,
                y_var,
                12 * (self.x_pad),
                1,
                lcd.DARKGREY,
            )
            y_var += self.y_pad

    def _draw_labels(self, page):
        """Draws labels for import and export Tinyseed UI"""
        self.ctx.display.draw_hcentered_text("Tiny Seed")
        if self.ctx.display.width() > 135:
            self.ctx.display.to_landscape()
            bit_number = 2048
            bit_offset = DEFAULT_PADDING // 2 + 2 * self.ctx.display.font_height
            for _ in range(12):
                lcd.draw_string(
                    (7 - len(str(bit_number))) * self.ctx.display.font_width
                    - DEFAULT_PADDING // 2,
                    self.ctx.display.width() - bit_offset,
                    str(bit_number),
                    lcd.WHITE,
                )
                bit_number //= 2
                bit_offset += self.x_pad
            self.ctx.display.to_portrait()
        y_offset = self.y_offset
        y_offset += (self.y_pad - self.ctx.display.font_height) // 2
        for x in range(12):
            line = str(page * 12 + x + 1)
            if (page * 12 + x + 1) < 10:
                line = " " + line
            self.ctx.display.draw_string(
                DEFAULT_PADDING // 2, y_offset, line, lcd.WHITE
            )
            y_offset += self.y_pad

    def _draw_punched(self, words, page):
        """Draws punched bits for import and export Tinyseed UI"""
        y_offset = self.y_offset
        for x in range(12):
            if isinstance(words[0], str):
                word_list_index = WORDLIST.index(words[page * 12 + x]) + 1
            else:
                word_list_index = words[page * 12 + x]
            for y in range(12):
                if (word_list_index >> (11 - y)) & 1:
                    x_offset = self.x_offset + 3
                    x_offset += y * (self.x_pad)
                    self.ctx.display.fill_rectangle(
                        x_offset,
                        y_offset + 3,
                        self.x_pad - 5,
                        self.y_pad - 5,
                        lcd.GREEN,
                    )
            y_offset += self.y_pad

    def export(self):
        """Shows seed as a punch pattern for Tiny Seed layout"""
        words = self.ctx.wallet.key.mnemonic.split(" ")
        for page in range(len(words) // 12):
            self._draw_labels(page)
            self._draw_grid()
            self._draw_punched(words, page)
            self.ctx.input.wait_for_button()
            self.ctx.display.clear()

    def _draw_index(self, index):
        """Outline index respective"""
        width = 6 * self.x_pad - 2
        if index >= 162:
            x_position = self.x_offset + 6 * self.x_pad + 1
        elif index >= 156:
            x_position = self.x_offset + 1
        elif index < 139:
            x_position = index % 12
            x_position *= self.x_pad
            x_position += self.x_offset + 1
            width = self.x_pad - 2
        else:
            return
        y_position = index // 12
        y_position *= self.y_pad
        y_position += self.y_offset + 1
        self.ctx.display.outline(
            x_position,
            y_position,
            width,
            self.y_pad - 2,
            lcd.WHITE,
        )

    def _draw_menu(self):
        """Draws options to leave and proceed"""
        y_offset = self.y_offset + 13 * self.y_pad
        x_offset = self.x_offset
        self.ctx.display.draw_string(
            x_offset + (5 * self.x_pad) // 2, y_offset + 1, t("Esc"), lcd.WHITE
        )
        self.ctx.display.draw_string(
            x_offset + (17 * self.x_pad) // 2, y_offset + 1, t("Go"), lcd.WHITE
        )
        self.ctx.display.fill_rectangle(
            x_offset,
            y_offset,
            12 * self.x_pad,
            1,
            lcd.DARKGREY,
        )
        self.ctx.display.fill_rectangle(
            x_offset,
            y_offset + self.y_pad,
            12 * self.x_pad,
            1,
            lcd.DARKGREY,
        )
        for _ in range(3):
            self.ctx.display.fill_rectangle(
                x_offset,
                y_offset,
                1,
                self.y_pad,
                lcd.DARKGREY,
            )
            x_offset += 6 * self.x_pad

    def _map_keys_array(self):
        """Maps an array of regions for keys to be placed in"""
        if self.ctx.input.touch is not None:
            x_region = self.x_offset
            for _ in range(13):
                self.ctx.input.touch.x_regions.append(x_region)
                x_region += self.x_pad
            y_region = self.y_offset
            for _ in range(15):
                self.ctx.input.touch.y_regions.append(y_region)
                y_region += self.y_pad

    def _draw_disabled(self):
        """Draws disabled section where checksum is automatically filled"""
        self.ctx.display.fill_rectangle(
            self.x_offset + 7 * self.x_pad,
            self.y_offset + 11 * self.y_pad,
            5 * self.x_pad,
            self.y_pad,
            lcd.DARKGREY,
        )

    def _check_sum(self, tiny_seed_numbers):
        """Dinamically calculates checksum"""
        # Inspired in Jimmy Song's HDPrivateKey.from_mnemonic() method
        binary_seed = bytearray()
        offset = 0
        for tiny_seed_number in tiny_seed_numbers:
            index = tiny_seed_number - 1 if tiny_seed_number > 1 else 0
            remaining = 11
            while remaining > 0:
                bits_needed = 8 - offset
                if remaining == bits_needed:
                    if bits_needed == 8:
                        binary_seed.append(index)
                    else:
                        binary_seed[-1] |= index
                    offset = 0
                    remaining = 0
                elif remaining > bits_needed:
                    if bits_needed == 8:
                        binary_seed.append(index >> (remaining - 8))
                    else:
                        binary_seed[-1] |= index >> (remaining - bits_needed)
                    remaining -= bits_needed
                    offset = 0
                    # lop off the top 8 bits
                    index &= (1 << remaining) - 1
                else:
                    binary_seed.append(index << (8 - remaining))
                    offset = remaining
                    remaining = 0

        checksum_length_bits = len(tiny_seed_numbers) * 11 // 33
        num_remainder = checksum_length_bits % 8
        if num_remainder:
            checksum_length = checksum_length_bits // 8 + 1
        else:
            checksum_length = checksum_length_bits // 8
        raw = bytes(binary_seed)
        data = raw[:-checksum_length]
        computed_checksum = int.from_bytes(
            hashlib.sha256(data).digest()[:checksum_length], "big"
        )
        checksum = computed_checksum >> (8 - checksum_length_bits)
        return checksum

    def enter_tiny_seed(self):
        """UI to manually enter a Tiny Seed"""

        def _toggle_bit(word, bit):
            """Toggle bit state according to pressed index"""
            return word ^ (1 << bit)

        def _to_words(tiny_seed_numbers):
            words = []
            for number in tiny_seed_numbers:
                words.append(WORDLIST[number - 1])
            return words

        index = 0
        tiny_seed_numbers = [2048] * 11 + [8]
        btn = None
        self._map_keys_array()
        while True:
            self._draw_labels(0)
            self._draw_grid()
            self._draw_disabled()
            self._draw_punched(tiny_seed_numbers, 0)
            self._draw_menu()
            self._draw_index(index)
            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_TOUCH:
                btn = BUTTON_ENTER
                index = self.ctx.input.touch.current_index()
            if btn == BUTTON_ENTER:
                if index >= 162:  # go
                    # self.ctx.input.touch.clear_regions()
                    return _to_words(tiny_seed_numbers)
                if index >= 156:  # ESC
                    self.ctx.display.clear()
                    if self.prompt(t("Are you sure?"), self.ctx.display.height() // 2):
                        break
                    self._map_keys_array()
                elif index < 139:
                    word_index = index // 12
                    bit = 11 - (index % 12)
                    if bit == 11:
                        tiny_seed_numbers[word_index] = 2048
                    else:
                        tiny_seed_numbers[word_index] = (
                            _toggle_bit(tiny_seed_numbers[word_index], bit) % 2048
                        )
                    if tiny_seed_numbers[word_index] == 0:
                        tiny_seed_numbers[word_index] = 2048
                    checksum = self._check_sum(tiny_seed_numbers)
                    tiny_seed_numbers[11] -= 1
                    tiny_seed_numbers[11] &= 0b11111110000
                    tiny_seed_numbers[11] += checksum + 1
            elif btn == BUTTON_PAGE:
                if index >= 167:
                    index = 0
                elif index >= 161:
                    index = 167
                elif index >= 138:
                    index = 161
                else:
                    index += 1
            elif btn == BUTTON_PAGE_PREV:
                if index <= 0:
                    index = 167
                elif index <= 138:
                    index -= 1
                elif index <= 161:
                    index = 138
                elif index <= 167:
                    index = 161
            self.ctx.display.clear()


class Stackbit(Page):
    """Class for handling Stackbit 1248 fomat"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.x_offset = DEFAULT_PADDING
        self.x_pad = 2 * self.ctx.display.font_width
        self.y_offset = 2 * self.ctx.display.font_height
        self.y_pad = self.ctx.display.font_height

    def _draw_labels(self, y_offset, word_index):
        """Draws labels for import and export Stackbit 1248 UI"""
        index_x_offset = self.x_offset + self.x_pad // 2 - 1
        y_offset += (self.y_pad - self.ctx.display.font_height) // 2
        if len(str(word_index)) > 1:
            index_x_offset -= self.ctx.display.font_width
        self.ctx.display.draw_string(
            index_x_offset,
            y_offset + self.y_pad // 2,
            str(word_index),
            lcd.WHITE,
            lcd.BLACK,
        )
        numbers_offset = self.x_offset + self.x_pad
        numbers_offset += (self.x_pad - self.ctx.display.font_width) // 2
        upper_numbers = [1, 1, 2, 1, 2, 1, 2]
        lower_numbers = [2, 4, 8, 4, 8, 4, 8]
        for x in range(len(upper_numbers)):
            self.ctx.display.draw_string(
                numbers_offset,
                y_offset,
                str(upper_numbers[x]),
                lcd.WHITE,
            )
            self.ctx.display.draw_string(
                numbers_offset,
                y_offset + self.y_pad,
                str(lower_numbers[x]),
                lcd.WHITE,
            )
            numbers_offset += self.x_pad

    def _draw_grid(self, y_offset):
        """Draws grid for import and export Stackbit 1248 UI"""
        y_offset -= 2
        x_bar_offset = self.x_offset
        # Horizontal lines
        width = 8 * self.x_pad + self.ctx.display.font_width // 2
        height = 2 * self.y_pad + 6
        self.ctx.display.fill_rectangle(
            x_bar_offset - self.ctx.display.font_width // 2,
            y_offset,
            width,
            1,
            lcd.DARKGREY,
        )
        self.ctx.display.fill_rectangle(
            x_bar_offset - self.ctx.display.font_width // 2,
            y_offset + height,
            width,
            1,
            lcd.DARKGREY,
        )
        # Vertical lines
        self.ctx.display.fill_rectangle(
            x_bar_offset - self.ctx.display.font_width // 2,
            y_offset,
            1,
            height,
            lcd.DARKGREY,
        )
        x_bar_offset += self.x_pad
        self.ctx.display.fill_rectangle(
            x_bar_offset,
            y_offset,
            1,
            height,
            lcd.DARKGREY,
        )
        x_bar_offset += self.x_pad
        for _ in range(4):
            self.ctx.display.fill_rectangle(
                x_bar_offset,
                y_offset,
                1,
                height,
                lcd.DARKGREY,
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
        """Draws punched bits for import and export Tinyseed UI"""
        outline_width = self.x_pad - 6
        outline_height = self.y_pad - 4
        outline_x_offset = self.x_offset + self.x_pad + 3
        if digits[0] == 2:
            self.ctx.display.outline(
                outline_x_offset,
                y_offset + self.y_pad + 1,
                outline_width,
                outline_height,
                lcd.GREEN,
            )
        elif digits[0] == 1:
            self.ctx.display.outline(
                outline_x_offset,
                y_offset + 1,
                outline_width,
                outline_height,
                lcd.GREEN,
            )
        outline_x_offset += self.x_pad
        for x in range(3):
            if (digits[x + 1] >> 3) & 1:
                self.ctx.display.outline(
                    outline_x_offset + self.x_pad,
                    y_offset + self.y_pad + 1,
                    outline_width,
                    outline_height,
                    lcd.GREEN,
                )
            if (digits[x + 1] >> 2) & 1:
                self.ctx.display.outline(
                    outline_x_offset,
                    y_offset + self.y_pad + 1,
                    outline_width,
                    outline_height,
                    lcd.GREEN,
                )
            if (digits[x + 1] >> 1) & 1:
                self.ctx.display.outline(
                    outline_x_offset + self.x_pad,
                    y_offset + 1,
                    outline_width,
                    outline_height,
                    lcd.GREEN,
                )
            if digits[x + 1] & 1:
                self.ctx.display.outline(
                    outline_x_offset,
                    y_offset + 1,
                    outline_width,
                    outline_height,
                    lcd.GREEN,
                )
            outline_x_offset += 2 * self.x_pad

    def export_1248(self, word_index, y_offset, word):
        """Draws punch pattern for Stackbit 1248 seed layout"""

        self.x_offset = DEFAULT_PADDING
        self.x_pad = 2 * self.ctx.display.font_width
        self.y_offset = 2 * self.ctx.display.font_height
        self.y_pad = self.ctx.display.font_height

        self.ctx.display.draw_hcentered_text("Stackbit 1248")
        self._draw_labels(y_offset, word_index)
        self._draw_grid(y_offset)
        digits, digits_str = self._word_to_digits(word)
        self._draw_punched(digits, y_offset)
        if self.ctx.display.height() > 240:
            self.ctx.display.draw_string(
                self.x_offset + 17 * self.ctx.display.font_width,
                y_offset,
                digits_str,
                lcd.LIGHTGREY,
            )
            self.ctx.display.draw_string(
                self.x_offset + 17 * self.ctx.display.font_width,
                y_offset + self.y_pad,
                word,
                lcd.LIGHTGREY,
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
        if index >= STACKBIT_GO_INDEX:
            x_position = x_offset + 3 * self.x_pad
            y_position += 1
        elif index >= STACKBIT_ESC_INDEX:
            x_position = x_offset
            y_position += 1
        elif index < 14:
            x_position = index % 7
            x_position *= self.x_pad
            x_position += x_offset
            width = self.x_pad - 2
        else:
            return
        self.ctx.display.outline(
            x_position,
            y_position,
            width,
            self.y_pad,
            lcd.WHITE,
        )

    def _draw_menu(self):
        """Draws options to leave and proceed"""
        y_offset = self.y_offset + 5 * self.y_pad
        label_y_offset = (self.y_pad - self.ctx.display.font_height) // 2
        x_offset = self.x_offset + self.x_pad
        self.ctx.display.draw_string(
            x_offset + self.x_pad, y_offset + label_y_offset, "ESC", lcd.WHITE
        )
        self.ctx.display.draw_string(
            x_offset + 4 * self.x_pad, y_offset + label_y_offset, "GO", lcd.WHITE
        )
        self.ctx.display.fill_rectangle(
            x_offset,
            y_offset,
            6 * self.x_pad,
            1,
            lcd.DARKGREY,
        )
        self.ctx.display.fill_rectangle(
            x_offset,
            y_offset + self.y_pad,
            6 * self.x_pad,
            1,
            lcd.DARKGREY,
        )
        for _ in range(3):
            self.ctx.display.fill_rectangle(
                x_offset,
                y_offset,
                1,
                self.y_pad,
                lcd.DARKGREY,
            )
            x_offset += 3 * self.x_pad

    def digits_to_word(self, digits):
        """Returns seed word respective to digits BIP39 dictionaty position"""
        word_number = ""
        for digit in digits:
            word_number += str(digit)
        word_number = int(word_number)
        if 0 < word_number <= 2048:
            return WORDLIST[word_number - 1]
        return None

    def preview_word(self, digits):
        """Draws word respective to current state"""
        preview_string = ""
        for digit in digits:
            preview_string += str(digit)
        word = self.digits_to_word(digits)
        if word is not None:
            preview_string += ": " + word
        y_offset = self.y_offset + 3 * self.y_pad
        self.ctx.display.draw_hcentered_text(preview_string, y_offset)

    def _map_keys_array(self):
        """Maps an array of regions for keys to be placed in"""
        if self.ctx.input.touch is not None:
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
        if btn == BUTTON_PAGE:
            if index >= STACKBIT_GO_INDEX:
                return 0
            if index >= STACKBIT_ESC_INDEX:
                return STACKBIT_GO_INDEX
            if index >= STACKBIT_MAX_INDEX:
                return STACKBIT_ESC_INDEX
            return page_move[index]
        if btn == BUTTON_PAGE_PREV:
            if index <= 0:
                return STACKBIT_GO_INDEX
            if index <= STACKBIT_MAX_INDEX:
                return page_prev_move[index]
            if index <= STACKBIT_ESC_INDEX:
                return STACKBIT_MAX_INDEX
        return STACKBIT_ESC_INDEX

    def enter_1248(self):
        """UI to manually enter a Stackbit 1248"""
        if self.ctx.display.width() > 135:
            self.x_pad = 3 * self.ctx.display.font_width
        else:
            self.x_pad = 2 * self.ctx.display.font_width
        self.x_offset = self.ctx.display.width()
        self.x_offset -= 8 * self.x_pad
        self.x_offset = max(self.x_offset, DEFAULT_PADDING)
        self.x_offset //= 2
        self.y_offset = 3 * self.ctx.display.font_height
        self.y_pad = 2 * self.ctx.display.font_height
        index = 0
        digits = [0, 0, 0, 0]
        word_index = 1
        self._map_keys_array()
        words = []
        while word_index <= 24:
            self.ctx.display.draw_hcentered_text("Stackbit 1248")
            y_offset = self.y_offset
            self._draw_labels(y_offset, word_index)
            self._draw_grid(y_offset)
            self._draw_menu()
            self._draw_index(index)
            self.preview_word(digits)
            self._draw_punched(digits, y_offset)
            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_TOUCH:
                btn = BUTTON_ENTER
                index = self.ctx.input.touch.current_index()
            if btn == BUTTON_ENTER:
                if index >= STACKBIT_GO_INDEX:  # go
                    word = self.digits_to_word(digits)
                    if word is not None:
                        digits = [0, 0, 0, 0]
                        index = 0
                        words.append(word)
                        if word_index == 12:
                            self.ctx.display.clear()
                            if self.prompt(t("Done?"), self.ctx.display.height() // 2):
                                break
                            self._map_keys_array()
                        word_index += 1
                elif index >= STACKBIT_ESC_INDEX:  # ESC
                    self.ctx.display.clear()
                    if self.prompt(t("Are you sure?"), self.ctx.display.height() // 2):
                        break
                    self._map_keys_array()
                elif index < 14:
                    digits = self._toggle_bit(digits, index)
            else:
                index = self.index(index, btn)
            self.ctx.display.clear()
        if len(words) in (12, 24):
            return words
        return None
