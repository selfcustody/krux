# The MIT License (MIT)

# Copyright (c) 2021-2025 Krux contributors

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

from .. import Menu, LETTERS, MENU_CONTINUE, MENU_EXIT
from ..login import MnemonicLoader
from ...krux_settings import Settings, t
from ...display import BOTTOM_PROMPT_LINE, FONT_HEIGHT
from ...themes import theme
from ...key import Key
from ...wallet import Wallet


class MnemonicXOR(MnemonicLoader):
    """
    UI to apply a exclusive-or operation between the current mnemonic entropy with
    chosen mnemonic entropies
    """

    # See implementation reference at
    # https://github.com/Coldcard/firmware/blob/2445b4d4350d0aad0f4ef8f966697a67ab9ecbdc/shared/utils.py#L752
    @staticmethod
    def _xor_bytes(a: bytes, b: bytes) -> bytearray:
        """XOR two byte sequences of equal length"""

        # All sequences should have same length because it would
        # reveal the last bytes from the longer bytestring as they are.
        # In the case of mnemonics, it might reveal last 12 words.
        if len(a) != len(b):
            raise ValueError("Sequences should have same length")

        out = bytearray(len(b))
        for i in range(len(b)):
            out[i] = a[i] ^ b[i]

        return out

    @staticmethod
    def _validate_entropy(entropy: bytes | bytearray) -> None:
        """Check for low entropy (all zeros or all ones)"""
        # TODO: apply a shannon low entropy check for XOR
        all_zeros = bytes(len(entropy))
        all_ones = b"\xff" * len(entropy)
        if entropy in (all_zeros, all_ones):
            raise ValueError("Low entropy mnemonic")

    @staticmethod
    def _check_last_word(words):
        _words = words.split(" ")
        main_words = _words[:-1]
        last_word = _words[-1:][0]

        if last_word not in Key.get_final_word_candidates(main_words):
            raise ValueError("Invalid checksum word: %s" % last_word)

    def xor_with_current_mnemonic(self, mnemonic_to_xor: str) -> str:
        """XOR current mnemonic with a new one following SeedXOR implementation"""
        from embit.bip39 import mnemonic_from_bytes, mnemonic_to_bytes

        # Validate same word count
        current_word_count = len(self.ctx.wallet.key.mnemonic.split())
        to_xor_word_count = len(mnemonic_to_xor.split())
        if current_word_count != to_xor_word_count:
            raise ValueError("Mnemonics should have same length")

        # Convert and validate entropies
        entropy_a = mnemonic_to_bytes(self.ctx.wallet.key.mnemonic)
        entropy_b = mnemonic_to_bytes(mnemonic_to_xor)
        self._validate_entropy(entropy_a)
        self._validate_entropy(entropy_b)

        # XOR and validate result
        new_entropy = self._xor_bytes(entropy_a, entropy_b)
        self._validate_entropy(new_entropy)

        return mnemonic_from_bytes(new_entropy)

    def _display_key_info(self, mnemonic: str, fingerprint: str, title: str) -> None:
        """Display mnemonic or fingerprint based on hide_mnemonic setting"""

        if not Settings().security.hide_mnemonic:
            self.display_mnemonic(
                mnemonic,
                title=title,
                fingerprint=fingerprint,
            )
        else:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                title + " " + fingerprint,
                color=theme.highlight_color,
            )

    def _load_key_from_words(self, words, charset=LETTERS, new=False):
        """
        Similar method from krux.pages.login.Login without loading a key,
        instead, it add the bytes from a mnemonic's entropy to the list of entropies
        """

        mnemonic_to_xor = " ".join(words)
        fingerprint_to_xor = Key.extract_fingerprint(mnemonic_to_xor)

        # Show the mnemonic to XOR with
        self._display_key_info(
            mnemonic_to_xor,
            fingerprint_to_xor,
            t("XOR With") + ":",
        )

        if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
            return MENU_CONTINUE

        self.ctx.display.clear()

        xored_mnemonic = self.xor_with_current_mnemonic(mnemonic_to_xor)
        xored_fingerprint = Key.extract_fingerprint(xored_mnemonic)

        # Display XOR operation and resulting fingerprint:
        offset_y = (self.ctx.display.height() // 2) - FONT_HEIGHT * 3
        lines = [
            Key.extract_fingerprint(self.ctx.wallet.key.mnemonic),
            "XOR",
            fingerprint_to_xor,
            "=",
        ]
        self.ctx.display.draw_hcentered_text(lines, offset_y, theme.fg_color)
        self.ctx.display.draw_hcentered_text(
            xored_fingerprint,
            offset_y + FONT_HEIGHT * len(lines),
            theme.highlight_color,
        )

        if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
            return MENU_CONTINUE

        # If last word do not match, raise an error
        MnemonicXOR._check_last_word(xored_mnemonic)

        # Show the XOR result
        self._display_key_info(
            xored_mnemonic,
            xored_fingerprint,
            t("XOR Result") + ":",
        )

        if self.prompt(t("Load?"), BOTTOM_PROMPT_LINE):
            xored_key = Key(
                xored_mnemonic,
                self.ctx.wallet.key.policy_type,
                self.ctx.wallet.key.network,
                "",
                self.ctx.wallet.key.account_index,
                self.ctx.wallet.key.script_type,
            )
            self.ctx.wallet = Wallet(xored_key)
            self.flash_text(
                t("%s: loaded!") % xored_fingerprint,
                highlight_prefix=":",
            )

        return MENU_EXIT

    def choose_len_mnemonic(self, extra_option=""):
        """XOR '12 or 24 words?" menu choice"""
        items = []
        if len(self.ctx.wallet.key.mnemonic.split(" ")) == 12:
            items.append((t("12 words"), lambda: 12))
        else:
            items.append((t("24 words"), lambda: 24))
        submenu = Menu(self.ctx, items, back_status=lambda: None)
        _, num_words = submenu.run_loop()
        self.ctx.display.clear()
        return num_words
