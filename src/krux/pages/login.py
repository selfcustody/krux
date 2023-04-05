# The MIT License (MIT)

# Copyright (c) 2021-2022 Krux contributors

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
# pylint: disable=C2801
import binascii
import hashlib
import lcd
from embit.networks import NETWORKS
from embit.wordlists.bip39 import WORDLIST
from embit import bip39
from urtypes.crypto.bip39 import BIP39
from ..metadata import VERSION
from ..settings import (
    CategorySetting,
    NumberSetting,
    DARKGREEN,
    SD_PATH,
    FLASH_PATH,
    Store,
)
from ..krux_settings import Settings, LoggingSettings, BitcoinSettings, TouchSettings
from ..input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_TOUCH
from ..qr import FORMAT_UR, FORMAT_NONE
from ..key import Key
from ..wallet import Wallet
from ..printers import create_printer
from ..krux_settings import t
from .stack_1248 import Stackbit
from .tiny_seed import TinySeed, TinyScanner
from ..sd_card import SDHandler
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
    ESC_KEY,
    DEFAULT_PADDING,
    SD_ROOT_PATH,
    LETTERS,
    UPPERCASE_LETTERS,
    NUM_SPECIAL_1,
    NUM_SPECIAL_2,
)
from ..encryption import StoredSeeds
import os
import uos
import time

SENTINEL_DIGITS = "11111"

D6_STATES = [str(i + 1) for i in range(6)]
D20_STATES = [str(i + 1) for i in range(20)]
DIGITS = "0123456789"
DIGITS_HEX = "0123456789ABCDEF"
DIGITS_OCT = "01234567"

D6_12W_MIN_ROLLS = 50
D6_24W_MIN_ROLLS = 99
D20_12W_MIN_ROLLS = 30
D20_24W_MIN_ROLLS = 60

SD_MSG_TIME = 2500

PASSPHRASE_MAX_LEN = 200

CATEGORY_SETTING_COLOR_DICT = {
    LoggingSettings.ERROR_TXT: lcd.RED,
    LoggingSettings.WARN_TXT: lcd.ORANGE,
    LoggingSettings.INFO_TXT: DARKGREEN,
    LoggingSettings.DEBUG_TXT: lcd.MAGENTA,
    BitcoinSettings.MAIN_TXT: lcd.ORANGE,
    BitcoinSettings.TEST_TXT: lcd.GREEN,
}


class Login(Page):
    """Represents the login page of the app"""

    def __init__(self, ctx):
        super().__init__(
            ctx,
            Menu(
                ctx,
                [
                    (t("Load Mnemonic"), self.load_key),
                    (t("New Mnemonic"), self.new_key),
                    (t("Settings"), self.settings),
                    (t("Tools"), self.tools),
                    (t("About"), self.about),
                    (t("Shutdown"), self.shutdown),
                ],
            ),
        )

    def load_key(self):
        """Handler for the 'load mnemonic' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("Via Camera"), self.load_key_from_camera),
                (t("Via Manual Input"), self.load_key_from_manual_input),
                (t("From Storage"), self.load_key_from_storage),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        index, status = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return MENU_CONTINUE
        return status

    def load_key_from_camera(self):
        """Handler for the 'via camera' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("QR Code"), self.load_key_from_qr_code),
                (
                    t("Tiny Seed"),
                    self.load_key_from_tiny_seed_image,
                ),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        index, status = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return MENU_CONTINUE
        return status

    def load_key_from_manual_input(self):
        """Handler for the 'via manual input' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("Words"), self.load_key_from_text),
                (t("Word Numbers"), self.pre_load_key_from_digits),
                (t("Tiny Seed (Bits)"), self.load_key_from_tiny_seed),
                (t("Stackbit 1248"), self.load_key_from_1248),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        index, status = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return MENU_CONTINUE
        return status

    def load_encrypted_seed(self, seed_id, sd_card=False):
        """Load a selected seed from the encrypted file"""
        key = self.capture_from_keypad(
            t("Encryption Key"),
            [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2],
        )
        if key in ("", ESC_KEY):
            raise ValueError("Decryption Failed")
        stored_seeds = StoredSeeds()
        try:
            words = stored_seeds.decrypt(key, seed_id, sd_card).split()
        except:
            raise ValueError("Decryption Failed")

        if len(words) not in (12, 24):
            raise ValueError("Decryption failed")
        del stored_seeds
        return self._load_key_from_words(words)

    def load_key_from_storage(self):
        """Lists all encrypted seeds stored on a file"""
        seed_ids_menu = []
        stored_seeds = StoredSeeds()
        for seed_id in stored_seeds.list_seeds():
            seed_ids_menu.append(
                (
                    seed_id + "(flash)",
                    lambda s_id=seed_id: self.load_encrypted_seed(s_id),
                )
            )
        if stored_seeds.has_sd_card:
            for seed_id in stored_seeds.list_seeds(sd_card=True):
                seed_ids_menu.append(
                    (
                        seed_id + "(SD card)",
                        lambda s_id=seed_id: self.load_encrypted_seed(s_id, sd_card=True),
                    )
            )
        del stored_seeds
        seed_ids_menu.append((t("Back"), lambda: MENU_EXIT))
        submenu = Menu(self.ctx, seed_ids_menu)
        index, status = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return MENU_CONTINUE
        return status

    def new_key(self):
        """Handler for the 'new mnemonic' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("Via D6"), self.new_key_from_d6),
                (t("Via D20"), self.new_key_from_d20),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        index, status = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return MENU_CONTINUE
        return status

    def new_key_from_d6(self):
        """Handler for the 'via D6' menu item"""
        return self._new_key_from_die(D6_STATES, D6_12W_MIN_ROLLS, D6_24W_MIN_ROLLS)

    def new_key_from_d20(self):
        """Handler for the 'via D20' menu item"""
        return self._new_key_from_die(D20_STATES, D20_12W_MIN_ROLLS, D20_24W_MIN_ROLLS)

    def _new_key_from_die(self, roll_states, min_rolls_12w, min_rolls_24w):
        submenu = Menu(
            self.ctx,
            [
                (t("12 words"), lambda: MENU_EXIT),
                (t("24 words"), lambda: MENU_EXIT),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        index, _ = submenu.run_loop()
        if index == 2:
            return MENU_CONTINUE

        min_rolls = min_rolls_12w if index == 0 else min_rolls_24w
        self.ctx.display.clear()

        delete_flag = False
        self.ctx.display.draw_hcentered_text(
            t("Roll die at least %d times to generate a mnemonic.") % (min_rolls)
        )
        if self.prompt(t("Proceed?"), self.ctx.display.bottom_prompt_line):
            rolls = []

            def delete_roll(buffer):
                # buffer not used here
                nonlocal delete_flag
                delete_flag = True
                return buffer

            while True:
                roll = ""
                while True:
                    dice_title = t("Rolls: %d\n") % len(rolls)
                    entropy = (
                        "".join(rolls) if len(roll_states) < 10 else "-".join(rolls)
                    )
                    if len(entropy) <= 10:
                        dice_title += entropy
                    else:
                        dice_title += "..." + entropy[-10:]
                    roll = self.capture_from_keypad(
                        dice_title,
                        [roll_states],
                        delete_key_fn=delete_roll,
                        go_on_change=True,
                    )
                    if roll == ESC_KEY:
                        return MENU_CONTINUE
                    break

                if roll != "":
                    rolls.append(roll)
                else:
                    # If its not a roll it is Del or Go
                    if delete_flag:  # Del
                        delete_flag = False
                        if len(rolls) > 0:
                            rolls.pop()
                    elif len(rolls) < min_rolls:  # Not enough to Go
                        self.ctx.display.flash_text(t("Not enough rolls!"))
                    else:  # Go
                        break

            entropy = "".join(rolls) if len(roll_states) < 10 else "-".join(rolls)

            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Rolls:\n\n%s") % entropy)
            self.ctx.input.wait_for_button()

            entropy_bytes = entropy.encode()
            entropy_hash = binascii.hexlify(
                hashlib.sha256(entropy_bytes).digest()
            ).decode()
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("SHA256 of rolls:\n\n%s") % entropy_hash
            )
            self.ctx.input.wait_for_button()
            num_bytes = 16 if min_rolls == min_rolls_12w else 32
            words = bip39.mnemonic_from_bytes(
                hashlib.sha256(entropy_bytes).digest()[:num_bytes]
            ).split()
            return self._load_key_from_words(words)

        return MENU_CONTINUE

    def _load_qr_passphrase(self):
        data, _ = self.capture_qr_code()
        if data is None:
            self.ctx.display.flash_text(t("Failed to load passphrase"), lcd.RED)
            return MENU_CONTINUE
        if len(data) > PASSPHRASE_MAX_LEN:
            self.ctx.display.flash_text(
                t("Maximum passphrase length exceeded (%s)") % PASSPHRASE_MAX_LEN,
                lcd.RED,
            )
            return MENU_CONTINUE
        return data

    def _load_key_from_words(self, words):
        mnemonic = " ".join(words)
        self.display_mnemonic(mnemonic)
        if not self.prompt(t("Continue?"), self.ctx.display.bottom_prompt_line):
            return MENU_CONTINUE
        self.ctx.display.clear()

        while True:
            submenu = Menu(
                self.ctx,
                [
                    (t("Type BIP39 passphrase"), self.load_passphrase),
                    (t("Scan BIP39 passphrase"), self._load_qr_passphrase),
                    (t("No BIP39 passphrase"), lambda: ""),
                ],
            )
            _, passphrase = submenu.run_loop()
            if passphrase in (ESC_KEY, MENU_CONTINUE):
                continue

            self.ctx.display.clear()

            # Temporary key, just to show the fingerprint
            temp_key = Key(
                mnemonic,
                False,
                NETWORKS[Settings().bitcoin.network],
                passphrase,
            )

            # Show fingerprint again because password can change the fingerprint,
            # and user needs to confirm not just the words, but the fingerprint too
            continue_string = ""
            if passphrase:
                continue_string += t("Passphrase: ") + passphrase + "\n\n"
            continue_string += (
                temp_key.fingerprint_hex_str(True) + "\n\n" + t("Continue?")
            )

            if self.prompt(
                continue_string,
                self.ctx.display.height() // 2,
            ):
                break

        submenu = Menu(
            self.ctx,
            [
                (
                    t("Single-key")
                    + "\n"
                    + Key.get_default_derivation(
                        False, NETWORKS[Settings().bitcoin.network]
                    ),
                    lambda: MENU_EXIT,
                ),
                (
                    t("Multisig")
                    + "\n"
                    + Key.get_default_derivation(
                        True, NETWORKS[Settings().bitcoin.network]
                    ),
                    lambda: MENU_EXIT,
                ),
            ],
        )
        index, _ = submenu.run_loop()
        multisig = index == 1
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Loading.."))

        del temp_key

        # Permanent wallet loaded
        self.ctx.wallet = Wallet(
            Key(
                mnemonic,
                multisig,
                NETWORKS[Settings().bitcoin.network],
                passphrase,
            )
        )
        try:
            self.ctx.printer = create_printer()
        except:
            self.ctx.log.exception("Exception occurred connecting to printer")
        return MENU_EXIT

    def load_key_from_qr_code(self):
        """Handler for the 'via qr code' menu item"""
        data, qr_format = self.capture_qr_code()
        if data is None:
            self.ctx.display.flash_text(t("Failed to load mnemonic"), lcd.RED)
            return MENU_CONTINUE

        words = []
        if qr_format == FORMAT_UR:
            words = BIP39.from_cbor(data.cbor).words
        else:
            try:
                data_str = data.decode() if not isinstance(data, str) else data
                if " " in data_str and len(data_str.split()) in (12, 24):
                    words = data_str.split()
            except:
                pass

            if not words:
                try:
                    data_bytes = (
                        data.encode("latin-1") if isinstance(data, str) else data
                    )
                    # CompactSeedQR format
                    if len(data_bytes) in (16, 32):
                        words = bip39.mnemonic_from_bytes(data_bytes).split()
                    # SeedQR format
                    elif len(data_bytes) in (48, 96):
                        words = [
                            WORDLIST[int(data_bytes[i : i + 4])]
                            for i in range(0, len(data_bytes), 4)
                        ]
                except:
                    pass

        if not words or (len(words) != 12 and len(words) != 24):
            self.ctx.display.flash_text(t("Invalid mnemonic length"), lcd.RED)
            return MENU_CONTINUE
        return self._load_key_from_words(words)

    def _load_key_from_keypad(
        self,
        title,
        charset,
        to_word,
        test_phrase_sentinel=None,
        autocomplete_fn=None,
        possible_keys_fn=None,
    ):
        words = []
        self.ctx.display.draw_hcentered_text(title)
        if self.prompt(t("Proceed?"), self.ctx.display.bottom_prompt_line):
            while len(words) < 24:
                if len(words) == 12:
                    self.ctx.display.clear()
                    if self.prompt(t("Done?"), self.ctx.display.height() // 2):
                        break

                word = ""
                word_num = ""
                while True:
                    word_num = ""
                    word = self.capture_from_keypad(
                        t("Word %d") % (len(words) + 1),
                        [charset],
                        autocomplete_fn,
                        possible_keys_fn,
                    )
                    if word == ESC_KEY:
                        return MENU_CONTINUE
                    # If the last 'word' is blank,
                    # pick a random final word that is a valid checksum
                    if (len(words) in (11, 23)) and word == "":
                        break
                    # If the first 'word' is the test phrase sentinel,
                    # we're testing and just want the test words
                    if (
                        len(words) == 0
                        and test_phrase_sentinel is not None
                        and word == test_phrase_sentinel
                    ):
                        break
                    if word != "":
                        word_num = word
                        word = to_word(word)
                    if word != "":
                        break

                if word not in WORDLIST:
                    if word == test_phrase_sentinel:
                        words = [
                            WORDLIST[0] if n + 1 < 12 else WORDLIST[1879]
                            for n in range(12)
                        ]
                        break

                    if word == "":
                        word = Key.pick_final_word(self.ctx.input.entropy, words)

                self.ctx.display.clear()
                if word_num == word:
                    word_num = ""
                else:
                    word_num += ": "
                if self.prompt(
                    str(len(words) + 1) + ".\n\n" + word_num + word + "\n\n",
                    self.ctx.display.height() // 2,
                ):
                    words.append(word)

            return self._load_key_from_words(words)

        return MENU_CONTINUE

    def load_key_from_text(self):
        """Handler for the 'via text' menu item"""
        title = t("Enter each word of your BIP-39 mnemonic.")

        # Precompute start and stop indexes for each letter in the wordlist
        # to reduce the search space for autocomplete, possible_letters, etc.
        # This is much cheaper (memory-wise) than a trie.
        search_ranges = {}
        i = 0
        while i < len(WORDLIST):
            start_word = WORDLIST[i]
            start_letter = start_word[0]
            j = i + 1
            while j < len(WORDLIST):
                end_word = WORDLIST[j]
                end_letter = end_word[0]
                if end_letter != start_letter:
                    search_ranges[start_letter] = (i, j)
                    i = j - 1
                    break
                j += 1
            if start_letter not in search_ranges:
                search_ranges[start_letter] = (i, j)
            i += 1

        def autocomplete(prefix):
            if len(prefix) > 0:
                letter = prefix[0]
                if letter not in search_ranges:
                    return None
                start, stop = search_ranges[letter]
                matching_words = list(
                    filter(
                        lambda word: word.startswith(prefix),
                        WORDLIST[start:stop],
                    )
                )
                if len(matching_words) == 1:
                    return matching_words[0]
            return None

        def to_word(user_input):
            if len(user_input) > 0:
                letter = user_input[0]
                if letter not in search_ranges:
                    return ""
                start, stop = search_ranges[letter]
                if user_input in WORDLIST[start:stop]:
                    return user_input
            return ""

        def possible_letters(prefix):
            if len(prefix) == 0:
                return LETTERS
            letter = prefix[0]
            if letter not in search_ranges:
                return ""
            start, stop = search_ranges[letter]
            return {
                word[len(prefix)]
                for word in WORDLIST[start:stop]
                if word.startswith(prefix) and len(word) > len(prefix)
            }

        return self._load_key_from_keypad(
            title, LETTERS, to_word, None, autocomplete, possible_letters
        )

    def pre_load_key_from_digits(self):
        """Handler for the 'via numbers' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("Decimal"), lambda: MENU_EXIT),
                (t("Hexadecimal"), lambda: MENU_EXIT),
                (t("Octal"), lambda: MENU_EXIT),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        index, _ = submenu.run_loop()
        self.ctx.display.clear()
        if index == 0:
            return self.load_key_from_digits()
        if index == 1:
            return self.load_key_from_hexadecimal()
        if index == 2:
            return self.load_key_from_octal()
        return MENU_CONTINUE

    def load_key_from_octal(self):
        """Handler for the 'via numbers'>'Octal' submenu item"""
        title = t(
            "Enter each word of your BIP-39 mnemonic as a number in octal from 1 to 4000."
        )

        def autocomplete(prefix):
            # 256 in decimal is 400 in octal
            if len(prefix) == 4 or (len(prefix) == 3 and int(prefix, 8) > 256):
                return prefix
            return None

        def to_word(user_input):
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
        """Handler for the 'via numbers'>'Hexadecimal' submenu item"""
        title = t(
            "Enter each word of your BIP-39 mnemonic as a number in hexadecimal from 1 to 800."
        )

        def autocomplete(prefix):
            # 128 decimal is 0x80
            if len(prefix) == 3 or (len(prefix) == 2 and int(prefix, 16) > 128):
                return prefix
            return None

        def to_word(user_input):
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
        """Handler for the 'via numbers'>'Decimal' submenu item"""
        title = t("Enter each word of your BIP-39 mnemonic as a number from 1 to 2048.")

        def autocomplete(prefix):
            if len(prefix) == 4 or (len(prefix) == 3 and int(prefix) > 204):
                return prefix
            return None

        def to_word(user_input):
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
            SENTINEL_DIGITS,
            autocomplete_fn=autocomplete,
            possible_keys_fn=possible_letters,
        )

    def load_key_from_1248(self):
        """Menu handler to load key from Stackbit 1248 sheet metal storage method"""
        stackbit = Stackbit(self.ctx)
        words = stackbit.enter_1248()
        del stackbit
        if words is not None:
            return self._load_key_from_words(words)
        return MENU_CONTINUE

    def load_key_from_tiny_seed(self):
        """Menu handler to manually load key from Tiny Seed sheet metal storage method"""
        submenu = Menu(
            self.ctx,
            [
                (t("12 words"), lambda: MENU_EXIT),
                (t("24 words"), lambda: MENU_EXIT),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        index, _ = submenu.run_loop()
        self.ctx.display.clear()
        if index == 2:
            return MENU_CONTINUE

        w24 = index == 1
        tiny_seed = TinySeed(self.ctx)
        words = tiny_seed.enter_tiny_seed(w24)
        del tiny_seed
        if words is not None:
            return self._load_key_from_words(words)
        return MENU_CONTINUE

    def load_key_from_tiny_seed_image(self):
        """Menu handler to scan key from Tiny Seed sheet metal storage method"""
        submenu = Menu(
            self.ctx,
            [
                (t("12 words"), lambda: MENU_EXIT),
                (t("24 words"), lambda: MENU_EXIT),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        index, _ = submenu.run_loop()
        self.ctx.display.clear()
        if index == 2:
            return MENU_CONTINUE

        intro = t("Paint punched dots black so they can be detected.") + " "
        intro += t("Use a black background surface.") + " "
        intro += t("Align camera and Tiny Seed properly.")
        self.ctx.display.draw_hcentered_text(intro)
        if not self.prompt(t("Proceed?"), self.ctx.display.bottom_prompt_line):
            return MENU_CONTINUE

        w24 = index == 1
        tiny_scanner = TinyScanner(self.ctx)
        words = tiny_scanner.scanner(w24)
        del tiny_scanner
        if words is None:
            self.ctx.display.flash_text(t("Failed to load mnemonic"), lcd.RED)
            return MENU_CONTINUE
        return self._load_key_from_words(words)

    def load_passphrase(self):
        """Loads and returns a passphrase from keypad"""
        return self.capture_from_keypad(
            t("Passphrase"), [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2]
        )

    def _draw_settings_pad(self):
        """Draws buttons to change settings with touch"""
        if self.ctx.input.touch is not None:
            self.ctx.input.touch.clear_regions()
            offset_y = self.ctx.display.height() * 2 // 3
            self.ctx.input.touch.add_y_delimiter(offset_y)
            self.ctx.input.touch.add_y_delimiter(
                offset_y + self.ctx.display.font_height * 3
            )
            button_width = (self.ctx.display.width() - 2 * DEFAULT_PADDING) // 3
            for i in range(4):
                self.ctx.input.touch.add_x_delimiter(DEFAULT_PADDING + button_width * i)
            offset_y += self.ctx.display.font_height
            keys = ["<", t("Go"), ">"]
            for i, x in enumerate(self.ctx.input.touch.x_regions[:-1]):
                self.ctx.display.outline(
                    x,
                    self.ctx.input.touch.y_regions[0],
                    button_width - 1,
                    self.ctx.display.font_height * 3,
                    lcd.DARKGREY,
                )
                offset_x = x
                offset_x += (
                    button_width - len(keys[i]) * self.ctx.display.font_width
                ) // 2
                self.ctx.display.draw_string(offset_x, offset_y, keys[i], lcd.WHITE)

    def _touch_to_physical(self, index):
        """Mimics touch presses into physical button presses"""
        if index == 0:
            return BUTTON_PAGE_PREV
        if index == 1:
            return BUTTON_ENTER
        return BUTTON_PAGE

    def tools(self):
        """Handler for the 'Tools' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("Check SD Card"), self.sd_check),
                (t("Print Test QR"), self.print_test),
                (t("Create QR Code"), self.create_qr),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        submenu.run_loop()
        self.ctx.display.clear()

        return MENU_CONTINUE

    def create_qr(self):
        """Handler for the 'Create QR Code' menu item"""
        if self.prompt(
            t("Create QR code from text?"),
            self.ctx.display.height() // 2,
        ):
            text = self.load_passphrase()
            if text in ("", ESC_KEY):
                return MENU_CONTINUE

            self.display_qr_codes(text, FORMAT_NONE, text, allow_any_btn=True)

            try:
                self.ctx.printer = create_printer()
            except:
                self.ctx.log.exception("Exception occurred connecting to printer")

            self.print_qr_prompt(text, FORMAT_NONE, text)
        return MENU_CONTINUE

    def print_test(self):
        """Handler for the 'Print Test QR' menu item"""
        try:
            self.ctx.printer = create_printer()
            if not self.ctx.printer:
                self.ctx.display.flash_text(t("Printer Driver not set!"), lcd.RED)
                return MENU_CONTINUE
        except:
            self.ctx.log.exception("Exception occurred connecting to printer")
            raise

        title = t("Krux Printer Test QR")
        self.display_qr_codes(title, FORMAT_NONE, title, allow_any_btn=True)
        self.print_qr_prompt(title, FORMAT_NONE, title)

        return MENU_CONTINUE

    def sd_check(self):
        """Handler for the 'SD Check' menu item"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Checking for SD card.."))
        try:
            # Check for SD hot-plug
            with SDHandler():
                sd_status = uos.statvfs(SD_ROOT_PATH)
                sd_total = int(sd_status[2] * sd_status[1] / 1024 / 1024)
                sd_free = int(sd_status[4] * sd_status[1] / 1024 / 1024)

                self.ctx.display.clear()
                self.ctx.display.draw_hcentered_text(
                    t("SD card")
                    + "\n\n"
                    + t("Size: ")
                    + "{:,}".format(sd_total)
                    + " MB"
                    + "\n\n"
                    + t("Used: ")
                    + "{:,}".format(sd_total - sd_free)
                    + " MB"
                    + "\n\n"
                    + t("Free: ")
                    + "{:,}".format(sd_free)
                    + " MB"
                )
                if self.prompt(
                    t("Explore files?"), self.ctx.display.bottom_prompt_line
                ):
                    self.select_file(select_file_handler=self._show_file_details)
        except OSError:
            self.ctx.display.flash_text(t("SD card not detected"), lcd.RED)

        return MENU_CONTINUE

    def _show_file_details(self, file):
        """Handler to print file info when selecting a file in the file explorer"""
        if SDHandler.dir_exists(file):
            return MENU_EXIT

        stats = uos.stat(file)
        size = stats[6] / 1024
        size_deximal_places = str(int(size * 100))[-2:]
        created = time.localtime(stats[9])
        modified = time.localtime(stats[8])
        file = file[4:] # remove "/sd/" prefix
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(
            file
            + "\n\n"
            + t("Size: ")
            + "{:,}".format(int(size))
            + "."
            + size_deximal_places
            + " KB"
            + "\n\n"
            + t("Created: ")
            + "%s-%s-%s %s:%s"
            % (created[0], created[1], created[2], created[3], created[4])
            + "\n\n"
            + t("Modified: ")
            + "%s-%s-%s %s:%s"
            % (modified[0], modified[1], modified[2], modified[3], modified[4])
        )
        self.ctx.input.wait_for_button()
        # if self.prompt(t("Delete File?"), self.ctx.display.bottom_prompt_line):
        #     with SDHandler() as sd:
        #         sd.delete(file)
        #     return MENU_EXIT
        return MENU_CONTINUE

    def settings(self):
        """Handler for the 'settings' menu item"""
        location = Settings().persist.location
        if location == SD_PATH:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Checking for SD card.."))
            try:
                # Check for SD hot-plug
                with SDHandler():
                    self.display_centered_text(
                        t("Your changes will be kept on the SD card."),
                        duration=SD_MSG_TIME,
                    )
            except OSError:
                self.display_centered_text(
                    t("SD card not detected.")
                    + "\n\n"
                    + t("Changes will last until shutdown."),
                    duration=SD_MSG_TIME,
                )
        else:
            try:
                # Check for flash
                os.listdir("/" + FLASH_PATH + "/.")
                self.display_centered_text(
                    t("Your changes will be kept on device flash storage."),
                    duration=SD_MSG_TIME,
                )
            except OSError:
                self.display_centered_text(
                    t("Device flash storage not detected.")
                    + "\n\n"
                    + t("Changes will last until shutdown."),
                    duration=SD_MSG_TIME,
                )

        return self.namespace(Settings())()

    def _settings_exit_check(self):
        """Handler for the 'Back' on settings screen"""

        # If user selected to persist on SD, we will try to remout and save
        # flash is always mounted, so settings is always persisted
        if Settings().persist.location == SD_PATH:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Checking for SD card.."))
            try:
                # Check for SD hot-plug
                with SDHandler():
                    Store.save_settings()
                    self.display_centered_text(
                        t("Changes persisted to SD card!"),
                        duration=SD_MSG_TIME,
                    )
            except OSError:
                self.display_centered_text(
                    t("SD card not detected.")
                    + "\n\n"
                    + t("Changes will last until shutdown."),
                    duration=SD_MSG_TIME,
                )

        return MENU_EXIT

    def namespace(self, settings_namespace):
        """Handler for navigating a particular settings namespace"""

        def handler():
            setting_list = settings_namespace.setting_list()
            namespace_list = settings_namespace.namespace_list()
            items = [
                (
                    settings_namespace.label(ns.namespace.split(".")[-1]),
                    self.namespace(ns),
                )
                for ns in namespace_list
            ]
            items.extend(
                [
                    (
                        settings_namespace.label(setting.attr),
                        self.setting(settings_namespace, setting),
                    )
                    for setting in setting_list
                ]
            )

            # If there is only one item in the namespace, don't show a submenu
            # and instead jump straight to the item's menu
            if len(items) == 1:
                return items[0][1]()

            # Case for "Back" on the main Settings
            if settings_namespace.namespace == Settings.namespace:
                items.append((t("Back"), self._settings_exit_check))
            else:
                items.append((t("Back"), lambda: MENU_EXIT))

            submenu = Menu(self.ctx, items)
            index, status = submenu.run_loop()
            if index == len(submenu.menu) - 1:
                return MENU_CONTINUE
            return status

        return handler

    def setting(self, settings_namespace, setting):
        """Handler for viewing and editing a particular setting"""

        def handler():
            if isinstance(setting, CategorySetting):
                return self.category_setting(settings_namespace, setting)

            if isinstance(setting, NumberSetting):
                self.number_setting(settings_namespace, setting)
                if settings_namespace.namespace == TouchSettings.namespace:
                    self._touch_threshold_exit_check()

            return MENU_CONTINUE

        return handler

    def _touch_threshold_exit_check(self):
        """Handler for the 'Back' on settings screen"""

        # Update touch detection threshold
        if self.ctx.input.touch is not None:
            self.ctx.input.touch.touch_driver.threshold(Settings().touch.threshold)

    def category_setting(self, settings_namespace, setting):
        """Handler for viewing and editing a CategorySetting"""
        categories = setting.categories

        starting_category = setting.__get__(settings_namespace)
        while True:
            current_category = setting.__get__(settings_namespace)
            color = CATEGORY_SETTING_COLOR_DICT.get(current_category, lcd.WHITE)
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                settings_namespace.label(setting.attr) + "\n" + str(current_category),
                color,
            )
            self._draw_settings_pad()
            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_TOUCH:
                btn = self._touch_to_physical(self.ctx.input.touch.current_index())
            if btn == BUTTON_ENTER:
                break
            for i, category in enumerate(categories):
                if current_category == category:
                    if btn in (BUTTON_PAGE, None):
                        new_category = categories[(i + 1) % len(categories)]
                    elif btn == BUTTON_PAGE_PREV:
                        new_category = categories[(i - 1) % len(categories)]
                    setting.__set__(settings_namespace, new_category)
                    break

        # When changing locale, exit Login to force recreate with new locale
        if (
            setting.attr == "locale"
            and setting.__get__(settings_namespace) != starting_category
        ):
            return MENU_EXIT
        return MENU_CONTINUE

    def number_setting(self, settings_namespace, setting):
        """Handler for viewing and editing a NumberSetting"""

        starting_value = setting.numtype(setting.__get__(settings_namespace))

        numerals = DIGITS
        # add the dot symbol when number type is float
        if setting.numtype == float:
            numerals += "."

        new_value = self.capture_from_keypad(
            settings_namespace.label(setting.attr),
            [numerals],
            starting_buffer=str(starting_value),
            esc_prompt=False,
        )
        if new_value in (ESC_KEY, ""):
            return MENU_CONTINUE

        new_value = setting.numtype(new_value)
        if setting.value_range[0] <= new_value <= setting.value_range[1]:
            setting.__set__(settings_namespace, new_value)
        else:
            self.ctx.display.flash_text(
                t("Value %s out of range: [%s, %s]")
                % (new_value, setting.value_range[0], setting.value_range[1]),
                lcd.RED,
            )

        return MENU_CONTINUE

    def about(self):
        """Handler for the 'about' menu item"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Krux\n\n\nVersion\n%s") % VERSION)
        self.ctx.input.wait_for_button()
        return MENU_CONTINUE
