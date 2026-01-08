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

import sys
from embit.networks import NETWORKS
from . import (
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
    LETTERS,
    EXTRA_MNEMONIC_LENGTH_FLAG,
)
from .mnemonic_loader import MnemonicLoader
from ..display import DEFAULT_PADDING, FONT_HEIGHT, BOTTOM_PROMPT_LINE
from ..krux_settings import Settings
from ..key import (
    Key,
    P2WPKH,
    P2WSH,
    P2SH,
    SINGLESIG_SCRIPT_MAP,
    MULTISIG_SCRIPT_MAP,
    MINISCRIPT_SCRIPT_MAP,
    TYPE_SINGLESIG,
    TYPE_MULTISIG,
    TYPE_MINISCRIPT,
    POLICY_TYPE_IDS,
    NAME_MULTISIG,
)
from ..krux_settings import t
from ..kboard import kboard


DIGITS_HEX = "0123456789ABCDEF"
DIGITS_OCT = "01234567"

DOUBLE_MNEMONICS_MAX_TRIES = 200
MASK256 = (1 << 256) - 1
MASK128 = (1 << 128) - 1


class Login(MnemonicLoader):
    """Represents the login page of the app"""

    # Used on boot.py when changing the locale on Settings
    SETTINGS_MENU_INDEX = 2

    def __init__(self, ctx):
        login_menu_items = [
            (t("Load Mnemonic"), self.load_key),
            (
                t("New Mnemonic"),
                (self.new_key if not Settings().security.hide_mnemonic else None),
            ),
            (t("Settings"), self.settings),
            (t("Tools"), self.tools),
            (t("About"), self.about),
        ]
        if ctx.power_manager is not None:
            kboard.has_battery = ctx.power_manager.has_battery()
        if kboard.has_battery:
            login_menu_items.append((t("Shutdown"), self.shutdown))

        super().__init__(
            ctx,
            Menu(
                ctx,
                login_menu_items,
                back_label=None,
            ),
        )

    def new_key(self):
        """Handler for the 'new mnemonic' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("Via Camera"), self.new_key_from_snapshot),
                (t("Via Words"), lambda: self.load_key_from_text(new=True)),
                (t("Via D6"), self.new_key_from_dice),
                (t("Via D20"), lambda: self.new_key_from_dice(True)),
            ],
        )
        index, status = submenu.run_loop()
        if index == submenu.back_index:
            return MENU_CONTINUE
        return status

    def new_key_from_dice(self, d_20=False):
        """Handler for both 'new mnemonic'>'via D6/D20' menu items. Default is D6"""
        from .new_mnemonic.dice_rolls import DiceEntropy

        dice_entropy = DiceEntropy(self.ctx, d_20)
        captured_entropy = dice_entropy.new_key()
        if captured_entropy is not None:
            from embit.bip39 import mnemonic_from_bytes

            words = mnemonic_from_bytes(captured_entropy).split()
            return self._load_key_from_words(words, new=True)
        return MENU_CONTINUE

    def new_key_from_snapshot(self):
        """Use camera's entropy to create a new mnemonic"""
        extra_option = t("Double mnemonic")
        len_mnemonic = self.choose_len_mnemonic(extra_option)
        if not len_mnemonic:
            return MENU_CONTINUE

        self.ctx.display.draw_hcentered_text(
            t("Use camera's entropy to create a new mnemonic")
            + ". "
            + t("(Experimental)")
        )
        if self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
            from .capture_entropy import CameraEntropy

            camera_entropy = CameraEntropy(self.ctx)
            entropy_bytes = camera_entropy.capture()
            if entropy_bytes is not None:
                import binascii
                from embit.bip39 import mnemonic_from_bytes
                from ..bip39 import entropy_checksum

                entropy_hash = binascii.hexlify(entropy_bytes).decode()
                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(
                    t("SHA256 of snapshot:") + "\n\n%s" % entropy_hash,
                    highlight_prefix=":",
                )
                self.ctx.input.wait_for_button()

                # Checks if user wants to create a double mnemonic
                if len_mnemonic == EXTRA_MNEMONIC_LENGTH_FLAG:
                    # import time  # Debug
                    # pre_t = time.ticks_ms()  # Debug

                    # split the mnemonic into two parts
                    first_12_entropy = entropy_bytes[:16]
                    second_12_entropy = entropy_bytes[16:32]

                    # calculate the checksum for the first 12 words
                    checksum1 = entropy_checksum(first_12_entropy, 4)
                    # print first 12 words

                    # replace checksum1 as first 4 bits of second 12 words
                    snd_12_array = bytearray(second_12_entropy)
                    snd_12_array[0] = (snd_12_array[0] & 0x0F) | (
                        (checksum1 & 0x0F) << 4
                    )
                    second_12_entropy = bytes(snd_12_array)
                    # reassemble the 256 bits entropy that has first 12 words with valid checksum
                    entropy_bytes = first_12_entropy + second_12_entropy

                    # Increment 1 to full 24 words entropy until
                    # both last 12 words and all 24 have valid checksum
                    tries = 0
                    entropy_int = int.from_bytes(entropy_bytes, "big")
                    while True:
                        # calculate the checksum for the new 24 words
                        ck_sum_24 = entropy_checksum(entropy_bytes, 8)

                        # Extract the lower 128 bits from the integer.
                        snd_12_int = entropy_int & MASK128
                        # Shift and combine with first 4 bits of the 24 wwords checksum
                        shifted_entr = ((snd_12_int << 4) & MASK128) | (ck_sum_24 >> 4)
                        shifted_entropy_bytes = shifted_entr.to_bytes(16, "big")
                        checksum_l_12 = entropy_checksum(shifted_entropy_bytes, 4)
                        # check if checksum_l_12 is equal to the last 4 bits of the
                        # checksum of the full 24 words
                        if checksum_l_12 == (ck_sum_24 & 0x0F):
                            break

                        # Increment the integer value and mask to 256 bits.
                        entropy_int = (entropy_int + 1) & MASK256
                        entropy_bytes = entropy_int.to_bytes(32, "big")
                        tries += 1
                        if tries > DOUBLE_MNEMONICS_MAX_TRIES:
                            raise ValueError("Failed to find a valid double mnemonic")
                    # print("Tries: {} / {} ms".format(tries, time.ticks_ms() - pre_t))  # Debug

                num_bytes = 16 if len_mnemonic == 12 else 32
                entropy_mnemonic = mnemonic_from_bytes(entropy_bytes[:num_bytes])
                return self._load_key_from_words(entropy_mnemonic.split(), new=True)
        return MENU_CONTINUE

    def _load_key_from_words(self, words, charset=LETTERS, new=False):
        mnemonic = " ".join(words)

        # Don't show word list confirmation or the mnemonic editor if hide mnemonic is enabled
        if not Settings().security.hide_mnemonic:
            if charset != LETTERS:
                if self._confirm_key_from_digits(mnemonic, charset) is not None:
                    return MENU_CONTINUE

            from .mnemonic_editor import MnemonicEditor

            mnemonic = MnemonicEditor(self.ctx, mnemonic, new).edit()
        if mnemonic is None:
            return MENU_CONTINUE

        return self._load_wallet_key(mnemonic)

    def _load_wallet_key(self, mnemonic):
        passphrase = ""
        if not hasattr(Settings().wallet, "policy_type") and hasattr(
            Settings().wallet, "multisig"
        ):
            # Retro compatibility with old settings - Multisig (false or true)
            if Settings().wallet.multisig:
                Settings().wallet.policy_type = NAME_MULTISIG

        # New settings - Policy type (single-sig, multisig, miniscript)
        policy_type = POLICY_TYPE_IDS.get(Settings().wallet.policy_type, TYPE_SINGLESIG)
        network = NETWORKS[Settings().wallet.network]
        account = 0

        # If single-sig, by default we use p2wpkh
        # but respect the script type setting
        # in default wallet settings
        if policy_type == TYPE_SINGLESIG:
            script_type = SINGLESIG_SCRIPT_MAP.get(
                Settings().wallet.script_type, P2WPKH
            )

        # If multi-sig, by default we use p2wsh
        # but respect the script type setting
        # in default wallet settings, but if we're
        # using P2SH, we don't use, by default,
        # an account (m/45')
        if policy_type == TYPE_MULTISIG:
            script_type = MULTISIG_SCRIPT_MAP.get(Settings().wallet.script_type, P2WSH)
            if script_type == P2SH:
                account = None

        # If miniscript, by default we use p2wsh
        # but respect the script type setting
        # in default wallet settings
        if policy_type == TYPE_MINISCRIPT:
            script_type = MINISCRIPT_SCRIPT_MAP.get(
                Settings().wallet.script_type, P2WSH
            )

        derivation_path = ""

        from ..wallet import Wallet
        from ..themes import theme
        from .utils import Utils

        utils = Utils(self.ctx)
        while True:
            key = Key(
                mnemonic,
                policy_type,
                network,
                passphrase,
                account,
                script_type,
                derivation_path,
            )
            network_name = network["name"]
            if not derivation_path:
                derivation_path = key.derivation

            wallet_info = "\n" + utils.generate_wallet_info(
                network_name, policy_type, script_type, derivation_path, True
            )
            wallet_info += "\n" + (
                t("No Passphrase")
                if not passphrase
                else t("Passphrase") + " (%d): *…*" % len(passphrase)
            )

            self.ctx.display.clear()
            submenu = Menu(
                self.ctx,
                [
                    (t("Load Wallet"), lambda: None),
                    (t("Passphrase"), lambda: None),
                    (t("Customize"), lambda: None),
                ],
                offset=(
                    self.ctx.display.draw_hcentered_text(wallet_info, info_box=True)
                    * FONT_HEIGHT
                    + DEFAULT_PADDING
                ),
            )

            # draw fingerprint with highlight color
            self.ctx.display.draw_hcentered_text(
                key.fingerprint_hex_str(True),
                color=theme.highlight_color,
                bg_color=theme.info_bg_color,
            )

            # draw network with highlight color
            self.ctx.display.draw_hcentered_text(
                network_name,
                DEFAULT_PADDING + FONT_HEIGHT,
                color=Utils.get_network_color(network_name),
                bg_color=theme.info_bg_color,
            )

            index, _ = submenu.run_loop()
            if index == submenu.back_index:
                if self.prompt(t("Are you sure?"), self.ctx.display.height() // 2):
                    del key
                    return MENU_CONTINUE
            if index == 0:
                break
            if index == 1:
                from .wallet_settings import PassphraseEditor

                passphrase_editor = PassphraseEditor(self.ctx)
                temp_passphrase = passphrase_editor.load_passphrase_menu(mnemonic)
                if temp_passphrase is not None:
                    passphrase = temp_passphrase
            elif index == 2:
                from .wallet_settings import WalletSettings

                wallet_settings = WalletSettings(self.ctx)
                network, policy_type, script_type, account, derivation_path = (
                    wallet_settings.customize_wallet(key)
                )

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Loading…"))

        self.ctx.wallet = Wallet(key)
        return MENU_EXIT

    def tools(self):
        """Handler for the 'Tools' menu item"""
        from .tools import Tools

        while True:
            if Tools(self.ctx).run() == MENU_EXIT:
                break

        # Unimport tools
        sys.modules.pop("krux.pages.tools")
        del sys.modules["krux.pages"].tools

        return MENU_CONTINUE

    def settings(self):
        """Handler for the 'settings' menu item"""
        from .settings_page import SettingsPage

        settings_page = SettingsPage(self.ctx)
        return settings_page.settings()

    def about(self):
        """Handler for the 'about' menu item"""

        import board
        from ..metadata import VERSION
        from ..qr import FORMAT_NONE

        title = "selfcustody.github.io/krux"
        msg = (
            title
            + "\n"
            + t("Hardware")
            + ": %s\n" % board.config["type"]
            + t("Version")
            + ": %s" % VERSION
        )
        offset_x = 0
        width = 0
        if kboard.is_cube:
            offset_x = self.ctx.display.width() // 4
            width = self.ctx.display.width() // 2
        self.display_qr_codes(
            title,
            FORMAT_NONE,
            msg,
            offset_x=offset_x,
            width=width,
            highlight_prefix=":",
        )
        return MENU_CONTINUE
