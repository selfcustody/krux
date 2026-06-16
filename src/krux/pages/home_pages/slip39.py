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
from embit.slip39 import ShareSet, Share
from ...qr import FORMAT_NONE
from ...display import BOTTOM_PROMPT_LINE, FONT_HEIGHT, DEFAULT_PADDING
from ...krux_settings import t
from .. import (
    Menu,
    Page,
    MENU_CONTINUE,
)


class Slip39(Page):
    """UI for SLIP-39 Shamir backup and restore"""

    def _capture_passphrase(self):
        """Capture an optional passphrase from the user"""
        from ..utils import Utils

        utils = Utils(self.ctx)
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            t("Enter passphrase") + "\n\n" + t("(Optional)")
        )
        passphrase = utils.capture_from_keypad(
            t("Passphrase"),
            keysets=[],
            starting_buffer="",
        )
        if passphrase is None:
            return None
        return passphrase.encode("utf-8") if passphrase else b""

    def _capture_threshold(self, max_shares):
        """Capture threshold (k) value from user"""
        from ..utils import Utils

        utils = Utils(self.ctx)
        k = ""
        while k == "":
            k = utils.capture_index_from_keypad(
                t("Threshold"),
                initial_val="2",
                range_min=2,
                range_max=max_shares,
            )
        if k is None:
            return None
        return k

    def _capture_total_shares(self):
        """Capture total number of shares (n) from user"""
        from ..utils import Utils

        utils = Utils(self.ctx)
        n = ""
        while n == "":
            n = utils.capture_index_from_keypad(
                t("Total Shares"),
                initial_val="3",
                range_min=2,
                range_max=16,
            )
        if n is None:
            return None
        return n

    def backup(self):
        """Generate SLIP-39 shares from the current wallet mnemonic"""
        mnemonic = self.ctx.wallet.key.mnemonic
        word_count = len(mnemonic.split())

        if word_count not in (12, 24):
            self.flash_error(t("Only 12 or 24 word mnemonics supported"))
            return MENU_CONTINUE

        n = self._capture_total_shares()
        if n is None:
            return MENU_CONTINUE

        k = self._capture_threshold(n)
        if k is None:
            return MENU_CONTINUE

        passphrase = self._capture_passphrase()
        if passphrase is None:
            return MENU_CONTINUE

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Generating shares..."))

        try:
            shares = ShareSet.generate_shares(
                mnemonic=mnemonic,
                k=k,
                n=n,
                passphrase=passphrase,
            )
        except Exception as e:
            self.flash_error(str(e))
            return MENU_CONTINUE

        share_num = 0
        while share_num < len(shares):
            share_mnemonic = shares[share_num]
            title = t("Share") + " %d/%d" % (share_num + 1, len(shares))
            info = title + "\n\n" + share_mnemonic

            self.ctx.display.clear()
            info_len = self.ctx.display.draw_hcentered_text(
                info, info_box=True
            )
            info_len *= FONT_HEIGHT
            info_len += DEFAULT_PADDING

            menu_items = [
                (
                    t("QR Code"),
                    lambda m=share_mnemonic, t=title: self.display_qr_codes(
                        m, FORMAT_NONE, title=t
                    ),
                ),
            ]

            if self.has_sd_card():
                menu_items.append(
                    (
                        t("Save to SD card"),
                        lambda: self._save_shares_to_sd(shares, k, n),
                    )
                )

            submenu = Menu(
                self.ctx,
                menu_items,
                offset=info_len,
            )
            index, _ = submenu.run_loop()

            if index == submenu.back_index:
                if share_num > 0:
                    share_num -= 1
                else:
                    break
            else:
                share_num += 1

        return MENU_CONTINUE

    def _save_shares_to_sd(self, shares, k, n):
        """Save all shares to SD card as a text file"""
        from ..file_operations import SaveFile

        content = "SLIP-39 Shamir Backup\n"
        content += "Threshold: %d of %d\n\n" % (k, n)
        for i, share in enumerate(shares):
            content += "Share %d/%d:\n%s\n\n" % (i + 1, n, share)

        save_page = SaveFile(self.ctx)
        save_page.save_file(
            content,
            "slip39_shares",
            "slip39_shares",
            t("SLIP-39 Shares") + ":",
            ".txt",
            save_as_binary=False,
        )

    def restore(self):
        """Restore a mnemonic from SLIP-39 shares"""
        shares = []
        return self._restore_loop(shares)

    def restore_with_first_share(self, first_share):
        """Restore a mnemonic from SLIP-39 shares, starting with an already-detected share"""
        shares = [first_share]
        self.flash_text(t("Share") + " 1 %s" % t("added"))
        return self._restore_loop(shares)

    def _restore_loop(self, shares):
        """Core SLIP-39 share collection and recovery loop"""
        min_shares = 2

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            t("Scan or enter SLIP-39 shares")
        )

        while len(shares) < min_shares:
            share_text = self._capture_share()
            if share_text is None:
                if len(shares) == 0:
                    return MENU_CONTINUE
                break

            try:
                Share.parse(share_text)
                if share_text in shares:
                    self.flash_error(t("Duplicate share"))
                    continue
                shares.append(share_text)
                self.flash_text(
                    t("Share") + " %d %s" % (len(shares), t("added"))
                )
            except Exception as e:
                self.flash_error(t("Invalid share") + ": " + str(e))
                continue

            if len(shares) >= 2:
                self.ctx.display.clear()
                if not self.prompt(
                    t("Add more shares?") + "\n\n"
                    + t("Collected") + ": %d" % len(shares),
                    BOTTOM_PROMPT_LINE,
                ):
                    break

        passphrase = self._capture_passphrase()
        if passphrase is None:
            return MENU_CONTINUE

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Recovering..."))

        try:
            recovered_mnemonic = ShareSet.recover_mnemonic(
                share_mnemonics=shares,
                passphrase=passphrase,
            )
        except Exception as e:
            self.flash_error(t("Recovery failed") + ": " + str(e))
            return MENU_CONTINUE

        from ...key import Key
        from ...wallet import Wallet
        from ...krux_settings import Settings

        key = Key(
            recovered_mnemonic,
            self.ctx.wallet.key.policy_type,
            self.ctx.wallet.key.network,
            passphrase=passphrase.decode("utf-8") if passphrase else "",
        )

        self.ctx.display.clear()
        if not Settings().security.hide_mnemonic:
            self.display_mnemonic(
                recovered_mnemonic,
                suffix=t("Words"),
                fingerprint=key.fingerprint_hex_str(True),
            )
        else:
            self.ctx.display.draw_centered_text(
                key.fingerprint_hex_str(True)
            )

        if self.prompt(t("Load?"), BOTTOM_PROMPT_LINE):
            self.ctx.wallet = Wallet(key)
            self.flash_text(
                t("%s: loaded!") % key.fingerprint_hex_str(True),
                highlight_prefix=":",
            )

        return MENU_CONTINUE

    def _capture_share(self):
        """Capture a single SLIP-39 share via QR scan or manual input"""
        submenu = Menu(
            self.ctx,
            [
                (t("QR Code"), self._scan_share_qr),
                (t("Manual Input"), self._enter_share_manually),
            ],
        )
        index, _ = submenu.run_loop()
        if index == submenu.back_index:
            return None
        return getattr(self, "_last_share", None)

    def _scan_share_qr(self):
        """Scan a SLIP-39 share via QR code"""
        from ..qr_capture import QRScannerCapture

        qr_scanner = QRScannerCapture(self.ctx)
        data = qr_scanner.capture()
        if data:
            self._last_share = data
        return MENU_CONTINUE

    def _enter_share_manually(self):
        """Manually enter a SLIP-39 share as text"""
        from ..utils import Utils

        utils = Utils(self.ctx)
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Enter SLIP-39 share"))
        share_text = utils.capture_from_keypad(
            t("Share"),
            keysets=[],
            starting_buffer="",
        )
        if share_text:
            self._last_share = share_text
        return MENU_CONTINUE

    def export(self):
        """SLIP-39 menu"""
        submenu = Menu(
            self.ctx,
            [
                (t("Backup"), self.backup),
                (t("Restore"), self.restore),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE
