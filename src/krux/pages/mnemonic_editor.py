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

import lcd
from embit import bip39
from embit.wordlists.bip39 import WORDLIST
from . import Page, ESC_KEY, LETTERS
from ..display import DEFAULT_PADDING, MINIMAL_PADDING, FONT_HEIGHT
from ..krux_settings import t
from ..themes import theme
from ..input import BUTTON_TOUCH, BUTTON_ENTER


class MnemonicEditor(Page):
    """Mnemonic Editor UI"""

    def __init__(self, ctx, mnemonic=None):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.initial_mnemonic = []
        self.current_mnemonic = []
        if mnemonic:
            self.initial_mnemonic = mnemonic.split(" ")
            self.current_mnemonic = self.initial_mnemonic.copy()
        self.mnemonic_length = len(self.current_mnemonic)
        self.header_offset = DEFAULT_PADDING
        self.search_ranges = {}

    def compute_search_ranges(self, alt_wordlist=None):
        """Compute search ranges for the autocomplete and possible_letters functions"""
        if alt_wordlist:
            wordlist = alt_wordlist
        else:
            wordlist = WORDLIST
        search_ranges = {}
        i = 0
        while i < len(wordlist):
            start_word = wordlist[i]
            start_letter = start_word[0]
            j = i + 1
            while j < len(wordlist):
                end_word = wordlist[j]
                end_letter = end_word[0]
                if end_letter != start_letter:
                    search_ranges[start_letter] = (i, j)
                    i = j - 1
                    break
                j += 1
            if start_letter not in search_ranges:
                search_ranges[start_letter] = (i, j)
            i += 1
        self.search_ranges = search_ranges

    def autocomplete(self, prefix, alt_wordlist=None):
        """Autocomplete a word"""
        if alt_wordlist:
            wordlist = alt_wordlist
            self.compute_search_ranges(wordlist)
        else:
            wordlist = WORDLIST
        if len(prefix) > 0:
            letter = prefix[0]
            if letter not in self.search_ranges:
                return None
            start, stop = self.search_ranges[letter]
            matching_words = list(
                filter(
                    lambda word: word.startswith(prefix),
                    wordlist[start:stop],
                )
            )
            if len(matching_words) == 1:
                return matching_words[0]
        return None

    def possible_letters(self, prefix, alt_wordlist=None):
        """Possible next letters for a BIP39 word given a prefix"""
        if alt_wordlist:
            wordlist = alt_wordlist
            self.compute_search_ranges(wordlist)
        else:
            wordlist = WORDLIST
        if len(prefix) == 0:
            return self.search_ranges.keys()
        letter = prefix[0]
        if letter not in self.search_ranges:
            return ""
        start, stop = self.search_ranges[letter]
        return {
            word[len(prefix)]
            for word in wordlist[start:stop]
            if word.startswith(prefix) and len(word) > len(prefix)
        }

    def recalculate_checksum(self):
        """Recalculate the checksum of the mnemonic"""
        entropy = bip39.mnemonic_to_bytes(
            " ".join(self.current_mnemonic), ignore_checksum=True
        )
        self.current_mnemonic = bip39.mnemonic_from_bytes(entropy).split(" ")

    def _draw_header(self):
        """Draw current mnemonic words"""

        header = "BIP39" + " " + t("Mnemonic")
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(header, MINIMAL_PADDING)
        self.header_offset = MINIMAL_PADDING * 2 + (
            len(self.ctx.display.to_lines(header)) * FONT_HEIGHT
        )

    def _map_words(self):
        """Map words to the screen"""

        def word_color(index):
            if self.current_mnemonic[index] != self.initial_mnemonic[index]:
                return theme.highlight_color
            return theme.fg_color

        # Words occupy 75% of the screen
        word_v_padding = self.ctx.display.height() * 3 // 4
        word_v_padding //= 12

        if self.ctx.input.touch is not None:
            self.ctx.input.touch.clear_regions()
            self.ctx.input.touch.x_regions.append(MINIMAL_PADDING)
            self.ctx.input.touch.x_regions.append(self.ctx.display.width() // 2)
            self.ctx.input.touch.x_regions.append(
                self.ctx.display.width() - MINIMAL_PADDING
            )
            if self.mnemonic_length == 24:
                self.ctx.display.draw_vline(
                    self.ctx.display.width() // 2,
                    self.header_offset,
                    12 * word_v_padding,
                    theme.frame_color,
                )
            y_region = self.header_offset
            for _ in range(13):
                self.ctx.display.draw_hline(
                    MINIMAL_PADDING,
                    y_region,
                    self.ctx.display.width() - 2 * MINIMAL_PADDING,
                    theme.frame_color,
                )
                self.ctx.input.touch.y_regions.append(y_region)
                y_region += word_v_padding
            y_region = self.header_offset
            y_region += (word_v_padding - FONT_HEIGHT) // 2
            word_index = 0
            while word_index < self.mnemonic_length:
                self.ctx.display.draw_string(
                    MINIMAL_PADDING,
                    y_region,
                    str(word_index + 1) + "." + self.current_mnemonic[word_index],
                    word_color(word_index),
                )
                word_index += 1
                if self.mnemonic_length == 24:
                    self.ctx.display.draw_string(
                        MINIMAL_PADDING + self.ctx.display.width() // 2,
                        y_region,
                        str(word_index + 1) + "." + self.current_mnemonic[word_index],
                        word_color(word_index),
                    )
                    word_index += 1
                y_region += word_v_padding

            go_txt = t("Go")
            esc_txt = t("Esc")
            go_x_offset = self.ctx.display.width() // 2
            go_x_offset -= lcd.string_width_px(go_txt)
            go_x_offset //= 2
            esc_x_offset = self.ctx.display.width() // 2
            esc_x_offset -= lcd.string_width_px(esc_txt)
            esc_x_offset //= 2
            esc_x_offset += self.ctx.display.width() // 2
            go_esc_y_offset = self.ctx.display.height()
            go_esc_y_offset -= y_region + FONT_HEIGHT + MINIMAL_PADDING
            go_esc_y_offset //= 2
            go_esc_y_offset += y_region
            self.ctx.display.draw_string(
                go_x_offset, go_esc_y_offset, go_txt, theme.go_color
            )
            self.ctx.display.draw_string(
                esc_x_offset, go_esc_y_offset, esc_txt, theme.error_color
            )
            self.ctx.display.draw_vline(
                self.ctx.display.width() // 2,
                go_esc_y_offset,
                FONT_HEIGHT,
                theme.frame_color,
            )

            self.ctx.input.touch.y_regions.append(self.ctx.display.height())

    def edit_word(self, index):
        """Edit a word"""
        self.compute_search_ranges()
        word = self.capture_from_keypad(
            t("Word %d") % (index + 1),
            [LETTERS],
            self.autocomplete,
            self.possible_letters,
        )
        if word == ESC_KEY:
            return None
        return word

    def edit(self):
        """Edit the mnemonic"""
        button_index = 0
        while True:
            self.ctx.display.clear()
            self._draw_header()
            self._map_words()
            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_TOUCH:
                button_index = self.ctx.input.touch.current_index()
                if self.mnemonic_length == 12 and button_index < 24:
                    button_index //= 2
                btn = BUTTON_ENTER
            if btn == BUTTON_ENTER:
                if button_index == 24:
                    break
                if button_index == 25:
                    self.ctx.display.clear()
                    if self.prompt(t("Are you sure?"), self.ctx.display.height() // 2):
                        return None
                    continue
                new_word = self.edit_word(button_index)
                if new_word is not None:
                    self.ctx.display.clear()
                    if self.prompt(
                        str(button_index + 1) + ".\n\n" + new_word + "\n\n",
                        self.ctx.display.height() // 2,
                    ):
                        self.current_mnemonic[button_index] = new_word
                        self.recalculate_checksum()
        return " ".join(self.current_mnemonic)
