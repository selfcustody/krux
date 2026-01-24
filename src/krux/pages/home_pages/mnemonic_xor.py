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

import math
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
    def _shannon_sum(distribution, sample_size):
        """Calculates Shannon's entropy of a given distribution."""
        # Calculate entropy
        unit_entropy = 0
        for count in distribution:
            probability = count / sample_size
            unit_entropy -= probability * (probability and math.log2(probability))
        return unit_entropy

    @staticmethod
    def _bits_of_bytes(data: bytes | bytearray) -> str:
        """MSB-first bitstring; used to form 11-bit tokens."""
        return "".join("{:08b}".format(b) for b in data)

    @staticmethod
    def _word11_histogram(entropy: bytes | bytearray) -> list[int]:
        """2048-bucket histogram of BIP-39 11-bit word indices derived from entropy||checksum."""
        import uhashlib_hw

        # length of the bitstream
        ent_bits = len(entropy) * 8

        # length of the checksum
        cs_len = ent_bits // 32

        # ENT: entropy
        s = MnemonicXOR._bits_of_bytes(entropy)

        # CS: checksum
        sha_s = uhashlib_hw.sha256(entropy).digest()
        cs_bits = MnemonicXOR._bits_of_bytes(sha_s)
        checksum = cs_bits[:cs_len]

        # A full bitstream is the concatenation of ENT || CS
        bitstream = s + checksum

        # 11 bit word (parts of 11 bits of ENT || CS) histogram
        m = (ent_bits + cs_len) // 11
        counts = [0] * 2048
        for i in range(m):
            idx = int(bitstream[i * 11 : (i + 1) * 11], 2)
            counts[idx] += 1
        return counts

    @staticmethod
    def _validate_entropy(entropy: bytes | bytearray) -> float | None:
        """Check for low entropy against its distribution"""
        allzero_entropy = bytearray(len(entropy))
        full_ff_entropy = bytearray([0xFF for i in range(len(entropy))])

        if entropy == allzero_entropy:
            raise ValueError("Low entropy (got [0x00; 32])")

        if entropy == full_ff_entropy:
            raise ValueError("Low entropy (got [0xFF; 32])")

        word_counts: list[int] = MnemonicXOR._word11_histogram(entropy)

        # This value is a random one got in some tests made in
        # `tests/pages/home_pages/test_mnemonic_xor.py::test_export_xor_fail_low_entropy`
        # method. We have three values and got one that could appear a middle term between
        # all 0x00 or all 0xFF (near 0.42), a dangerous one (near 2.29) and a acceptable
        # one (near 3.42). We couldn't assert a "very good one" (we don't know the tip value
        # for that, I'm assuming that could be 5.0). This value cannot guarantee the quality
        # of the entropy, just how much information we have in a mix of real data plus its
        # checksum. This value is a minimum accepable quantity of bits per 11bit word bits
        # of that type of data. (something like 3.42 bits/word).
        threshold = getattr(Settings().security, "entropy_threshold", 3.42)

        bits_per_word = MnemonicXOR._shannon_sum(word_counts, sum(word_counts))
        if bits_per_word < threshold:
            raise ValueError("Low entropy (got {:1f} bits/word)".format(bits_per_word))

    def _xor_with_current_mnemonic(self, mnemonic_to_xor: str) -> str:
        """XOR current mnemonic with a new one following SeedXOR implementation"""
        from embit.bip39 import mnemonic_from_bytes, mnemonic_to_bytes

        # Validate same word count
        current_word_count = len(self.ctx.wallet.key.mnemonic.split())
        to_xor_word_count = len(mnemonic_to_xor.split())
        if current_word_count != to_xor_word_count:
            raise AttributeError("Mnemonics should have same length")

        # Convert and validate entropies
        entropy_a = mnemonic_to_bytes(self.ctx.wallet.key.mnemonic)
        entropy_b = mnemonic_to_bytes(mnemonic_to_xor)

        # The A is the current entropy, so no need to validate
        # (we assume that user followed the guidelines and
        # alreay validated the entropy).
        # But B and C should be validated
        self._validate_entropy(entropy_b)

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

    def _load_xored_mnemonic(self, fingerprint_to_xor, xored_mnemonic):
        """Load and display the xored mnemonic and its made operations"""
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

        # Show the XOR result
        if xored_mnemonic is not None:
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

    def _load_key_from_words(self, words, charset=LETTERS, new=False):
        """
        Similar method from krux.pages.login.Login without loading a key,
        instead, it add the bytes from a mnemonic's entropy to the list of entropies
        """
        import time

        # This method could be used in a custom manner since it is the "final"
        # step between choosing and loading.
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

        # XOR the mnemonic entropy and if we receive any error, just warn the user.
        try:
            xored_mnemonic = self._xor_with_current_mnemonic(mnemonic_to_xor)
            return self._load_xored_mnemonic(fingerprint_to_xor, xored_mnemonic)
        except Exception as e:
            self.ctx.display.clear()
            lines = ["%s:\n%s" % (fingerprint_to_xor, str(e))]
            self.ctx.display.draw_hcentered_text(lines)
            time.sleep(3)
            self.ctx.display.clear()

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
