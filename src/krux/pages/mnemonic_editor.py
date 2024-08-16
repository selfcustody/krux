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
from . import Page, LETTERS
from ..display import DEFAULT_PADDING, MINIMAL_PADDING, FONT_HEIGHT
from ..krux_settings import t
from ..themes import theme
from ..input import BUTTON_TOUCH, BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV


class MnemonicEditor(Page):
    """Mnemonic Editor UI"""

    def __init__(self, ctx, mnemonic):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.initial_mnemonic = mnemonic
        self.current_mnemonic = mnemonic.split(" ")
        self.mnemonic_length = len(self.current_mnemonic)
        self.header_offset = DEFAULT_PADDING
        # Words occupy 75% of the screen
        self.word_v_padding = self.ctx.display.height() * 3 // 4
        self.word_v_padding //= 12

    def _draw_header(self):
        """Draw current mnemonic words"""

        header = "BIP39" + " " + t("Mnemonic")
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(header, MINIMAL_PADDING)
        self.header_offset = MINIMAL_PADDING * 2 + (
            len(self.ctx.display.to_lines(header)) * FONT_HEIGHT
        )

    def _map_words(self):
        word_list = [
            str(i + 1) + "." + ("  " if i + 1 < 10 else " ") + word
            for i, word in enumerate(self.current_mnemonic)
        ]
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
                    12 * self.word_v_padding,
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
                y_region += self.word_v_padding
            y_region = self.header_offset
            y_region += (self.word_v_padding - FONT_HEIGHT) // 2
            word_index = 0
            while word_index < self.mnemonic_length:
                self.ctx.display.draw_string(
                    MINIMAL_PADDING,
                    y_region,
                    str(word_index) + "." + self.current_mnemonic[word_index],
                )
                word_index += 1
                if self.mnemonic_length == 24:
                    self.ctx.display.draw_string(
                        MINIMAL_PADDING + self.ctx.display.width() // 2,
                        y_region,
                        str(word_index) + "." + self.current_mnemonic[word_index],
                    )
                    word_index += 1
                y_region += self.word_v_padding

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
        # from .login import autocomplete, possible_keys

        word = self.capture_from_keypad(
            t("Word %d") % (index + 1),
            [LETTERS],
            None,
            None,
        )
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
                if button_index >= 24:
                    break
                btn = BUTTON_ENTER
            if btn == BUTTON_ENTER:
                if button_index >= 24:
                    break
                # self.current_mnemonic[button_index] = self.edit_word(button_index)
                self.edit_word(button_index)

            print(button_index)
