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
from embit import bip85
from ...display import BOTTOM_PROMPT_LINE
from ...krux_settings import t
from ..settings_page import DIGITS
from ...krux_settings import Settings
from .. import (
    Page,
    Menu,
    ESC_KEY,
    MENU_EXIT,
)

MAX_BIP85_CHILD_INDEX = 2**31 - 1


class Bip85(Page):
    """UI to export and load BIP85 entropy"""

    def export(self):
        """Exports BIP85 child mnemonics"""
        submenu = Menu(
            self.ctx,
            [
                (t("12 words"), lambda: MENU_EXIT),
                (t("24 words"), lambda: MENU_EXIT),
            ],
        )
        menu_index, _ = submenu.run_loop()
        num_words = 12 if menu_index == 0 else 24
        while True:
            child = self.capture_from_keypad(t("Child Index"), [DIGITS])
            if child == ESC_KEY:
                return None
            try:
                child_index = int(child)
                if child_index > MAX_BIP85_CHILD_INDEX:
                    raise ValueError
                break
            except ValueError:
                self.flash_error(
                    t("Please insert a value between 0 and %d") % MAX_BIP85_CHILD_INDEX
                )
                continue
        bip85_words = bip85.derive_mnemonic(
            self.ctx.wallet.key.root,
            num_words,
            child_index,
        )
        self.ctx.display.clear()

        from ...key import Key

        key = Key(
            bip85_words,
            self.ctx.wallet.key.multisig,
            self.ctx.wallet.key.network,
        )
        if not Settings().security.hide_mnemonic:
            self.display_mnemonic(
                bip85_words,
                suffix=t("Words") + "\n%s" % key.fingerprint_hex_str(True),
            )
        else:
            self.ctx.display.draw_centered_text(key.fingerprint_hex_str(True))
        if self.prompt(t("Load child?"), BOTTOM_PROMPT_LINE):
            from ...wallet import Wallet

            self.ctx.wallet = Wallet(key)
        return None
