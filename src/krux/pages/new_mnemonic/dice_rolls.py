# The MIT License (MIT)

# Copyright (c) 2021-2023 Krux contributors

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

from .. import (
    Page,
    Menu,
    MENU_EXIT,
    ESC_KEY,
)
from ...themes import theme
from ...krux_settings import t
from ...display import DEFAULT_PADDING

D6_STATES = [str(i + 1) for i in range(6)]
D20_STATES = [str(i + 1) for i in range(20)]

D6_12W_MIN_ROLLS = 50
D6_24W_MIN_ROLLS = 99
D20_12W_MIN_ROLLS = 30
D20_24W_MIN_ROLLS = 60
MIN_ENTROPY_12W = 128
MIN_ENTROPY_24W = 256


class DiceEntropy(Page):
    """Capture and analise entropy from dice rolls"""

    def __init__(self, ctx, d_20=False):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.d_20 = d_20
        self.roll_states = D20_STATES if d_20 else D6_STATES
        self.len_states = len(self.roll_states)
        self.min_rolls = 0
        self.min_entropy = 0
        self.rolls = []
        self.roll_counts = [0] * self.len_states

    def _count_rolls(self):
        self.roll_counts = [0] * self.len_states
        for roll in self.rolls:
            self.roll_counts[int(roll) - 1] += 1

    def shannons_entropy_rolls(self):
        """Calculates Shannon's entropy of a given list"""
        import math

        # Total number of pixels (equal to the number of bytes)
        total_rolls = len(self.rolls)
        if not total_rolls:
            return 0
        self._count_rolls()

        # Calculate entropy
        entropy = 0
        for count in self.roll_counts:
            probability = count / total_rolls
            entropy -= probability * (probability and math.log2(probability))

        return entropy * total_rolls

    def _stats_for_nerds(self):
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(
            t("Rolls distribution:"), self.ctx.display.font_height
        )
        self._count_rolls()
        max_count = self.roll_counts.index(max(self.roll_counts))
        scale_factor = (4 * self.ctx.display.font_height) / self.roll_counts[max_count]
        bar_graph = []
        for count in self.roll_counts:
            bar_graph.append(count * scale_factor)
        bar_pad = self.ctx.display.width() // (self.len_states + 2)
        offset_x = bar_pad
        for individual_bar in bar_graph:
            offset_y = (
                8 * self.ctx.display.font_height
            )  # 2 from tittle 4 from max bar height
            offset_y -= int(individual_bar)
            self.ctx.display.fill_rectangle(
                offset_x + 1,
                offset_y,
                bar_pad - 2,
                int(individual_bar),
                theme.highlight_color,
            )
            offset_x += bar_pad
        shannons_entropy = self.shannons_entropy_rolls()
        self.ctx.display.draw_hcentered_text(
            t("Shannon's Entropy: ") + str(int(shannons_entropy)) + "bits",
            10 * self.ctx.display.font_height,
        )

        self.ctx.input.wait_for_button()

    def _draw_progress_bar(self):
        offset_y = DEFAULT_PADDING + 2 * self.ctx.display.font_height
        pb_height = self.ctx.display.font_height - 4
        if len(self.rolls) > 0:  # Only draws if rolls > 0
            progress = min(self.min_rolls, len(self.rolls))
            progress *= self.ctx.display.usable_width()
            progress //= self.min_rolls
            progress -= 3
            self.ctx.display.fill_rectangle(
                DEFAULT_PADDING + 2,
                offset_y + 2,
                progress,
                (pb_height // 2) - 2,
                theme.fg_color,
            )

        shannon_entropy = int(self.shannons_entropy_rolls())
        if shannon_entropy:  # Only draws if Shannon's > 0
            shannon_progress = min(self.min_entropy, shannon_entropy)
            shannon_progress *= self.ctx.display.usable_width()
            shannon_progress //= self.min_entropy
            shannon_progress -= 3
            self.ctx.display.fill_rectangle(
                DEFAULT_PADDING + 2,
                offset_y + (pb_height // 2) + 1,
                shannon_progress,
                (pb_height // 2) - 2,
                theme.highlight_color,
            )
        if shannon_entropy >= self.min_entropy and len(self.rolls) >= self.min_rolls:
            outline_color = theme.go_color
        else:
            outline_color = theme.no_esc_color
        self.ctx.display.outline(
            DEFAULT_PADDING,
            offset_y,
            self.ctx.display.usable_width(),
            pb_height,
            outline_color,
        )

    def new_key(self):
        """Create a new key from dice rolls"""
        submenu = Menu(
            self.ctx,
            [
                (t("12 words"), lambda: MENU_EXIT),
                (t("24 words"), lambda: MENU_EXIT),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        index, _ = submenu.run_loop()
        if index == 2:
            return None

        if index == 0:
            self.min_entropy = MIN_ENTROPY_12W
            self.min_rolls = D20_12W_MIN_ROLLS if self.d_20 else D6_12W_MIN_ROLLS
        else:
            self.min_entropy = MIN_ENTROPY_24W
            self.min_rolls = D20_24W_MIN_ROLLS if self.d_20 else D6_24W_MIN_ROLLS
        self.ctx.display.clear()

        delete_flag = False
        self.ctx.display.draw_hcentered_text(
            t("Roll dice at least %d times to generate a mnemonic.") % (self.min_rolls)
        )
        if self.prompt(t("Proceed?"), self.ctx.display.bottom_prompt_line):

            def delete_roll(buffer):
                # buffer not used here
                nonlocal delete_flag
                delete_flag = True
                return buffer

            while True:
                roll = ""
                while True:
                    dice_title = t("Rolls: %d\n") % len(self.rolls)
                    entropy = (
                        "".join(self.rolls)
                        if self.len_states < 10
                        else "-".join(self.rolls)
                    )
                    if len(entropy) <= 10:
                        dice_title += entropy
                    else:
                        dice_title += "..." + entropy[-10:]
                    roll = self.capture_from_keypad(
                        dice_title,
                        [self.roll_states],
                        delete_key_fn=delete_roll,
                        progress_bar_fn=self._draw_progress_bar,
                        go_on_change=True,
                    )
                    if roll == ESC_KEY:
                        return None
                    break

                if roll != "":
                    self.rolls.append(roll)
                else:
                    # If its not a roll it is Del or Go
                    if delete_flag:  # Del
                        delete_flag = False
                        if len(self.rolls) > 0:
                            self.rolls.pop()
                    elif len(self.rolls) < self.min_rolls:  # Not enough to Go
                        self.flash_text(t("Not enough rolls!"))
                    elif self.shannons_entropy_rolls() < self.min_entropy:
                        self.ctx.display.clear()
                        self.ctx.display.draw_hcentered_text(
                            t("Poor entropy detected. More rolls are recommended")
                        )
                        if self.prompt(
                            t("Proceed anyway?"), self.ctx.display.bottom_prompt_line
                        ):
                            break
                    else:  # Go
                        break

            entropy = (
                "".join(self.rolls) if self.len_states < 10 else "-".join(self.rolls)
            )
            self.ctx.display.clear()
            rolls_str = t("Rolls:\n\n%s") % entropy
            self.ctx.display.draw_hcentered_text(rolls_str, info_box=True)

            submenu = Menu(
                self.ctx,
                [
                    (t("Stats for Nerds"), lambda: MENU_EXIT),
                    (t("Generate Words"), lambda: MENU_EXIT),
                ],
                offset=(len(self.ctx.display.to_lines(rolls_str)) + 1)
                * self.ctx.display.font_height,
            )
            index, _ = submenu.run_loop()
            if index == 0:
                self._stats_for_nerds()

            import hashlib
            import binascii

            entropy_bytes = entropy.encode()
            entropy_hash = binascii.hexlify(
                hashlib.sha256(entropy_bytes).digest()
            ).decode()
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("SHA256 of rolls:\n\n%s") % entropy_hash
            )
            self.ctx.input.wait_for_button()
            num_bytes = 16 if self.min_rolls == D20_12W_MIN_ROLLS else 32
            return hashlib.sha256(entropy_bytes).digest()[:num_bytes]

        return None
