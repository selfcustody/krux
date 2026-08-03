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

DOUBLE_MNEMONICS_MAX_TRIES = 200
MASK256 = (1 << 256) - 1
MASK128 = (1 << 128) - 1


class Login(MnemonicLoader):
    """Represents the login page of the app"""

    # Used on boot.py when changing the locale on Settings
    SETTINGS_MENU_INDEX = 2
    ENTROPY_SOURCE_CAMERA = 0
    ENTROPY_SOURCE_D6 = 1
    ENTROPY_SOURCE_D20 = 2

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
                (t("Via Camera"), lambda: self.new_key_from_snapshot(True)),
                (t("Via Words"), lambda: self.load_key_from_text(new=True)),
                (t("Via D6"), lambda: self.new_key_from_dice(False, True)),
                (t("Via D20"), lambda: self.new_key_from_dice(True, True)),
            ],
        )
        index, status = submenu.run_loop()
        if index == submenu.back_index:
            return MENU_CONTINUE
        return status

    def _mix_entropy(self, entropy_1, entropy_2):
        """Combine two entropy sources deterministically"""
        import hashlib

        return hashlib.sha256(
            hashlib.sha256(entropy_1).digest() + hashlib.sha256(entropy_2).digest()
        ).digest()

    def _maybe_add_second_entropy(self, entropy_bytes, len_mnemonic, first_source):
        """Optionally collect and mix a second entropy source"""
        import binascii

        if not self.prompt(t("Add a 2nd entropy source?"), BOTTOM_PROMPT_LINE):
            return entropy_bytes

        while True:
            second_source = self._entropy_source_menu(t("2nd entropy source"))
            if second_source is None:
                warning_msg = t("2nd entropy source was not added.")
                warning_msg += "\n\n"
                warning_msg += t("Proceed with a single source?")
                if self.prompt(warning_msg, BOTTOM_PROMPT_LINE):
                    return entropy_bytes
                return None

            if second_source == first_source:
                warning_msg = t("Same source selected.")
                warning_msg += "\n"
                warning_msg += t("Entropy gain may be limited.")
                warning_msg += "\n\n"
                warning_msg += t("Proceed anyway?")
                proceed_same_source = self.prompt(warning_msg, BOTTOM_PROMPT_LINE)
                self.ctx.display.clear()
                if not proceed_same_source:
                    continue
            break

        second_entropy = self._capture_entropy_from_source(second_source, len_mnemonic)
        if second_entropy is None:
            warning_msg = t("2nd entropy capture was cancelled.")
            warning_msg += "\n\n"
            warning_msg += t("Proceed with a single source?")
            if self.prompt(warning_msg, BOTTOM_PROMPT_LINE):
                return entropy_bytes
            return None

        mixed_entropy = self._mix_entropy(entropy_bytes, second_entropy)

        mixed_entropy_hash = binascii.hexlify(mixed_entropy).decode()
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            t("SHA256 of combined entropy:") + "\n\n%s" % mixed_entropy_hash,
            highlight_prefix=":",
        )
        self.ctx.input.wait_for_button()
        return mixed_entropy

    def _entropy_source_menu(self, prompt, excluded=None):
        """Ask user to pick an entropy source, optionally excluding one"""
        options = [
            (self.ENTROPY_SOURCE_CAMERA, t("Via Camera")),
            (self.ENTROPY_SOURCE_D6, t("Via D6")),
            (self.ENTROPY_SOURCE_D20, t("Via D20")),
        ]
        items = [
            (label, (lambda entropy_source=entropy_source: entropy_source))
            for entropy_source, label in options
            if entropy_source != excluded
        ]
        submenu = Menu(self.ctx, items, back_status=lambda: None)
        self.ctx.display.draw_hcentered_text(prompt)
        _, entropy_source = submenu.run_loop()
        self.ctx.display.clear()
        return entropy_source

    def _new_key_from_dice_with_len(self, len_mnemonic, d_20=False):
        """Capture entropy from dice using a pre-selected mnemonic length"""
        from .new_mnemonic.dice_rolls import DiceEntropy

        dice_entropy = DiceEntropy(self.ctx, d_20)
        return dice_entropy.new_key(len_mnemonic)

    def _capture_camera_entropy(self):
        """Use camera entropy source and return its 32-byte digest"""
        self.ctx.display.draw_hcentered_text(
            t("Use camera's entropy to create a new mnemonic")
            + ". "
            + t("(Experimental)")
        )
        if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
            return None

        from .capture_entropy import CameraEntropy
        import binascii

        camera_entropy = CameraEntropy(self.ctx)
        entropy_bytes = camera_entropy.capture()
        if entropy_bytes is None:
            return None

        entropy_hash = binascii.hexlify(entropy_bytes).decode()
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            t("SHA256 of snapshot:") + "\n\n%s" % entropy_hash,
            highlight_prefix=":",
        )
        self.ctx.input.wait_for_button()
        return entropy_bytes

    def _capture_entropy_from_source(self, entropy_source, len_mnemonic):
        """Capture entropy from the selected source"""
        if entropy_source == self.ENTROPY_SOURCE_CAMERA:
            return self._capture_camera_entropy()

        dice_mnemonic_len = (
            24 if len_mnemonic == EXTRA_MNEMONIC_LENGTH_FLAG else len_mnemonic
        )
        return self._new_key_from_dice_with_len(
            dice_mnemonic_len, d_20=(entropy_source == self.ENTROPY_SOURCE_D20)
        )

    def _adjust_double_mnemonic_entropy(self, entropy_bytes):
        """Adjust entropy so both 12w halves and 24w mnemonic checksums are valid"""
        from ..bip39 import entropy_checksum

        first_12_entropy = entropy_bytes[:16]
        second_12_entropy = entropy_bytes[16:32]

        checksum1 = entropy_checksum(first_12_entropy, 4)

        snd_12_array = bytearray(second_12_entropy)
        snd_12_array[0] = (snd_12_array[0] & 0x0F) | ((checksum1 & 0x0F) << 4)
        second_12_entropy = bytes(snd_12_array)

        entropy_bytes = first_12_entropy + second_12_entropy
        tries = 0
        entropy_int = int.from_bytes(entropy_bytes, "big")
        while True:
            ck_sum_24 = entropy_checksum(entropy_bytes, 8)

            snd_12_int = entropy_int & MASK128
            shifted_entr = ((snd_12_int << 4) & MASK128) | (ck_sum_24 >> 4)
            shifted_entropy_bytes = shifted_entr.to_bytes(16, "big")
            checksum_l_12 = entropy_checksum(shifted_entropy_bytes, 4)

            if checksum_l_12 == (ck_sum_24 & 0x0F):
                return entropy_bytes

            entropy_int = (entropy_int + 1) & MASK256
            entropy_bytes = entropy_int.to_bytes(32, "big")
            tries += 1
            if tries > DOUBLE_MNEMONICS_MAX_TRIES:
                raise ValueError("Failed to find a valid double mnemonic")

    def new_key_from_two_entropy_sources(self):
        """Create a new mnemonic by combining two entropy sources"""
        import hashlib
        import binascii
        from embit.bip39 import mnemonic_from_bytes

        len_mnemonic = self.choose_len_mnemonic(t("Double mnemonic"))
        if not len_mnemonic:
            return MENU_CONTINUE

        source_1 = self._entropy_source_menu(t("1st entropy source"))
        if source_1 is None:
            return MENU_CONTINUE

        source_2 = self._entropy_source_menu(t("2nd entropy source"))
        if source_2 is None:
            return MENU_CONTINUE

        entropy_1 = self._capture_entropy_from_source(source_1, len_mnemonic)
        if entropy_1 is None:
            return MENU_CONTINUE

        entropy_2 = self._capture_entropy_from_source(source_2, len_mnemonic)
        if entropy_2 is None:
            return MENU_CONTINUE

        mixed_entropy = hashlib.sha256(
            hashlib.sha256(entropy_1).digest() + hashlib.sha256(entropy_2).digest()
        ).digest()

        mixed_entropy_hash = binascii.hexlify(mixed_entropy).decode()
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            t("SHA256 of combined entropy:") + "\n\n%s" % mixed_entropy_hash,
            highlight_prefix=":",
        )
        self.ctx.input.wait_for_button()

        if len_mnemonic == EXTRA_MNEMONIC_LENGTH_FLAG:
            mixed_entropy = self._adjust_double_mnemonic_entropy(mixed_entropy)

        num_bytes = 16 if len_mnemonic == 12 else 32
        entropy_mnemonic = mnemonic_from_bytes(mixed_entropy[:num_bytes])
        return self._load_key_from_words(entropy_mnemonic.split(), new=True)

    def new_key_from_dice(self, d_20=False, ask_for_second_entropy=False):
        """Handler for both 'new mnemonic'>'via D6/D20' menu items. Default is D6"""
        from .new_mnemonic.dice_rolls import DiceEntropy

        dice_entropy = DiceEntropy(self.ctx, d_20)
        captured_entropy = dice_entropy.new_key()
        if captured_entropy is not None:
            from embit.bip39 import mnemonic_from_bytes

            if ask_for_second_entropy:
                len_mnemonic = 12 if len(captured_entropy) == 16 else 24
                first_source = self.ENTROPY_SOURCE_D20 if d_20 else self.ENTROPY_SOURCE_D6
                captured_entropy = self._maybe_add_second_entropy(
                    captured_entropy,
                    len_mnemonic,
                    first_source,
                )
                if captured_entropy is None:
                    return MENU_CONTINUE

            words = mnemonic_from_bytes(captured_entropy).split()
            return self._load_key_from_words(words, new=True)
        return MENU_CONTINUE

    def new_key_from_snapshot(self, ask_for_second_entropy=False):
        """Use camera's entropy to create a new mnemonic"""
        extra_option = t("Double mnemonic")
        len_mnemonic = self.choose_len_mnemonic(extra_option)
        if not len_mnemonic:
            return MENU_CONTINUE

        entropy_bytes = self._capture_camera_entropy()
        if entropy_bytes is not None:
            from embit.bip39 import mnemonic_from_bytes

            if ask_for_second_entropy:
                entropy_bytes = self._maybe_add_second_entropy(
                    entropy_bytes,
                    len_mnemonic,
                    self.ENTROPY_SOURCE_CAMERA,
                )
                if entropy_bytes is None:
                    return MENU_CONTINUE

            if len_mnemonic == EXTRA_MNEMONIC_LENGTH_FLAG:
                entropy_bytes = self._adjust_double_mnemonic_entropy(entropy_bytes)

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
