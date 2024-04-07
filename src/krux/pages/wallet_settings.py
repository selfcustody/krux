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
from ..display import FONT_HEIGHT
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
ACCOUNT_MAX = 2**31 - 1  # Maximum account index


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
                disable_statusbar=True,
            )
            _, passphrase = submenu.run_loop()
            if passphrase in (ESC_KEY, MENU_EXIT):
                return None
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

    def customize_wallet(self, key):
        """Customize wallet derivation properties"""

        network = key.network
        multisig = key.multisig
        script_type = "84"  # TODO: Add script type selection
        account = key.account_index
        while True:
            derivation_path = "m/"
            derivation_path += "'/".join(
                [
                    "48" if multisig else script_type,
                    "0" if network == NETWORKS["main"] else "1",
                    str(account) + "'",
                ]
            )
            if multisig:
                derivation_path += "/2'"

            derivation_path = self.fit_to_line(derivation_path, crop_middle=False)
            self.ctx.display.draw_hcentered_text(derivation_path, info_box=True)
            submenu = Menu(
                self.ctx,
                [
                    (t("Network"), self._coin_type),
                    (t("Single/Multisig"), lambda: None),
                    (t("Script Type"), self._script_type if not multisig else None),
                    (t("Account"), lambda: None),
                    (t("Back"), lambda: MENU_EXIT),
                ],
                offset=2 * FONT_HEIGHT,
            )
            index, value = submenu.run_loop()
            if index == len(submenu.menu) - 1:
                break
            if index == 0:
                network = value
            elif index == 1:
                multisig = self._multisig()
            elif index == 2:
                script_type = value
            elif index == 3:
                account_temp = self._account(account)
                if account_temp is not None:
                    account = account_temp
        return network, multisig, script_type, account

    def _coin_type(self):
        """Network selection menu"""
        submenu = Menu(
            self.ctx,
            [
                (t("Mainnet"), lambda: None),
                (t("Testnet"), lambda: None),
            ],
            disable_statusbar=True,
        )
        index, _ = submenu.run_loop()
        return NETWORKS["test"] if index == 1 else NETWORKS["main"]

    def _multisig(self):
        """Multisig selection menu"""
        submenu = Menu(
            self.ctx,
            [
                (t("Single-sig"), lambda: MENU_EXIT),
                (t("Multisig"), lambda: MENU_EXIT),
            ],
            disable_statusbar=True,
        )
        index, _ = submenu.run_loop()
        return index == 1

    def _script_type(self):
        """Script type selection menu"""
        submenu = Menu(
            self.ctx,
            [
                (t("Legacy") + " - 44", None),  #  lambda: "44"),
                (t("Nested Segwit") + " - 49", None),  #  lambda: "49"),
                (t("Native Segwit") + " - 84", lambda: "84"),
                (t("Taproot") + " - 86", None),  # lambda: "86"),
            ],
            disable_statusbar=True,
        )
        _, purpose = submenu.run_loop()
        return purpose

    def _account(self, initial_account=None):
        """Account input"""
        account = self.capture_from_keypad(
            t("Account Index"),
            [DIGITS],
            starting_buffer=(
                str(initial_account) if initial_account is not None else ""
            ),
        )
        if account == ESC_KEY:
            return None
        try:
            account = int(account)
            if account > ACCOUNT_MAX:
                raise ValueError
        except:
            self.flash_text(t("Insert an account between 0 and %d") % ACCOUNT_MAX)
            return None
        return account
