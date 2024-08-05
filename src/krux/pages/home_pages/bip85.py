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
from embit.bip32 import HARDENED_INDEX
from ...display import BOTTOM_PROMPT_LINE
from ...krux_settings import t
from ..settings_page import DIGITS
from ...krux_settings import Settings
from .. import (
    Page,
    ESC_KEY,
    MENU_CONTINUE,
    choose_len_mnemonic,
)


class Bip85(Page):
    """UI to export and load BIP85 entropy"""

    def export(self):
        """Exports BIP85 child mnemonics"""
        num_words = choose_len_mnemonic(self.ctx)
        if not num_words:
            return MENU_CONTINUE

        while True:
            child = self.capture_from_keypad(t("Child Index"), [DIGITS])
            if child == ESC_KEY:
                return None
            try:
                child_index = int(child)
            except:  # Empty input
                continue

            if child_index >= HARDENED_INDEX:
                self.flash_error(
                    t("Value %s out of range: [%s, %s]")
                    % (child_index, 0, HARDENED_INDEX - 1)
                )
                continue
            break
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
            script_type=self.ctx.wallet.key.script_type,
        )
        if not Settings().security.hide_mnemonic:
            self.display_mnemonic(
                bip85_words,
                suffix=t("Words") + "\n%s" % key.fingerprint_hex_str(True),
            )
        else:
            self.ctx.display.draw_centered_text(key.fingerprint_hex_str(True))
        if self.prompt(t("Load?"), BOTTOM_PROMPT_LINE):
            from ...wallet import Wallet

            self.ctx.wallet = Wallet(key)
        return None
