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
from embit.bip32 import HARDENED_INDEX
from ..display import FONT_HEIGHT, DEFAULT_PADDING, BOTTOM_PROMPT_LINE
from ..krux_settings import t
from . import (
    Page,
    Menu,
    DIGITS,
    MENU_CONTINUE,
    MENU_EXIT,
    ESC_KEY,
    LETTERS,
    UPPERCASE_LETTERS,
    NUM_SPECIAL_1,
    NUM_SPECIAL_2,
)
from ..key import (
    SINGLESIG_SCRIPT_PURPOSE,
    MULTISIG_SCRIPT_PURPOSE,
    MINISCRIPT_PURPOSE,
    TYPE_SINGLESIG,
    TYPE_MULTISIG,
    TYPE_MINISCRIPT,
)
from ..settings import (
    MAIN_TXT,
    TEST_TXT,
)
from ..key import P2PKH, P2SH_P2WPKH, P2WPKH, P2WSH, P2TR

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
                    (t("Type BIP39 Passphrase"), self._load_passphrase),
                    (t("Scan BIP39 Passphrase"), self._load_qr_passphrase),
                ],
                disable_statusbar=True,
            )
            _, passphrase = submenu.run_loop()
            if passphrase in (ESC_KEY, MENU_EXIT):
                return None
            self.ctx.display.clear()
            self.ctx.display.draw_hcentered_text(t("Passphrase") + ": " + passphrase)
            if self.prompt(
                t("Proceed?"),
                BOTTOM_PROMPT_LINE,
            ):
                return passphrase

    def _load_passphrase(self):
        """Loads and returns a passphrase from keypad"""
        data = self.capture_from_keypad(
            t("Passphrase"), [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2]
        )
        if len(str(data)) > PASSPHRASE_MAX_LEN:
            raise ValueError("Maximum length exceeded (%s)" % PASSPHRASE_MAX_LEN)
        return data

    def _load_qr_passphrase(self):
        from .qr_capture import QRCodeCapture

        qr_capture = QRCodeCapture(self.ctx)
        data, _ = qr_capture.qr_capture_loop()
        if data is None:
            self.flash_error(t("Failed to load"))
            return MENU_CONTINUE
        if len(data) > PASSPHRASE_MAX_LEN:
            raise ValueError("Maximum length exceeded (%s)" % PASSPHRASE_MAX_LEN)
        return data


class WalletSettings(Page):
    """Class for customizing wallet derivation path"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def customize_wallet(self, key):
        """Customize wallet derivation properties"""

        network = key.network
        policy_type = key.policy_type
        script_type = key.script_type
        account = key.account_index
        while True:
            derivation_path = "m/"
            if policy_type == TYPE_SINGLESIG:
                derivation_path += str(SINGLESIG_SCRIPT_PURPOSE[script_type])
            elif policy_type == TYPE_MULTISIG:
                derivation_path += str(MULTISIG_SCRIPT_PURPOSE)
            elif policy_type == TYPE_MINISCRIPT:
                # For now, miniscript is the same as multisig
                derivation_path += str(MINISCRIPT_PURPOSE)
            derivation_path += "'/"
            derivation_path += "0'" if network == NETWORKS[MAIN_TXT] else "1'"
            derivation_path += "/" + str(account) + "'"
            if policy_type in (TYPE_MULTISIG, TYPE_MINISCRIPT):
                derivation_path += "/2'"

            self.ctx.display.clear()
            derivation_path = self.fit_to_line(derivation_path, crop_middle=False)
            info_len = self.ctx.display.draw_hcentered_text(
                derivation_path, info_box=True
            )
            submenu = Menu(
                self.ctx,
                [
                    (t("Network"), lambda: None),
                    (t("Policy Type"), lambda: None),
                    (
                        t("Script Type"),
                        (lambda: None) if policy_type == TYPE_SINGLESIG else None,
                    ),
                    (t("Account"), lambda: None),
                ],
                offset=info_len * FONT_HEIGHT + DEFAULT_PADDING,
            )
            index, _ = submenu.run_loop()
            if index == len(submenu.menu) - 1:
                break
            if index == 0:
                new_network = self._coin_type()
                if new_network is not None:
                    network = new_network
            elif index == 1:
                new_policy_type = self._policy_type()
                if new_policy_type is not None:
                    policy_type = new_policy_type
                    if policy_type == TYPE_SINGLESIG and script_type == P2WSH:
                        # If is single-sig, and script is p2wsh, force to pick a new type
                        script_type = self._script_type()
                        script_type = P2WPKH if script_type is None else script_type
            elif index == 2:
                new_script_type = self._script_type()
                if new_script_type is not None:
                    script_type = new_script_type
            elif index == 3:
                account_temp = self._account(account)
                if account_temp is not None:
                    account = account_temp
        if policy_type != TYPE_SINGLESIG:
            script_type = P2WSH
        return network, policy_type, script_type, account

    def _coin_type(self):
        """Network selection menu"""
        submenu = Menu(
            self.ctx,
            [
                ("Mainnet", lambda: None),
                ("Testnet", lambda: None),
            ],
            disable_statusbar=True,
        )
        index, _ = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return None
        return NETWORKS[TEST_TXT] if index == 1 else NETWORKS[MAIN_TXT]

    def _policy_type(self):
        """Policy type selection menu"""
        submenu = Menu(
            self.ctx,
            [
                ("Single-sig", lambda: MENU_EXIT),
                ("Multisig", lambda: MENU_EXIT),
                ("Miniscript (Experimental)", lambda: MENU_EXIT),
            ],
            disable_statusbar=True,
        )
        index, _ = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return None
        return index  # Index is equal to the policy types IDs

    def _script_type(self):
        """Script type selection menu"""
        submenu = Menu(
            self.ctx,
            [
                ("Legacy - 44", lambda: P2PKH),
                ("Nested Segwit - 49", lambda: P2SH_P2WPKH),
                ("Native Segwit - 84", lambda: P2WPKH),
                ("Taproot - 86 (Experimental)", lambda: P2TR),
            ],
            disable_statusbar=True,
        )
        index, script_type = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return None
        return script_type

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
            if account >= HARDENED_INDEX:
                raise ValueError
        except:
            self.flash_error(
                t("Value %s out of range: [%s, %s]") % (account, 0, HARDENED_INDEX - 1)
            )
            return None
        return account
