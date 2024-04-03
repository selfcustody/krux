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

from embit.networks import NETWORKS
from ..krux_settings import t
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
    ESC_KEY,
    LETTERS,
    UPPERCASE_LETTERS,
    NUM_SPECIAL_1,
    NUM_SPECIAL_2,
)
from .settings_page import DIGITS

PASSPHRASE_MAX_LEN = 200


class PassphraseEditor(Page):
    """Class for adding or editing a passphrase"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def load_passphrase_menu(self):
        """Load a passphrase from keypad or QR code"""
        passphrase = ""
        while True:
            submenu = Menu(
                self.ctx,
                [
                    (t("Type BIP39 passphrase"), self._load_passphrase),
                    (t("Scan BIP39 passphrase"), self._load_qr_passphrase),
                    (t("Back"), lambda: MENU_EXIT),
                ],
            )
            _, passphrase = submenu.run_loop()
            if passphrase in (ESC_KEY, MENU_EXIT):
                return MENU_CONTINUE
            self.ctx.display.clear()
            if self.prompt(
                t("Passphrase") + ": " + passphrase,
                self.ctx.display.height() // 2,
            ):
                return passphrase

    def _load_passphrase(self):
        """Loads and returns a passphrase from keypad"""
        return self.capture_from_keypad(
            t("Passphrase"), [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2]
        )

    def _load_qr_passphrase(self):
        data, _ = self.capture_qr_code()
        if data is None:
            self.flash_error(t("Failed to load passphrase"))
            return MENU_CONTINUE
        if len(data) > PASSPHRASE_MAX_LEN:
            self.flash_error(t("Maximum length exceeded (%s)") % PASSPHRASE_MAX_LEN)
            return MENU_CONTINUE
        return data


class WalletSettings(Page):
    """Class for customizing wallet derivation path"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def customize_wallet(
        self,
        network,
        multisig=False,
        script_type=None,
        account_number=0,
    ):
        """Customize wallet derivation properties"""

        while True:
            submenu = Menu(
                self.ctx,
                [
                    (t("Network"), lambda: None),
                    (t("Single/Multisig"), lambda: None),
                    (t("Script Type"), None),
                    (t("Account"), lambda: None if not multisig else None),
                    (t("Back"), lambda: MENU_EXIT),
                ],
            )
            index, _ = submenu.run_loop()
            if index == len(submenu.menu) - 1:
                break
            if index == 0:
                network = self._testnet()
            elif index == 1:
                multisig = self._multisig()
            elif index == 3:
                account_temp = self._account_number()
                if account_temp is not None:
                    account_number = account_temp
        return network, multisig, script_type, account_number

    def _testnet(self):
        """Network selection menu"""
        submenu = Menu(
            self.ctx,
            [
                (t("Mainnet"), lambda: None),
                (t("Testnet"), lambda: None),
            ],
        )
        index, _ = submenu.run_loop()
        return NETWORKS["test"] if index == 1 else NETWORKS["main"]

    def _multisig(self):
        """Multisig selection menu"""
        submenu = Menu(
            self.ctx,
            [
                (t("Single-sig"), lambda: None),
                (t("Multisig"), lambda: None),
            ],
        )
        index, _ = submenu.run_loop()
        return index == 1

    def _account_number(self):
        """Account number input"""
        account = self.capture_from_keypad(t("Account Number"), [DIGITS])
        if account == ESC_KEY:
            return None
        try:
            account_number = int(account)
            if account_number > 999:
                raise ValueError
        except:
            self.flash_text(t("Insert an account between 0 and 999"))
            return None
        return account_number
