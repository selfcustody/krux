# The MIT License (MIT)

# Copyright (c) 2021-2026 Krux contributors

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

from .. import Menu, LETTERS, MENU_CONTINUE, MENU_EXIT, DIGITS, ESC_KEY
from ..mnemonic_loader import MnemonicLoader
from ...krux_settings import t
from ...kurihara import (
    KuriharaScheme,
    share_to_mnemonic,
    share_from_mnemonic,
    entropy_to_mnemonic,
)


class ThresholdBackup(MnemonicLoader):
    """Split or restore a mnemonic with an n-of-m threshold (Kurihara).

    A true threshold generalization of Mnemonic XOR (Seed XOR): any n of the m
    shares reconstruct the seed, while fewer than n reveal nothing, and each
    share is itself a valid BIP39 mnemonic. Unlike m-of-m Seed XOR, this
    tolerates losing up to m - n shares.

    Shares are derived deterministically from the secret (so repeating the split
    yields the same shares, like Coldcard's deterministic Seed XOR); the masks
    stay unpredictable to anyone holding fewer than n shares.
    """

    def __init__(self, ctx):
        super().__init__(ctx)
        self.captured_words = None

    @staticmethod
    def _deterministic_randfunc(entropy):
        """Reproducible mask stream keyed by the secret entropy"""
        counter = [0]

        def randfunc(nbytes):
            out = b""
            while len(out) < nbytes:
                out += hashlib.sha256(
                    b"krux-threshold" + entropy + counter[0].to_bytes(4, "big")
                ).digest()
                counter[0] += 1
            return out[:nbytes]

        return randfunc

    def _capture_int(self, title):
        """Capture a positive integer from the numeric keypad (None if cancelled)"""
        value = self.capture_from_keypad(title, [DIGITS])
        if value in (ESC_KEY, ""):
            return None
        return int(value)

    def _info(self, text):
        """Show an already-translated centered message and wait for a button"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(text)
        self.ctx.input.wait_for_button()

    # ----- Split -----

    def _choose_scheme(self, num_bits):
        """Ask for m then n on the keypad, retrying with guidance if invalid"""
        while True:
            m = self._capture_int(t("Total shares to create (m), 2 to 5"))
            if m is None:
                return None
            n = self._capture_int(t("Shares needed to restore (n), 2 to m"))
            if n is None:
                return None
            if 2 <= m <= 5 and 2 <= n <= m:
                return KuriharaScheme(n, m, num_bits)
            self._info(
                t(
                    "Create m shares (m from 2 to 5) and need n of them to "
                    "restore (n from 2 to m). For example 2-of-3 or 3-of-5."
                )
            )

    def split(self):
        """Split the current mnemonic into threshold shares for backup"""
        from embit.bip39 import mnemonic_to_bytes

        mnemonic = self.ctx.wallet.key.mnemonic
        entropy = mnemonic_to_bytes(mnemonic)
        num_bits = len(entropy) * 8

        scheme = self._choose_scheme(num_bits)
        if scheme is None:
            return MENU_CONTINUE

        self.ctx.display.clear()
        if not self.prompt(
            t("Split into %d shares, any %d restore the seed?") % (scheme.m, scheme.n),
            self.ctx.display.height() // 2,
        ):
            return MENU_CONTINUE

        shares = scheme.generate(entropy, self._deterministic_randfunc(entropy))
        self._browse_shares(shares, scheme.m)
        return MENU_CONTINUE

    def _show_share(self, share, m):
        """Display one share full-screen as a BIP39 mnemonic"""
        self.display_mnemonic(
            share_to_mnemonic(share),
            title=t("Share %d of %d") % (share.part_id, m),
        )
        self.ctx.input.wait_for_button()
        return MENU_CONTINUE

    def _browse_shares(self, shares, m):
        """Browse the shares, then confirm they were written down"""
        while True:
            items = [
                (
                    t("Share %d of %d") % (share.part_id, m),
                    lambda share=share: self._show_share(share, m),
                )
                for share in shares
            ]
            items.append((t("I saved all shares"), lambda: MENU_EXIT))
            menu = Menu(self.ctx, items)
            index, _ = menu.run_loop()
            if index == menu.back_index:
                return
            if self.prompt(
                t(
                    "Have you written down all %d shares? "
                    "They will not be shown again."
                )
                % m,
                self.ctx.display.height() // 2,
            ):
                return

    # ----- Restore -----

    def _load_key_from_words(self, words, charset=LETTERS, new=False):
        """Capture hook for recover(): keep the entered words and exit the loader"""
        self.captured_words = words
        return MENU_EXIT

    def _collect_shares(self, n, m):
        """Collect n shares (number + mnemonic each); None on cancel/mismatch"""
        from embit.bip39 import mnemonic_to_bytes

        shares = []
        num_bits = None
        for _ in range(n):
            part_id = self._capture_int(t("Share number (1 to m)"))
            if part_id is None or not 1 <= part_id <= m:
                return None
            self.captured_words = None
            self.load_key()
            if not self.captured_words:
                return None
            mnemonic = " ".join(self.captured_words)
            bits = len(mnemonic_to_bytes(mnemonic)) * 8
            if num_bits is None:
                num_bits = bits
            try:
                shares.append(share_from_mnemonic(part_id, mnemonic, n, m, num_bits))
            except ValueError:
                self._info(t("All shares must have the same number of words."))
                return None
        return shares

    def restore(self):
        """Reconstruct a mnemonic from n threshold shares.

        Returns the recovered BIP39 mnemonic (str), or None if cancelled. The
        caller loads it through the normal flow (e.g. Login._load_key_from_words),
        so this works both at login and with a key already loaded.
        """
        m = self._capture_int(t("Total shares created (m), 2 to 5"))
        if m is None:
            return None
        n = self._capture_int(t("Shares you have (n), 2 to m"))
        if n is None:
            return None
        if not 2 <= m <= 5 or not 2 <= n <= m:
            self._info(
                t(
                    "Create m shares (m from 2 to 5) and need n of them to "
                    "restore (n from 2 to m). For example 2-of-3 or 3-of-5."
                )
            )
            return None

        shares = self._collect_shares(n, m)
        if shares is None:
            return None

        try:
            num_bits = len(shares[0].to_bytes()) * 8
            secret = KuriharaScheme(n, m, num_bits).reconstruct(shares)
        except ValueError:
            self._info(t("Could not reconstruct. Check the share numbers and retry."))
            return None

        return entropy_to_mnemonic(secret)
