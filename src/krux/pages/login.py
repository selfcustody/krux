# The MIT License (MIT)

# pylint: disable=C0103,C0116,C0206,C0302,E0601,R0912,R0914,W0212,W0612,W0613

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
    P2WSH,
    P2TR,
    SCRIPT_LONG_NAMES,
    TYPE_SINGLESIG,
    TYPE_MULTISIG,
    TYPE_MINISCRIPT,
    POLICY_TYPE_IDS,
)
from ..krux_settings import t
from ..settings import NAME_SINGLE_SIG, NAME_MULTISIG, NAME_MINISCRIPT


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
        shtn_reboot_label = (
            t("Shutdown") if ctx.power_manager.has_battery() else t("Reboot")
        )
        super().__init__(
            ctx,
            Menu(
                ctx,
                [
                    (t("Load Mnemonic"), self.load_key),
                    (
                        t("New Mnemonic"),
                        (
                            self.new_key
                            if not Settings().security.hide_mnemonic
                            else None
                        ),
                    ),
                    (t("Settings"), self.settings),
                    (t("Tools"), self.tools),
                    (t("About"), self.about),
                    (shtn_reboot_label, self.shutdown),
                ],
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
        if index == len(submenu.menu) - 1:
            return MENU_CONTINUE
        return status

    def load_key_from_camera(self):
        """Handler for the 'load mnemonic'>'via camera' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("QR Code"), self.load_key_from_qr_code),
                ("Tiny Seed", lambda: self.load_key_from_tiny_seed_image("Tiny Seed")),
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
        if index == len(submenu.menu) - 1:
            return MENU_CONTINUE
        return status

    def load_key_from_manual_input(self):
        """Handler for the 'load mnemonic'>'via manual input' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("Words"), self.load_key_from_text),
                (t("Word Numbers"), self.pre_load_key_from_digits),
                ("Tiny Seed (Bits)", self.load_key_from_tiny_seed),
                ("Stackbit 1248", self.load_key_from_1248),
            ],
        )
        index, status = submenu.run_loop()
        if index == len(submenu.menu) - 1:
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
        if index == len(submenu.menu) - 1:
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

        if charset != LETTERS:
            if self._confirm_key_from_digits(mnemonic, charset) is not None:
                return MENU_CONTINUE

        # If the mnemonic is not hidden, show the mnemonic editor
        if not Settings().security.hide_mnemonic:
            from .mnemonic_editor import MnemonicEditor

            mnemonic = MnemonicEditor(self.ctx, mnemonic, new).edit()
        if mnemonic is None:
            return MENU_CONTINUE
        self.ctx.display.clear()

        passphrase = ""
        if not hasattr(Settings().wallet, "policy_type") and hasattr(
            Settings().wallet, "multisig"
        ):
            # Retro compatibility with old settings - Multisig (false or true)
            if Settings().wallet.multisig:
                Settings().wallet.policy_type = TYPE_MULTISIG
        else:
            # New settings - Policy type (single-sig, multisig, miniscript)
            policy_type = POLICY_TYPE_IDS.get(
                Settings().wallet.policy_type, TYPE_SINGLESIG
            )
        network = NETWORKS[Settings().wallet.network]
        account = 0
        if policy_type == TYPE_SINGLESIG:
            script_type = SCRIPT_LONG_NAMES.get(Settings().wallet.script_type)
        elif policy_type == TYPE_MINISCRIPT and Settings().wallet.script_type == P2TR:
            script_type = P2TR
        else:
            script_type = P2WSH
        derivation_path = ""
        from ..wallet import Wallet
        from ..themes import theme

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
            if not derivation_path:
                derivation_path = key.derivation
            wallet_info = "\n"
            wallet_info += network["name"] + "\n"
            if policy_type == TYPE_SINGLESIG:
                wallet_info += NAME_SINGLE_SIG + "\n"
            elif policy_type == TYPE_MULTISIG:
                wallet_info += NAME_MULTISIG + "\n"
            elif policy_type == TYPE_MINISCRIPT:
                if script_type == P2TR:
                    wallet_info += "TR "
                wallet_info += NAME_MINISCRIPT + "\n"
            wallet_info += key.derivation_str(True) + "\n"
            wallet_info += (
                t("No Passphrase") if not passphrase else t("Passphrase") + ": *..*"
            )

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
            index, _ = submenu.run_loop()
            if index == len(submenu.menu) - 1:
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
        self.ctx.display.draw_centered_text(t("Loading.."))

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
            numbers_str,
            suffix_dict[charset],
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
                self.ctx.display.draw_centered_text(t("Processing.."))
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
        except:
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
        if index == len(submenu.menu) - 1:
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
        """Menu handler to manually load key from Tiny Seed sheet metal storage method"""
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

    def load_key_from_tiny_seed_image(self, grid_type="Tiny Seed"):
        """Menu handler to scan key from Tiny Seed sheet metal storage method"""
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
        from ..kboard import kboard
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

        ### on-device testing hack
        # pylint: disable=W0105
        """
        from krux.baseconv import base_encode

        msg = "running test_multi_wrapped_envelopes()..."
        print("\n" + msg)
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(msg)
        matryoshka, matryoshka2, matryoshka3 = test_multi_wrapped_envelopes(None)
        self.display_qr_codes(matryoshka, 1, "binary Matryoshka: k=abc")
        self.display_qr_codes(
            base_encode(matryoshka2, 43), 1, "base43 Matryoshka (doc-ID): k=abc"
        )
        self.display_qr_codes(
            base_encode(matryoshka3, 32),
            1,
            "base32 Matryoshka (deflated doc-ID): k=abc",
        )

        msg = "running report_rate_of_failure()..."
        print("\n" + msg)
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text("See console; " + msg)
        msg = test_report_rate_of_failure(None)
        self.ctx.display.draw_centered_text(msg)
        self.ctx.input.wait_for_button()

        msg = "running brute_force_compression_checks()..."
        print("\n" + msg)
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text("See console; " + msg)
        msg = test_brute_force_compression_checks(None)
        self.ctx.display.draw_centered_text(msg)
        self.ctx.input.wait_for_button()

        msg = "running assert_hashing()..."
        print("\n" + msg)
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text("See console; " + msg)
        msg = test_assert_hashing(None)
        self.ctx.display.draw_centered_text(msg)
        self.ctx.input.wait_for_button()
        """

        return MENU_CONTINUE


def test_multi_wrapped_envelopes(m5stickv):
    """Test that nothing breaks when KEF messages are used to hide other KEF messages"""

    from krux import kef
    from krux.wdt import wdt
    from hashlib import sha256
    from binascii import hexlify

    I_VECTOR = b"OR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e"
    key = "abc"
    iterations, i_step = 10000, 1234
    orig_plaintext = "KEF my dear, you can call me Matryoshka. ;)".encode()

    # encrypt plaintext for versions of KEF
    plaintext = orig_plaintext
    plaintext2 = orig_plaintext
    plaintext3 = orig_plaintext
    for v, version in sorted(kef.VERSIONS.items()):
        if version is None or version["mode"] is None:
            continue

        wdt.feed()
        label = '"{}", K={}'.format(version["name"][4:], key)
        # id can be simple, or up to 255 chars, even non-ascii bytes
        id_ = 'k: "abc"'
        id2 = kef_self_document(v, label=label, iterations=iterations, limit=252)
        id3 = kef._deflate(id2.encode())
        cipher = kef.Cipher(key, id_, iterations)
        cipher2 = kef.Cipher(key, id2, iterations)
        cipher3 = kef.Cipher(key, id3, iterations)
        iv = I_VECTOR[: kef.MODE_IVS.get(version["mode"], 0)]
        cipher_payload = cipher.encrypt(plaintext, v, iv)
        cipher_payload2 = cipher2.encrypt(plaintext2, v, iv)
        cipher_payload3 = cipher3.encrypt(plaintext3, v, iv)
        plaintext = kef.wrap(id_, v, iterations, cipher_payload)
        plaintext2 = kef.wrap(id2, v, iterations, cipher_payload2)
        plaintext3 = kef.wrap(id3, v, iterations, cipher_payload3)
        assert plaintext[:-1] != b"\x00"
        assert plaintext2[:-1] != b"\x00"
        assert plaintext3[:-1] != b"\x00"
        iterations += i_step

    print(
        "\nI'm the sample Matryoshka.",
        repr(plaintext),
        "\nsha256:" + hexlify(sha256(plaintext).digest()).decode(),
    )
    print(
        "\nI'm a Matryoshka with self-doc ID.",
        repr(plaintext2),
        "\nsha256:" + hexlify(sha256(plaintext2).digest()).decode(),
    )
    print(
        "\nI'm a Matryoshka w/ compressed self-doc ID `deflate(ID, wbits=-10)`.",
        repr(plaintext3),
        "\nsha256:" + hexlify(sha256(plaintext3).digest()).decode(),
    )
    answer = plaintext, plaintext2, plaintext3

    # decode and decrypt KEF packages until we find something that's not KEF
    while True:
        wdt.feed()
        try:
            parsed = kef.unwrap(plaintext)
            parsed2 = kef.unwrap(plaintext2)
            parsed3 = kef.unwrap(plaintext3)
            id_, v, iterations, cipher_payload = parsed
            id2, v2, iterations2, cipher_payload2 = parsed2
            id3, v3, iterations3, cipher_payload3 = parsed3
            assert v == v2 == v3
            assert iterations == iterations2 == iterations3
            assert id2 == kef._reinflate(id3)
            # print("\n" + id_)
        except:
            break
        cipher = kef.Cipher(key, id_, iterations)
        cipher2 = kef.Cipher(key, id2, iterations)
        cipher3 = kef.Cipher(key, id3, iterations)
        plaintext = cipher.decrypt(cipher_payload, v)
        plaintext2 = cipher2.decrypt(cipher_payload2, v)
        plaintext3 = cipher3.decrypt(cipher_payload3, v)

    assert plaintext == orig_plaintext
    assert plaintext2 == orig_plaintext
    assert plaintext3 == orig_plaintext

    return answer


def test_report_rate_of_failure(m5stickv):
    from krux import kef
    from hashlib import sha512
    from embit.bip39 import mnemonic_from_bytes
    from krux.wdt import wdt

    I_VECTOR = b"OR\xa1\x93l>2q \x9e\x9dd\x05\x9e\xd7\x8e"

    encrs = {}
    errs = {}
    for v in kef.VERSIONS:
        if kef.VERSIONS[v] is None or kef.VERSIONS[v]["mode"] is None:
            continue

        name = kef.VERSIONS[v]["name"]
        iv = I_VECTOR[: kef.MODE_IVS.get(kef.VERSIONS[v]["mode"], 0)]
        e = kef.Cipher(b"key", b"salt", 10000)
        encrs[v] = {
            "name": name,
            "iv": iv,
            "e": e,
            "timid": 0,
            "avoided": 0,
            "failed": 0,
            "wrapper": 0,
            "sampled": 0,
        }
        errs[v] = {
            "encrypt": {},
            "wrapper": {},
            "decrypt": {},
        }

    # plaintext: will be deterministically altered for each loop
    plain = b""  # play here

    # samples per message type: *1 per message function below, *2 for re-encoding utf8
    # (256 is enough, 1K takes 9 seconds, 100K takes 12 minutes)
    samples = 256  # play here

    # message functions: takes message bytes, returns new same-size message bytes
    def f_16bytes(msg):
        return msg[:16]

    def f_32bytes(msg):
        return msg[:32]

    def f_12w_mnemonic(msg):
        return mnemonic_from_bytes(f_16bytes(msg[:16])).encode()

    def f_24w_mnemonic(msg):
        return mnemonic_from_bytes(f_32bytes(msg[:32])).encode()

    def f_repeated(msg):
        return msg[:16] * 2

    def f_medium(msg):
        return msg

    def f_long(msg):
        return b"".join(
            [
                f_16bytes(msg),
                f_32bytes(msg),
                f_12w_mnemonic(msg),
                f_24w_mnemonic(msg),
                f_repeated(msg),
                f_medium(msg),
            ]
        )

    msg_funcs = (
        f_16bytes,
        f_32bytes,
        f_12w_mnemonic,
        f_24w_mnemonic,
        f_repeated,
        f_medium,
        f_long,
    )

    def utf8_encoded(msg):
        # decoding latin-1 maintains byte-length; re-encoding to utf8 likely adds bytes
        # return msg.decode("latin-1").encode("utf8")
        return bytes(msg)

    failures = 0
    for i in range(samples):
        # rehash plain, make another for each message function, again for utf8 re-encoding
        plain = sha512(plain).digest()
        plaintexts = [msgfunc(plain) for msgfunc in msg_funcs]
        plaintexts.extend([utf8_encoded(msgfunc(plain)) for msgfunc in msg_funcs])
        for plain in plaintexts:
            for v in kef.VERSIONS:
                wdt.feed()

                if kef.VERSIONS[v] is None or kef.VERSIONS[v]["mode"] is None:
                    continue

                avoided = False
                failed = False
                kef_failed = False
                try:
                    cipher = encrs[v]["e"].encrypt(plain, v, encrs[v]["iv"])
                except Exception as err:
                    avoided = True
                    cipher = encrs[v]["e"].encrypt(
                        plain, v, encrs[v]["iv"], fail_unsafe=False
                    )
                    if repr(err) in errs[v]["encrypt"]:
                        errs[v]["encrypt"][repr(err)] += 1
                    else:
                        errs[v]["encrypt"][repr(err)] = 1

                try:
                    envelope = kef.wrap(b"salt", v, 10000, cipher)
                    assert kef.unwrap(envelope)[3] == cipher
                except Exception as err:
                    kef_failed = True
                    if repr(err) in errs[v]["wrapper"]:
                        errs[v]["wrapper"][repr(err)] += 1
                    else:
                        errs[v]["wrapper"][repr(err)] = 1

                try:
                    assert plain == encrs[v]["e"].decrypt(cipher, v)
                except Exception as err:
                    failed = True
                    if avoided:
                        err = "Decryption has failed but encryption was avoided"
                    if repr(err) in errs[v]["decrypt"]:
                        errs[v]["decrypt"][repr(err)] += 1
                    else:
                        errs[v]["decrypt"][repr(err)] = 1

                if not failed and avoided:
                    encrs[v]["timid"] += 1
                if failed and avoided:
                    encrs[v]["avoided"] += 1
                if failed and not avoided:
                    encrs[v]["failed"] += 1
                    failures += 1
                    print(
                        "Failure to decrypt: v: {}, plain: {}, cipher: {}".format(
                            v, plain, cipher
                        )
                    )
                if kef_failed:
                    failures += 1
                    print(
                        "KEF wrapping failure: v: {}, plain: {}, cipher: {}".format(
                            v, plain, cipher
                        )
                    )

                encrs[v]["sampled"] += 1

    print("Failure Summary:\nVer  Ver Name     Timid   Avoid    Fail  KEFerr   Samples")
    for v in sorted(kef.VERSIONS):
        if kef.VERSIONS[v] is None or kef.VERSIONS[v]["mode"] is None:
            continue

        print(
            " {:2d}  {:10s}  {:6d}  {:6d}  {:6d}  {:6d}  {:8d}".format(
                v,
                encrs[v]["name"],
                encrs[v]["timid"],  # able to decrypt, but refused to encrypt
                encrs[v]["avoided"],  # couldn't decrypt and refused to encrypt
                encrs[v]["failed"],  # failed to decrypt w/o refusing to encrypt
                encrs[v]["wrapper"],  # failure during KEF wrapping
                encrs[v]["sampled"],  # total samples
            )
        )

    print("\nPer-Version Failure Details:\nVer  Function    Count  Description")
    for v in sorted(kef.VERSIONS):
        if kef.VERSIONS[v] is None or kef.VERSIONS[v]["mode"] is None:
            continue

        for func in ("encrypt", "decrypt", "wrapper"):
            for error, count in errs[v][func].items():
                print(" {:2d}  {:10s} {:6d}  {}".format(v, func, count, error))

    assert failures == 0
    return "Fail summary: {} failures".format(failures)


def kef_self_document(version, label=None, iterations=None, limit=None):
    """This is NOT a unit-test, it's a way for KEF encoding to document itself"""

    from krux import kef
    from collections import OrderedDict

    def join_text(a_dict, limit):
        result = "\n".join(["{}: {}".format(k, v) for k, v in a_dict.items()])
        if not limit or len(result) <= limit:
            return result

        result = result.replace(" + ", " +")
        if len(result) <= limit:
            return result

        result = result.replace(" +", "+")
        if len(result) <= limit:
            return result

        result = result.replace(" ", "")
        if len(result) <= limit:
            return result

        return result[: limit - 3] + "..."

    # rules are declared as VERSIONS values
    v_name = kef.VERSIONS[version]["name"]
    v_mode = kef.VERSIONS[version]["mode"]
    mode_name = [k for k, v in kef.MODE_NUMBERS.items() if v == v_mode][0]
    v_iv = kef.MODE_IVS.get(v_mode, 0)
    v_auth = kef.VERSIONS[version].get("auth", 0)
    v_pkcs = kef.VERSIONS[version].get("pkcs_pad", False)
    v_compress = kef.VERSIONS[version].get("compress", False)

    label_key = "KEF bytes"
    if label:
        label_key = "[{}] KEF bytes".format(label)

    itertext = " big; =(i > 10K) ? i : i * 10K"
    if iterations:
        itertext = "; ={}".format(iterations)

    text = OrderedDict()
    text[label_key] = "len_id + id + v + i + cpl"
    text["len_id"] = "1b"
    text["id"] = "<len_id>b"
    text["v"] = "1b; ={}".format(version)
    text["i"] = "3b{}".format(itertext)
    text["cpl"] = None

    cpl = "{}"
    if v_iv:
        cpl = "iv + {}".format(cpl)
        iv_arg = ", iv"
        text["iv"] = "{}b".format(v_iv)
    else:
        iv_arg = ""

    if v_compress:
        plain = "zlib(<P>, wbits=-10)"
    else:
        plain = "<P>"

    if mode_name in ("AES-ECB", "AES-CBC", "AES-CTR"):
        if v_auth > 0:
            auth = "sha256({} + k)[:{}]".format(plain, v_auth)
            cpl += " + auth"
            text["e"] = None
            text["pad"] = None
        elif v_auth < 0:
            auth = "sha256({})[:{}]".format(plain, -v_auth)
            plain += " + auth"
            text["e"] = None
            text["auth"] = None
    elif mode_name == "AES-GCM":
        auth = "e.authtag[:{}]".format(v_auth)
        cpl += " + auth"
        text["e"] = None
        text["auth"] = None

    pad = None
    if v_pkcs in (True, False):
        plain += " + pad"
        text["pad"] = None
        pad = "PKCS7" if v_pkcs else "NUL"

    text["cpl"] = cpl.format("e.encrypt({})".format(plain))
    text["e"] = "AES(k, {}{})".format(mode_name[-3:], iv_arg)
    text["auth"] = auth
    if pad:
        text["pad"] = pad
    text["k"] = "pbkdf2_hmac(sha256, <K>, id, i)"

    return join_text(text, limit)


def test_brute_force_compression_checks(m5stickv):
    from hashlib import sha256
    from binascii import hexlify
    from krux.baseconv import base_encode, base_decode
    from krux import kef
    from krux.wdt import wdt

    file_name = "/sd/brute-force.txt"
    file_mode = "r"  # "w": to create file; "r": to read file; None to avoid file I/O
    attempts = 1000  # 1000 good enough for unit-tests, increase for on-device testing
    bstr = b""

    if file_mode:
        if file_mode == "r":
            print("Reading file '{}'...".format(file_name))
            try:
                file_handle = open(file_name, file_mode)
            except:
                file_mode = "w"
                print("  failed to read file {}".format(file_name))

        if file_mode == "w":
            print("Creating file '{}'...".format(file_name))
            try:
                file_handle = open(file_name, file_mode)
            except:
                file_mode = None
                print("  failed to create file {}, skipping file I/O".format(file_name))

    for i in range(attempts):
        wdt.feed()
        bstr = hexlify(sha256(bstr).digest()) * 10
        comp = kef._deflate(bstr)
        sb64 = base_encode(comp, 64)
        assert bstr == kef._reinflate(base_decode(sb64, 64))

        if file_mode == "w":
            file_handle.write(sb64 + "\n")
            continue

        if file_mode != "r":
            continue

        sb64_from_file = file_handle.readline()
        assert bstr == kef._reinflate(base_decode(sb64_from_file, 64))

    if file_mode:
        file_handle.close()

    print(
        "file_mode: {}  Completed {} deflate/reinflate assertions".format(
            file_mode, i + 1
        )
    )
    return "file_mode: {}  Completed {} deflate/reinflate assertions".format(
        file_mode, i + 1
    )


#
# this section inspired by script 'assert_hashing.py' for testing hashlib and uhashlib_hw
#
import hashlib

try:
    import uhashlib_hw

    hw_hashing = True
except:
    hw_hashing = False


def pbkdf2_hmac_sha256(password, salt, iterations):
    """returns hashlib.pbkdf2_hmac() with "sha256" as first parameter"""
    return hashlib.pbkdf2_hmac("sha256", password, salt, iterations)


def assert_hashing(f_hash, f_hmac):
    """churns nonce through sha256() and pbkdf_hmac(sha256,) calls, asserts expected results"""
    #  pylint: disable=C0301
    expecteds = [
        b"\xaaj\xc2\xd4\x96\x18\x82\xf4*4\\v\x15\xf4\x13=\xde\x8emn|\x1bk@\xaeO\xf6\xeeR\xc3\x93\xd0",
        b"\x9e?wG\xe9\rI\xac\xb3\n\xceZt7\xce\xa8\xf6\xe5\xa6\xfe\xa2H\xaa\xf2_\x16Y\xcc\x9a$\xe0\x80",
        b'\xdc\xee\x1fc\xa0\x17\x85\xffda\xd8{\xc91\xd0\xab:\\\x9d@\xec\xc96s\xf0\xc5\xe8"r\x8b\xf1^',
        b'\xdc\xee\x1fc\xa0\x17\x85\xffda\xd8{\xc91\xd0\xab:\\\x9d@\xec\xc96s\xf0\xc5\xe8"r\x8b\xf1^',
        b'\x1fdFbl\x13\xe6\x93\xfb\xd1\x13\xacj\xf5\x9f"<\xf1\xa2@\x168\x04=\x95<`i\xb3\xcc\x7f\x98',
        b"\x1d\x98\xdc\x98\x9f\xda\x91=\xd3\xefC\xc3_\xd4qivyU\x84\x11K\xe5s+\xa8\xbc\x97\x83\x00Y\xd1",
    ]

    hashes = []
    nonce = b""
    for i in range(32):
        nonce = f_hash(nonce).digest()
        hashes.append(nonce)

        nonce = f_hash(nonce[-i:]).digest()
        hashes.append(nonce)

        nonce = f_hash(nonce * (i + 1)).digest()
        hashes.append(nonce)

        nonce = f_hmac(nonce[-i:], nonce[:-i], (i + 1) * 2)  # short password and salt
        hashes.append(nonce)

        nonce = f_hmac(nonce * (i + 1), nonce, (i + 1) * 4)  # long password
        hashes.append(nonce)

        nonce = f_hmac(
            nonce, (nonce * (i + 1))[:1024], (i + 1) * 8
        )  # long salt (clipped at 1024)
        hashes.append(nonce)
    nonce = f_hash(b"".join(hashes)).digest()

    calculateds = [
        hashes[2],  # 3rd churned digest is solely from sha256
        nonce,  # last nonce is sha256 of contatenated hashes from sha256/hmac churns above
        f_hmac(b"".join(hashes), nonce, 16),  # long_password == sha256(long_password)
        f_hmac(f_hash(b"".join(hashes)).digest(), nonce, 16),  # proves above
        f_hmac(nonce, b"".join(hashes)[:1024], 32),  # long_salt is not the same case
        f_hmac(nonce, f_hash(b"".join(hashes)[:1024]).digest(), 32),  # proves above
    ]

    err = ""
    for i, (expected, calculated) in enumerate(zip(expecteds, calculateds)):
        try:
            assert expected == calculated
        except:
            err += "\nTest case: {}\n   expected: {}\n calculated: {}".format(
                i, repr(expected), repr(calculated)
            )
    if err:
        raise AssertionError(err)


def test_assert_hashing(m5stickv):
    """assert sanity of sha256 and pbkdf2_hmac implementations against known results"""

    err = ""
    if hw_hashing:
        try:
            assert_hashing(uhashlib_hw.sha256, uhashlib_hw.pbkdf2_hmac_sha256)
        except Exception as e:
            err += "\n\nFAILED assert_hashing() with uhashlib_hw module" + str(e)

    try:
        assert_hashing(hashlib.sha256, pbkdf2_hmac_sha256)
    except Exception as e:
        err += "\n\nFAILED assert_hashing() with hashlib module" + str(e)

    if err:
        print(err)
        raise AssertionError(err)
    print(
        "test_assert_hashing() passed successfully.  hw_hashing: {}".format(hw_hashing)
    )
    return "test_assert_hashing() passed successfully.  hw_hashing: {}".format(
        hw_hashing
    )
