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
from embit.wordlists.bip39 import WORDLIST
from . import (
    Page,
    Menu,
    DIGITS,
    MENU_CONTINUE,
    MENU_EXIT,
    ESC_KEY,
    LETTERS,
    EXTRA_MNEMONIC_LENGTH_FLAG,
    choose_len_mnemonic,
)
from ..display import DEFAULT_PADDING, FONT_HEIGHT, BOTTOM_PROMPT_LINE
from ..krux_settings import Settings
from ..qr import FORMAT_UR
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


class Login(Page):
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
        if kboard.has_battery:
            login_menu_items.append((t("Shutdown"), ctx.power_manager.shutdown))

        super().__init__(
            ctx,
            Menu(
                ctx,
                login_menu_items,
                back_label=None,
            ),
        )

    def load_key(self):
        """Handler for the 'load mnemonic' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("Via Camera"), self.load_key_from_camera),
                (t("Via Manual Input"), self.load_key_from_manual_input),
                (t("From Storage"), self.load_mnemonic_from_storage),
            ],
        )
        index, status = submenu.run_loop()
        if index == submenu.back_index:
            return MENU_CONTINUE
        return status

    def load_key_from_camera(self):
        """Handler for the 'load mnemonic'>'via camera' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("QR Code"), self.load_key_from_qr_code),
                ("Tinyseed", lambda: self.load_key_from_tiny_seed_image("Tinyseed")),
                (
                    "OneKey KeyTag",
                    lambda: self.load_key_from_tiny_seed_image("OneKey KeyTag"),
                ),
                (
                    t("Binary Grid"),
                    lambda: self.load_key_from_tiny_seed_image("Binary Grid"),
                ),
            ],
        )
        index, status = submenu.run_loop()
        if index == submenu.back_index:
            return MENU_CONTINUE
        return status

    def load_key_from_manual_input(self):
        """Handler for the 'load mnemonic'>'via manual input' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("Words"), self.load_key_from_text),
                (t("Word Numbers"), self.pre_load_key_from_digits),
                ("Tinyseed (Bits)", self.load_key_from_tiny_seed),
                ("Stackbit 1248", self.load_key_from_1248),
            ],
        )
        index, status = submenu.run_loop()
        if index == submenu.back_index:
            return MENU_CONTINUE
        return status

    def load_mnemonic_from_storage(self):
        """Handler to 'load mnemonic'>'from storage"""
        from .encryption_ui import LoadEncryptedMnemonic

        encrypted_mnemonics = LoadEncryptedMnemonic(self.ctx)
        words = encrypted_mnemonics.load_from_storage()
        if words == MENU_CONTINUE:
            return MENU_CONTINUE
        return self._load_key_from_words(words)

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
        len_mnemonic = choose_len_mnemonic(self.ctx, extra_option)
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

    def _confirm_key_from_digits(self, mnemonic, charset):
        from .utils import Utils

        charset_type = {
            DIGITS: Utils.BASE_DEC,
            DIGITS_HEX: Utils.BASE_HEX,
            DIGITS_OCT: Utils.BASE_OCT,
        }
        suffix_dict = {
            DIGITS: Utils.BASE_DEC_SUFFIX,
            DIGITS_HEX: Utils.BASE_HEX_SUFFIX,
            DIGITS_OCT: Utils.BASE_OCT_SUFFIX,
        }
        numbers_str = Utils.get_mnemonic_numbers(mnemonic, charset_type[charset])
        self.display_mnemonic(
            mnemonic,
            suffix_dict[charset],
            numbers_str,
            fingerprint=Key.extract_fingerprint(mnemonic),
        )
        if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
            return MENU_CONTINUE
        self.ctx.display.clear()

        return None

    def _encrypted_qr_code(self, data):
        from ..encryption import EncryptedQRCode
        from ..baseconv import base_decode

        encrypted_qr = EncryptedQRCode()
        public_data = None
        try:  # Try to decode base43 data
            data = base_decode(data, 43)
            public_data = encrypted_qr.public_data(data)
        except:
            pass
        if not public_data:  # Failed to decode and parse base43
            public_data = encrypted_qr.public_data(data)
        if public_data:
            self.ctx.display.clear()
            if self.prompt(
                public_data + "\n\n" + t("Decrypt?"), self.ctx.display.height() // 2
            ):
                from .encryption_ui import EncryptionKey
                from embit.bip39 import mnemonic_from_bytes

                key_capture = EncryptionKey(self.ctx)
                key = key_capture.encryption_key()
                if key in (None, "", ESC_KEY):
                    self.flash_error(t("Key was not provided"))
                    return MENU_CONTINUE
                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(t("Processing…"))
                word_bytes = encrypted_qr.decrypt(key)
                if word_bytes is None:
                    self.flash_error(t("Failed to decrypt"))
                    return MENU_CONTINUE
                return mnemonic_from_bytes(word_bytes).split()
            return MENU_CONTINUE  # prompt NO
        return None

    def auto_complete_qr_words(self, words):
        """Ensure all words are in the wordlist, autocomplete if possible"""
        for i, word in enumerate(words):
            if word not in WORDLIST:
                word_lower = word.lower()
                # Try to autocomplete the word
                auto_complete = False
                for list_word in WORDLIST:
                    if list_word.startswith(word_lower):
                        words[i] = list_word
                        auto_complete = True
                        break
                if not auto_complete:
                    # Mark as invalid and clear the words list to indicate failure
                    return []
        return words

    def load_key_from_qr_code(self):
        """Handler for the 'via qr code' menu item"""
        from .qr_capture import QRCodeCapture
        from .encryption_ui import decrypt_kef

        qr_capture = QRCodeCapture(self.ctx)
        data, qr_format = qr_capture.qr_capture_loop()
        if data is None:
            self.flash_error(t("Failed to load"))
            return MENU_CONTINUE

        try:
            data = decrypt_kef(self.ctx, data)
        except KeyError:
            self.flash_error(t("Failed to decrypt"))
            return MENU_CONTINUE
        except ValueError:
            # ValueError=not KEF or declined to decrypt
            pass

        words = []
        if qr_format == FORMAT_UR:
            from urtypes.crypto.bip39 import BIP39

            words = BIP39.from_cbor(data.cbor).words
        else:
            try:
                data_str = data.decode() if not isinstance(data, str) else data
                words = data_str.split() if " " in data_str else []
                if len(words) in (12, 24):
                    words = self.auto_complete_qr_words(words)
                else:
                    words = []
            except:
                pass

            if not words:
                data_bytes = ""
                try:
                    data_bytes = (
                        data.encode("latin-1") if isinstance(data, str) else data
                    )
                except:
                    try:
                        data_bytes = (
                            data.encode("shift-jis") if isinstance(data, str) else data
                        )
                    except:
                        pass

                # CompactSeedQR format
                if len(data_bytes) in (16, 32):
                    from embit.bip39 import mnemonic_from_bytes

                    words = mnemonic_from_bytes(data_bytes).split()
                # SeedQR format
                elif len(data_bytes) in (48, 96):
                    words = [
                        WORDLIST[int(data_bytes[i : i + 4])]
                        for i in range(0, len(data_bytes), 4)
                    ]

        if not words or (len(words) != 12 and len(words) != 24):
            self.flash_error(t("Invalid mnemonic length"))
            return MENU_CONTINUE
        return self._load_key_from_words(words)

    def _load_key_from_keypad(
        self,
        title,
        charset,
        to_word,
        autocomplete_fn=None,
        possible_keys_fn=None,
        new=False,
        len_mnemonic=None,
    ):
        words = []
        self.ctx.display.draw_hcentered_text(title)
        if self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
            while len(words) < 24:
                if new:
                    if len(words) == len_mnemonic - 1:
                        self.ctx.display.clear()
                        self.ctx.display.draw_centered_text(
                            t(
                                "Leave blank if you'd like Krux to pick a valid final word"
                            )
                        )
                        self.ctx.input.wait_for_button()
                    elif len(words) == len_mnemonic:
                        break
                else:
                    if len(words) == 12:
                        self.ctx.display.clear()
                        if self.prompt(t("Done?"), self.ctx.display.height() // 2):
                            break

                word = ""
                word_num = ""
                while True:
                    word_num = ""

                    # if new and last word, lead input to a valid mnemonic
                    if new and len(words) == len_mnemonic - 1:
                        finalwords = Key.get_final_word_candidates(words)
                        word = self.capture_from_keypad(
                            t("Word %d") % (len(words) + 1),
                            [charset],
                            lambda x: autocomplete_fn(x, finalwords),
                            lambda x: possible_keys_fn(x, finalwords),
                        )
                    else:
                        word = self.capture_from_keypad(
                            t("Word %d") % (len(words) + 1),
                            [charset],
                            autocomplete_fn,
                            possible_keys_fn,
                        )

                    if word == ESC_KEY:
                        return MENU_CONTINUE

                    # If 'new' and the last 'word' is blank,
                    # pick a random final word that is a valid checksum
                    if new and word == "" and len(words) == len_mnemonic - 1:
                        break

                    if to_word is not None:
                        word_num = word
                        word = to_word(word)

                    if word not in WORDLIST:
                        word = ""

                    if word != "":
                        break

                if word not in WORDLIST and word == "":
                    word = Key.pick_final_word(self.ctx.input.entropy, words)

                self.ctx.display.clear()
                if word_num in (word, ""):
                    word_num = ""
                else:
                    word_num += ": "
                if self.prompt(
                    str(len(words) + 1) + ".\n\n" + word_num + word + "\n\n",
                    self.ctx.display.height() // 2,
                    highlight_prefix=":",
                ):
                    words.append(word)

            return self._load_key_from_words(words, charset, new)

        return MENU_CONTINUE

    def load_key_from_text(self, new=False):
        """Handler for both 'new/load mnemonic'>[...]>'via words' menu items"""
        from .mnemonic_editor import MnemonicEditor

        if new:
            len_mnemonic = choose_len_mnemonic(self.ctx)
            if not len_mnemonic:
                return MENU_CONTINUE
            title = t("Enter %d BIP39 words.") % len_mnemonic
        else:
            len_mnemonic = None
            title = t("Enter each word of your BIP39 mnemonic.")

        mnemonic_editor = MnemonicEditor(self.ctx)
        mnemonic_editor.compute_search_ranges()

        return self._load_key_from_keypad(
            title,
            LETTERS,
            None,
            autocomplete_fn=mnemonic_editor.autocomplete,
            possible_keys_fn=mnemonic_editor.possible_letters,
            new=new,
            len_mnemonic=len_mnemonic,
        )

    def pre_load_key_from_digits(self):
        """Handler for the 'load mnemonic'>'via numbers' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("Decimal"), self.load_key_from_digits),
                (t("Hexadecimal"), self.load_key_from_hexadecimal),
                (t("Octal"), self.load_key_from_octal),
            ],
        )
        index, status = submenu.run_loop()
        if index == submenu.back_index:
            return MENU_CONTINUE
        return status

    def load_key_from_octal(self):
        """Handler for the 'load mnemonic'>'via numbers'>'octal' submenu item"""
        title = t(
            "Enter each word of your BIP39 mnemonic as a number in octal from 1 to 4000."
        )

        def autocomplete(prefix):
            # 256 in decimal is 400 in octal
            if len(prefix) == 4 or (len(prefix) == 3 and int(prefix, 8) > 256):
                return prefix
            return None

        def to_word(user_input):
            if user_input:
                word_num = int(user_input, 8)
                if 0 < word_num <= 2048:
                    return WORDLIST[word_num - 1]
            return ""

        def possible_letters(prefix):
            if prefix == "":
                return DIGITS_OCT.replace("0", "")
            if prefix == "400":
                return "0"
            return DIGITS_OCT

        return self._load_key_from_keypad(
            title,
            DIGITS_OCT,
            to_word,
            autocomplete_fn=autocomplete,
            possible_keys_fn=possible_letters,
        )

    def load_key_from_hexadecimal(self):
        """Handler for the 'load mnemonic'>'via numbers'>'hexadecimal' submenu item"""
        title = t(
            "Enter each word of your BIP39 mnemonic as a number in hexadecimal from 1 to 800."
        )

        def autocomplete(prefix):
            # 128 decimal is 0x80
            if len(prefix) == 3 or (len(prefix) == 2 and int(prefix, 16) > 128):
                return prefix
            return None

        def to_word(user_input):
            if user_input:
                word_num = int(user_input, 16)
                if 0 < word_num <= 2048:
                    return WORDLIST[word_num - 1]
            return ""

        def possible_letters(prefix):
            if prefix == "":
                return DIGITS_HEX.replace("0", "")
            if prefix == "80":
                return "0"
            return DIGITS_HEX

        return self._load_key_from_keypad(
            title,
            DIGITS_HEX,
            to_word,
            autocomplete_fn=autocomplete,
            possible_keys_fn=possible_letters,
        )

    def load_key_from_digits(self):
        """Handler for the 'load mnemonic'>'via numbers'>'decimal' submenu item"""
        title = t("Enter each word of your BIP39 mnemonic as a number from 1 to 2048.")

        def autocomplete(prefix):
            if len(prefix) == 4 or (len(prefix) == 3 and int(prefix) > 204):
                return prefix
            return None

        def to_word(user_input):
            if user_input:
                word_num = int(user_input)
                if 0 < word_num <= 2048:
                    return WORDLIST[word_num - 1]
            return ""

        def possible_letters(prefix):
            if prefix == "":
                return DIGITS.replace("0", "")
            if prefix == "204":
                return DIGITS.replace("9", "")
            return DIGITS

        return self._load_key_from_keypad(
            title,
            DIGITS,
            to_word,
            autocomplete_fn=autocomplete,
            possible_keys_fn=possible_letters,
        )

    def load_key_from_1248(self):
        """Menu handler to load key from Stackbit 1248 sheet metal storage method"""
        from .stack_1248 import Stackbit

        stackbit = Stackbit(self.ctx)
        words = stackbit.enter_1248()
        del stackbit
        if words is not None:
            return self._load_key_from_words(words)
        return MENU_CONTINUE

    def load_key_from_tiny_seed(self):
        """Menu handler to manually load key from Tinyseed sheet metal storage method"""
        from .tiny_seed import TinySeed

        len_mnemonic = choose_len_mnemonic(self.ctx)
        if not len_mnemonic:
            return MENU_CONTINUE

        tiny_seed = TinySeed(self.ctx)
        words = tiny_seed.enter_tiny_seed(len_mnemonic == 24)
        del tiny_seed
        if words is not None:
            return self._load_key_from_words(words)
        return MENU_CONTINUE

    def load_key_from_tiny_seed_image(self, grid_type="Tinyseed"):
        """Menu handler to scan key from Tinyseed sheet metal storage method"""
        from .tiny_seed import TinyScanner

        len_mnemonic = choose_len_mnemonic(self.ctx)
        if not len_mnemonic:
            return MENU_CONTINUE

        intro = t("Paint punched dots black so they can be detected.") + " "
        intro += t("Use a black background surface.") + " "
        intro += t("Align camera and backup plate properly.")
        self.ctx.display.draw_hcentered_text(intro)
        if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
            return MENU_CONTINUE

        tiny_scanner = TinyScanner(self.ctx, grid_type)
        words = tiny_scanner.scanner(len_mnemonic == 24)
        del tiny_scanner
        if words is None:
            self.flash_error(t("Failed to load"))
            return MENU_CONTINUE
        return self._load_key_from_words(words)

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
