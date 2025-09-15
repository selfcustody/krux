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
    NAME_SINGLE_SIG,
    NAME_MULTISIG,
    NAME_MINISCRIPT,
)

from ..settings import (
    MAIN_TXT,
    TEST_TXT,
)

from ..key import P2PKH, P2SH, P2SH_P2WPKH, P2SH_P2WSH, P2WPKH, P2WSH, P2TR

PASSPHRASE_MAX_LEN = 200
DERIVATION_KEYPAD = "1234567890/h"

P2SH_DEFAULT_DERIVATION = "m/45h"
MINISCRIPT_DEFAULT_DERIVATION = "m/48h/0h/0h/2h"


class PassphraseEditor(Page):
    """Class for adding or editing a passphrase"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def load_passphrase_menu(self, mnemonic):
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

            from ..themes import theme
            from ..key import Key

            self.ctx.display.clear()
            self.ctx.display.draw_hcentered_text(
                Key.extract_fingerprint(mnemonic, passphrase),
                color=theme.highlight_color,
            )
            self.ctx.display.draw_hcentered_text(
                t("Passphrase") + " (%d):" % len(passphrase),
                DEFAULT_PADDING + FONT_HEIGHT * 2,
                theme.highlight_color,
            )
            self.ctx.display.draw_hcentered_text(
                passphrase, DEFAULT_PADDING + FONT_HEIGHT * 3
            )
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
        from .encryption_ui import decrypt_kef

        qr_capture = QRCodeCapture(self.ctx)
        data, _ = qr_capture.qr_capture_loop()
        if data is None:
            self.flash_error(t("Failed to load"))
            return MENU_CONTINUE

        try:
            data = decrypt_kef(self.ctx, data).decode()
        except KeyError:
            self.flash_error(t("Failed to decrypt"))
            return MENU_CONTINUE
        except ValueError:
            # ValueError=not KEF or declined to decrypt
            pass

        if len(data) > PASSPHRASE_MAX_LEN:
            raise ValueError("Maximum length exceeded (%s)" % PASSPHRASE_MAX_LEN)
        return data


class WalletSettings(Page):
    """Class for customizing wallet derivation path"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def _get_account_text_from_policy_type(self, policy_type, script_type):
        """Get the account text based on policy type and script type"""
        if (
            policy_type == TYPE_MULTISIG and script_type == P2SH
        ) or policy_type == TYPE_MINISCRIPT:
            return t("Derivation Path")

        return t("Account")

    def customize_wallet(self, key):
        """Customize wallet derivation properties"""
        from ..themes import theme
        from .utils import Utils

        utils = Utils(self.ctx)
        network = key.network
        policy_type = key.policy_type
        script_type = key.script_type
        account = key.account_index
        derivation_path = key.derivation
        while True:
            network_name = network["name"]
            if not derivation_path:
                derivation_path = self._derivation_path_str(
                    policy_type, script_type, network, account
                )

            wallet_info = utils.generate_wallet_info(
                network_name, policy_type, script_type, derivation_path
            )

            self.ctx.display.clear()
            derivation_path = self.fit_to_line(derivation_path, crop_middle=False)
            info_len = self.ctx.display.draw_hcentered_text(wallet_info, info_box=True)

            # if the wallet is P2SH, we need to change
            # the "Account" label to "Cossiger Index"
            # as well if it uses a miniscript policy
            # type we need to change it to "Derivation Path"
            account_txt = self._get_account_text_from_policy_type(
                policy_type, script_type
            )

            submenu = Menu(
                self.ctx,
                [
                    (t("Network"), lambda: None),
                    (t("Policy Type"), lambda: None),
                    (t("Script Type"), lambda: None),
                    (account_txt, lambda: None),
                ],
                offset=info_len * FONT_HEIGHT + DEFAULT_PADDING,
            )

            # draw network with highlight color
            self.ctx.display.draw_hcentered_text(
                network_name,
                color=Utils.get_network_color(network_name),
                bg_color=theme.info_bg_color,
            )

            index, _ = submenu.run_loop()
            if index == submenu.back_index:
                break
            if index == 0:
                new_network = self._coin_type()
                if new_network is not None:
                    derivation_path = ""
                    network = new_network
            elif index == 1:
                new_policy_type = self._policy_type()
                if new_policy_type is not None:
                    derivation_path = ""
                    policy_type = new_policy_type
                    if (
                        policy_type == TYPE_SINGLESIG
                        and script_type not in SINGLESIG_SCRIPT_PURPOSE
                    ):
                        # If is single-sig, and script is p2wsh, force to pick a new type
                        script_type = self._script_type()
                        script_type = P2WPKH if script_type is None else script_type

                    elif (
                        policy_type == TYPE_MULTISIG
                        and script_type not in MULTISIG_SCRIPT_PURPOSE
                    ):
                        # If is multisig,force to p2wsh if not set
                        script_type = self._script_type_multisig()
                        script_type = P2WSH if script_type is None else script_type

                    elif policy_type == TYPE_MINISCRIPT and script_type not in (
                        P2WSH,
                        P2TR,
                    ):
                        # If is miniscript, pick P2WSH or P2TR
                        script_type = self._miniscript_type()
                        script_type = P2WSH if script_type is None else script_type

            elif index == 2:
                if policy_type == TYPE_MINISCRIPT:
                    new_script_type = self._miniscript_type()
                elif policy_type == TYPE_MULTISIG:
                    new_script_type = self._script_type_multisig()
                else:
                    new_script_type = self._script_type()
                if new_script_type is not None:
                    derivation_path = ""
                    script_type = new_script_type
            elif index == 3:
                if policy_type != TYPE_MINISCRIPT and not (
                    policy_type == TYPE_MULTISIG and script_type == P2SH
                ):
                    new_account = utils.capture_index_from_keypad(
                        t("Account Index"), account
                    )
                    if new_account not in (None, ""):
                        derivation_path = ""
                        account = new_account
                else:
                    new_derivation_path = self._derivation_path(derivation_path)
                    if new_derivation_path is not None:
                        derivation_path = new_derivation_path
        return network, policy_type, script_type, account, derivation_path

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
        if index == submenu.back_index:
            return None
        return NETWORKS[TEST_TXT] if index == 1 else NETWORKS[MAIN_TXT]

    def _policy_type(self):
        """Policy type selection menu"""
        submenu = Menu(
            self.ctx,
            [
                (NAME_SINGLE_SIG, lambda: MENU_EXIT),
                (NAME_MULTISIG, lambda: MENU_EXIT),
                (NAME_MINISCRIPT + " (Experimental)", lambda: MENU_EXIT),
            ],
            disable_statusbar=True,
        )
        index, _ = submenu.run_loop()
        if index == submenu.back_index:
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
        if index == submenu.back_index:
            return None
        return script_type

    def _script_type_multisig(self):
        """Script type selection menu"""
        submenu = Menu(
            self.ctx,
            [
                ("Legacy - 45", lambda: P2SH),
                ("Nested Segwit - 48", lambda: P2SH_P2WSH),
                ("Native Segwit - 48", lambda: P2WSH),
            ],
            disable_statusbar=True,
        )
        index, script_type = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return None
        return script_type

    def _miniscript_type(self):
        """Script type selection menu for miniscript policy type"""
        submenu = Menu(
            self.ctx,
            [
                ("Native Segwit - P2WSH", lambda: P2WSH),
                ("Taproot - P2TR", lambda: P2TR),
            ],
            disable_statusbar=True,
        )
        index, script_type = submenu.run_loop()
        if index == submenu.back_index:
            return None
        return script_type

    def _derivation_path_str(self, policy_type, script_type, network, account):
        # While BIP45 states that m/45h/<n> -- where <n> is the
        # cosiger index (non hardened) -- this is a very old BIP
        # and not many wallets support it. Also Seedsigner and
        # Sparrow uses m/45h as default derivation path. Therefore
        # to maintain compatibility with those wallets, use m/45h.
        if policy_type == TYPE_MULTISIG and script_type == P2SH:
            return P2SH_DEFAULT_DERIVATION

        derivation_path = "m/"

        # Add the purpose type to the derivation path in accordance with
        # the specified BIP (45, 48, or 84)
        if policy_type == TYPE_SINGLESIG:
            derivation_path += str(SINGLESIG_SCRIPT_PURPOSE[script_type])
        elif policy_type == TYPE_MULTISIG:
            derivation_path += str(MULTISIG_SCRIPT_PURPOSE[script_type])
        elif policy_type == TYPE_MINISCRIPT:
            # For now, miniscript is the same as multisig
            derivation_path += str(MINISCRIPT_PURPOSE)

        # The first derivation node is always hardened
        derivation_path += "h/"

        # If another we're using BIP48 or BIP84,
        # we use the zeroth (for mainnet) or first (for testnet)
        # derivation node as the coin type (hardened) as well
        # the account index (hardened)
        derivation_path += "0h" if network == NETWORKS[MAIN_TXT] else "1h"
        derivation_path += "/" + str(account) + "h"

        # As stated in the BIP48, the script type is
        # 1h for P2SH_P2WSH and 2h for P2WSH
        if policy_type is TYPE_MULTISIG and script_type == P2SH_P2WSH:
            derivation_path += "/1h"
        elif policy_type is TYPE_MULTISIG and script_type == P2WSH:
            derivation_path += "/2h"
        elif policy_type is TYPE_MINISCRIPT:
            derivation_path += "/2h"
        return derivation_path

    def _derivation_path(self, derivation):
        """Derivation path input"""
        while True:
            derivation = self.capture_from_keypad(
                t("Derivation Path"),
                [DERIVATION_KEYPAD],
                starting_buffer=(str(derivation) if derivation is not None else ""),
                delete_key_fn=lambda x: x[:-1] if len(x) > 2 else x,
            )
            if derivation == ESC_KEY:
                return None
            nodes = derivation.split("/")[1:]

            # Check node numbers are valid
            valid_nodes = True
            for node in nodes:
                if not node:
                    valid_nodes = False
                    break
                try:
                    if node[-1] == "h":
                        node = node[:-1]
                    if not 0 <= int(node) < HARDENED_INDEX:
                        raise ValueError
                except ValueError:
                    valid_nodes = False
                    break
            if not valid_nodes:
                self.flash_error(
                    t("Invalid derivation path"),
                )
                continue

            # Check if all nodes are hardened
            # except for BIP45 non-hardened cosigner index
            not_hardened_txt = ""
            for i, node in enumerate(nodes):
                if node[-1] != "h" and not derivation.startswith("m/45h"):
                    not_hardened_txt += "Node {}: {}\n".format(i, node)
            if not_hardened_txt:
                self.ctx.display.clear()
                if not self.prompt(
                    t("Some nodes are not hardened:")
                    + "\n\n"
                    + not_hardened_txt
                    + "\n"
                    + t("Proceed?"),
                    self.ctx.display.height() // 2,
                    highlight_prefix=":",
                ):
                    # Allow user to edit the derivation path
                    continue
            return derivation
