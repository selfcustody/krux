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
"""
2XD8 Entropy Booklet method (github.com/bowtiedcrake/2xd8-entropy-booklet).

Unlike Krux's D6/D20 dice entropy (which hashes a whole roll sequence with
SHA-256), this method draws *whole BIP39 words* directly: two distinguishable
D8 dice are rolled twice per word.

  Roll 1 (card select): White read openly 1-8 (3 bits). Black read only as a
  pair -- 1/2, 3/4, 5/6, 7/8 (2 bits). Together they select 1 of 32 "cards".
  Roll 2 (word select): White = row 1-8, Black = column 1-8 on that card's
  8x8 grid (6 bits).

5 + 6 = 11 bits = 1-of-2048, exactly the width of one BIP39 word index, with
no modulo bias -- the same mapping used by the printed booklet (card n, cell
k holds BIP39 index n + 32*k).

Each roll pair is entered on a two-wheel picker (White, Black) and the result
-- the card number, then the word -- is revealed the instant it's computed,
so a user can check it against a physical printed booklet as they go, word
by word, instead of only seeing results after the whole mnemonic is drawn.

The final checksum word is never drawn by hand: the (11 or 23) drawn words
supply the leading entropy bits, the remaining bits are zero-padded, and
embit's mnemonic_from_bytes() (standard BIP39, called by the Login handler)
computes the real checksum word from that entropy -- mirroring the booklet's
own rule that a hardware wallet/offline tool must compute the last word.
"""
import lcd
from embit.bip39 import WORDLIST
from .. import (
    Page,
    ESC_KEY,
    BUTTON_ENTER,
    BUTTON_PAGE,
    BUTTON_PAGE_PREV,
    BUTTON_TOUCH,
    SWIPE_UP,
    SWIPE_DOWN,
    SWIPE_LEFT,
    FAST_FORWARD,
    FAST_BACKWARD,
)
from ...display import DEFAULT_PADDING, FONT_HEIGHT, FONT_WIDTH, BOTTOM_PROMPT_LINE
from ...themes import theme
from ...krux_settings import t
from ...kboard import kboard

INCREMENT = (BUTTON_PAGE, SWIPE_DOWN, FAST_FORWARD)
DECREMENT = (BUTTON_PAGE_PREV, SWIPE_UP, FAST_BACKWARD)
LOCK_IN = (BUTTON_ENTER, BUTTON_TOUCH)


def card_number(white1, black1):
    """White's 8 values x Black collapsed into 4 equal pairs -> 1-of-32 card"""
    black_pair_idx = (black1 + 1) // 2  # 1,2->1  3,4->2  5,6->3  7,8->4
    return (white1 - 1) * 4 + black_pair_idx


def word_index(card_n, white2, black2):
    """Full 1-based BIP39 index (1..2048), same mapping as the printed
    booklet: card n, cell k (row-major, White=row, Black=col) holds
    index n + 32*k."""
    k = (white2 - 1) * 8 + (black2 - 1)  # 0..63
    return card_n + 32 * k


class EntropyApp2XD8(Page):
    """Draw whole BIP39 words with a pair of D8 dice, 2XD8 Booklet method.

    Each word is drawn in two revealed steps -- card, then word -- via a
    two-wheel (White, Black) picker, so the result can be checked against a
    physical booklet as it's produced.
    """

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.words_needed = 0
        self.words = []

    def _draw_wheel_screen(self, top_label, sub_label, values, active, locked):
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(top_label, color=theme.highlight_color)
        self.ctx.display.draw_hcentered_text(sub_label, 2 * FONT_HEIGHT)

        width = self.ctx.display.width()
        height = self.ctx.display.height()
        col_w = width // 2
        box_size = min(col_w - 3 * FONT_WIDTH, height // 4)
        box_y = height * 3 // 5 - box_size // 2

        labels = (t("WHITE"), t("BLACK"))
        for i in range(2):
            cx = col_w * i + col_w // 2
            label_color = theme.highlight_color if i == active else theme.fg_color
            self.ctx.display.draw_string(
                cx - len(labels[i]) * FONT_WIDTH // 2,
                box_y - 2 * FONT_HEIGHT,
                labels[i],
                label_color,
            )
            box_x = cx - box_size // 2
            if i == active:
                self.ctx.display.outline(
                    box_x, box_y, box_size, box_size, theme.highlight_color
                )
            text = str(values[i])
            value_color = theme.highlight_color if locked[i] else theme.fg_color
            self.ctx.display.draw_string(
                cx - len(text) * FONT_WIDTH // 2,
                box_y + box_size // 2 - FONT_HEIGHT // 2,
                text,
                value_color,
            )

        # Skipped on tiny displays (m5stickv/cube) -- there isn't room for
        # this without recreating the exact cramped-screen problem this
        # feature is meant to avoid; the header's "Word X of N" is the only
        # progress context those devices get.
        if not kboard.has_minimal_display:
            self._draw_recent_words(height)
            self._draw_progress_bar(height)

    def _draw_recent_words(self, height):
        if not self.words:
            return
        # Drop the oldest of the 3 first if it still doesn't fit -- better to
        # show fewer words cleanly than wrap into the progress bar below.
        recent = self.words[-3:]
        start_num = len(self.words) - len(recent) + 1
        while recent:
            text = " ".join(
                "%d.%s" % (start_num + i, w) for i, w in enumerate(recent)
            )
            if lcd.string_width_px(text) <= self.ctx.display.usable_width():
                break
            recent = recent[1:]
            start_num += 1
        if not text:
            return
        self.ctx.display.draw_hcentered_text(
            text, height - 3 * FONT_HEIGHT, theme.fg_color, max_lines=1
        )

    def _draw_progress_bar(self, height):
        offset_y = height - int(1.5 * FONT_HEIGHT)
        pb_height = FONT_HEIGHT - 4
        words_done = len(self.words)
        if words_done and self.words_needed:
            progress = words_done * (self.ctx.display.usable_width() - 3)
            progress //= self.words_needed
            self.ctx.display.fill_rectangle(
                DEFAULT_PADDING + 2,
                offset_y + 2,
                progress,
                pb_height - 4,
                theme.fg_color,
            )
        outline_color = (
            theme.go_color if words_done >= self.words_needed else theme.no_esc_color
        )
        self.ctx.display.outline(
            DEFAULT_PADDING,
            offset_y,
            self.ctx.display.usable_width(),
            pb_height,
            outline_color,
        )

    def _pick_die_pair(self, top_label, sub_label):
        """Two-wheel picker (White, Black), 1-8 each. Page/swipe up-down
        scrolls the active wheel; Enter/tap locks it and auto-advances to
        the next wheel; a long-press/swipe-left cancels. Returns
        (white, black) ints, or None if cancelled."""
        values = [1, 1]
        locked = [False, False]
        active = 0
        while True:
            self._draw_wheel_screen(top_label, sub_label, values, active, locked)
            btn = self.ctx.input.wait_for_button()
            if btn in INCREMENT:
                values[active] = values[active] % 8 + 1
            elif btn in DECREMENT:
                values[active] = (values[active] - 2) % 8 + 1
            elif btn in LOCK_IN:
                locked[active] = True
                if active == 0:
                    active = 1
                else:
                    return values[0], values[1]
            elif btn == SWIPE_LEFT:
                if self.esc_prompt() == ESC_KEY:
                    return None

    def new_key(self):
        """Draw words via the 2XD8 method; returns raw entropy bytes (drawn
        words zero-padded to the full width) ready for
        embit.bip39.mnemonic_from_bytes, or None if cancelled."""
        len_mnemonic = self.choose_len_mnemonic()
        if not len_mnemonic:
            return None
        self.words_needed = 11 if len_mnemonic == 12 else 23

        self.ctx.display.draw_hcentered_text(
            t("Roll two D8 dice (White, Black), twice per word.")
            + "\n"
            + t("Card, then word, is revealed as you go --")
            + "\n"
            + t("check them against your booklet.")
        )
        if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
            return None

        while len(self.words) < self.words_needed:
            word_num = len(self.words) + 1
            top_label = t("Word %d of %d") % (word_num, self.words_needed)

            rolled = self._pick_die_pair(top_label, t("Get Card"))
            if rolled is None:
                return None
            card_n = card_number(*rolled)

            rolled = self._pick_die_pair(top_label, t("Card %02d - Get Word") % card_n)
            if rolled is None:
                return None
            word = WORDLIST[word_index(card_n, *rolled) - 1]

            self.words.append(word)
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("WORD %d: %s") % (word_num, word.upper())
            )
            self.ctx.display.draw_hcentered_text(
                t("Press to continue"), BOTTOM_PROMPT_LINE, theme.frame_color
            )
            while True:
                btn = self.ctx.input.wait_for_button()
                if btn in LOCK_IN:
                    break
                if btn == SWIPE_LEFT:
                    if self.esc_prompt() == ESC_KEY:
                        return None

        # Reuses the same numbered-list renderer the final mnemonic screen
        # uses (paginates by button-press on tiny displays, two columns on
        # bigger ones) instead of cramming everything into one info box.
        # The prompt is deliberately a separate, cleared screen -- chaining
        # it directly under the word list at a fixed offset overlapped the
        # last word(s) on small displays, since display_mnemonic() doesn't
        # report how many lines it actually used.
        self.display_mnemonic(" ".join(self.words), title=t("Words Drawn"))
        self.ctx.input.wait_for_button()
        self.ctx.display.clear()
        if not self.prompt(
            t("Compute checksum word and generate mnemonic?"),
            self.ctx.display.height() // 2,
        ):
            return None

        bits = "".join("{:011b}".format(WORDLIST.index(word)) for word in self.words)
        total_bits = 256 if len_mnemonic == 24 else 128
        bits += "0" * (total_bits - len(bits))  # unresolved tail bits, per booklet spec
        return int(bits, 2).to_bytes(total_bits // 8, "big")
