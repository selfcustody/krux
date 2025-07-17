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

from embit import bip39
from embit.wordlists.bip39 import WORDLIST
from . import Page, ESC_KEY, LETTERS
from ..display import DEFAULT_PADDING, MINIMAL_PADDING, FONT_HEIGHT
from ..krux_settings import t
from ..themes import theme
from ..input import BUTTON_TOUCH, BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV
from ..key import Key
from ..kboard import kboard

GO_INDEX = 25
ESC_INDEX = 24


class MnemonicEditor(Page):
    """Mnemonic Editor UI"""

    def __init__(self, ctx, mnemonic=None, new=False):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.new_mnemonic = new
        self.valid_checksum = False
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
        start, stop = self.search_ranges[letter]
        return {
            word[len(prefix)]
            for word in wordlist[start:stop]
            if word.startswith(prefix) and len(word) > len(prefix)
        }

    def calculate_checksum(self):
        """Recalculate the checksum of the mnemonic"""
        if self.new_mnemonic:
            entropy = bip39.mnemonic_to_bytes(
                " ".join(self.current_mnemonic), ignore_checksum=True
            )
            self.current_mnemonic = bip39.mnemonic_from_bytes(entropy).split(" ")
            self.valid_checksum = True
        else:
            self.valid_checksum = bip39.mnemonic_is_valid(
                " ".join(self.current_mnemonic)
            )

    def _draw_header(self):
        """Draw current mnemonic words"""
        from ..wallet import is_double_mnemonic

        header = "BIP39" + " " + t("Mnemonic")
        mnemonic = " ".join(self.current_mnemonic)
        fingerprint = ""
        if is_double_mnemonic(mnemonic):
            header += "*"
        if self.valid_checksum:
            fingerprint = Key.extract_fingerprint(mnemonic)
            if fingerprint:
                fingerprint = "\n" + fingerprint
                header += fingerprint
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(header, MINIMAL_PADDING)
        if fingerprint:
            self.ctx.display.draw_hcentered_text(
                fingerprint, MINIMAL_PADDING, theme.highlight_color
            )
        self.header_offset = MINIMAL_PADDING * 2 + (
            len(self.ctx.display.to_lines(header)) * FONT_HEIGHT
        )
        if kboard.has_minimal_display:
            self.header_offset -= MINIMAL_PADDING

    def _map_words(self, button_index=0, page=0):
        """Map words to the screen"""

        def word_color(index):
            if (
                index == self.mnemonic_length - 1
                and not self.new_mnemonic
                and not self.valid_checksum
            ):
                return theme.error_color
            if self.current_mnemonic[index] != self.initial_mnemonic[index]:
                return theme.highlight_color
            return theme.fg_color

        # Words occupy 75% of the screen
        word_v_padding = self.ctx.display.height() * 3 // 4
        word_v_padding //= 12

        if self.ctx.input.touch is not None:
            self.ctx.input.touch.clear_regions()
            self.ctx.input.touch.x_regions.append(0)
            self.ctx.input.touch.x_regions.append(self.ctx.display.width() // 2)
            self.ctx.input.touch.x_regions.append(self.ctx.display.width())
            if not self.ctx.input.buttons_active and self.mnemonic_length == 24:
                self.ctx.display.draw_vline(
                    self.ctx.display.width() // 2,
                    self.header_offset,
                    12 * word_v_padding,
                    theme.frame_color,
                )
            y_region = self.header_offset
            for _ in range(13):
                if not self.ctx.input.buttons_active:
                    self.ctx.display.draw_hline(
                        MINIMAL_PADDING,
                        y_region,
                        self.ctx.display.width() - 2 * MINIMAL_PADDING,
                        theme.frame_color,
                    )
                self.ctx.input.touch.y_regions.append(y_region)
                y_region += word_v_padding
            self.ctx.input.touch.y_regions.append(self.ctx.display.height())
        y_region = self.header_offset
        y_region += (word_v_padding - FONT_HEIGHT) // 2
        word_index = 0
        if kboard.is_m5stickv or self.mnemonic_length == 12:
            x_padding = DEFAULT_PADDING
        else:
            x_padding = MINIMAL_PADDING
        while word_index < 12:
            paged_index = word_index + page * 12
            if word_index == button_index and self.ctx.input.buttons_active:
                self.ctx.display.draw_string(
                    x_padding,
                    y_region,
                    str(paged_index + 1) + "." + self.current_mnemonic[paged_index],
                    theme.bg_color,
                    word_color(paged_index),
                )
            else:
                self.ctx.display.draw_string(
                    x_padding,
                    y_region,
                    str(paged_index + 1) + "." + self.current_mnemonic[paged_index],
                    word_color(paged_index),
                )
            if self.mnemonic_length == 24 and not kboard.is_m5stickv:
                if word_index + 12 == button_index and self.ctx.input.buttons_active:
                    self.ctx.display.draw_string(
                        MINIMAL_PADDING + self.ctx.display.width() // 2,
                        y_region,
                        str(word_index + 13)
                        + "."
                        + self.current_mnemonic[word_index + 12],
                        theme.bg_color,
                        word_color(word_index + 12),
                    )
                else:
                    self.ctx.display.draw_string(
                        MINIMAL_PADDING + self.ctx.display.width() // 2,
                        y_region,
                        str(word_index + 13)
                        + "."
                        + self.current_mnemonic[word_index + 12],
                        word_color(word_index + 12),
                    )
            word_index += 1
            y_region += word_v_padding

        if self.mnemonic_length == 24 and kboard.is_m5stickv and page == 0:
            go_txt = "13-24"
        else:
            go_txt = t("Go")
        esc_txt = t("Esc")
        menu_index = None
        if self.ctx.input.buttons_active and button_index >= ESC_INDEX:
            menu_index = button_index - ESC_INDEX
        self.draw_proceed_menu(
            go_txt, esc_txt, y_region, menu_index, self.valid_checksum
        )

    def edit_word(self, index):
        """Edit a word"""
        word_txt = str(index + 1) + ". " + self.current_mnemonic[index]
        self.flash_text(word_txt)
        while True:
            self.compute_search_ranges()
            # if new and last word, lead input to a valid mnemonic
            if self.new_mnemonic and index == self.mnemonic_length - 1:
                final_words = Key.get_final_word_candidates(self.current_mnemonic[:-1])
                word = self.capture_from_keypad(
                    t("Word %d") % (index + 1),
                    [LETTERS],
                    lambda x: self.autocomplete(x, final_words),
                    lambda x: self.possible_letters(x, final_words),
                )
            else:
                word = self.capture_from_keypad(
                    t("Word %d") % (index + 1),
                    [LETTERS],
                    self.autocomplete,
                    self.possible_letters,
                )
            if word == ESC_KEY:
                return None
            if word in WORDLIST:
                return word
            word = ""

    def edit(self):
        """Edit the mnemonic"""
        button_index = GO_INDEX  # start at "Go"
        self.calculate_checksum()
        page = 0
        while True:
            self.ctx.display.clear()
            self._draw_header()
            self._map_words(button_index, page)
            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_TOUCH:
                button_index = self.ctx.input.touch.current_index()
                if button_index < ESC_INDEX:
                    if self.mnemonic_length == 24 and button_index % 2 == 1:
                        button_index //= 2
                        button_index += 12
                    else:
                        button_index //= 2
                btn = BUTTON_ENTER
            if btn == BUTTON_ENTER:
                if button_index == GO_INDEX:
                    if self.mnemonic_length == 24 and kboard.is_m5stickv and page == 0:
                        page = 1
                        continue
                    # Done
                    if self.valid_checksum:
                        break
                    continue
                if button_index == ESC_INDEX:
                    # Cancel
                    self.ctx.display.clear()
                    if self.prompt(t("Are you sure?"), self.ctx.display.height() // 2):
                        return None
                    continue
                new_word = self.edit_word(button_index + page * 12)
                if new_word is not None:
                    self.ctx.display.clear()
                    if self.prompt(
                        str(button_index + 1) + ".\n\n" + new_word + "\n\n",
                        self.ctx.display.height() // 2,
                    ):
                        self.current_mnemonic[button_index + page * 12] = new_word
                        self.calculate_checksum()
            elif btn == BUTTON_PAGE:
                button_index += 1
                if (
                    kboard.is_m5stickv
                    and self.mnemonic_length == 24
                    and button_index == 12
                ) or (self.mnemonic_length == 12 and button_index == 12):
                    button_index += 12
                button_index %= 26
            elif btn == BUTTON_PAGE_PREV:
                button_index -= 1
                if (
                    kboard.is_m5stickv
                    and self.mnemonic_length == 24
                    and button_index == 23
                ) or (self.mnemonic_length == 12 and button_index == 23):
                    button_index -= 12
                button_index %= 26

        return " ".join(self.current_mnemonic)
