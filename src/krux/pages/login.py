# The MIT License (MIT)

# Copyright (c) 2021 Tom J. Sun

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
import binascii
import hashlib
import lcd
from embit.networks import NETWORKS
from embit.wordlists.bip39 import WORDLIST
import urtypes
from ..logging import LEVEL_NAMES, level_name, Logger, DEBUG
from ..metadata import VERSION
from ..settings import settings
from ..input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_TOUCH
from ..qr import FORMAT_UR
from ..key import Key, pick_final_word, to_mnemonic_words
from ..wallet import Wallet
from ..printers import create_printer
from ..i18n import t, translations
from . import Page, Menu, MENU_CONTINUE, MENU_EXIT, DEFAULT_PADDING

SENTINEL_DIGITS = "11111"

DIGITS = "0123456789"
LETTERS = "abcdefghijklmnopqrstuvwxyz"
BITS = "01"

D6_STATES = "123456"
D20_STATES = [str(i + 1) for i in range(20)]

D6_MIN_ROLLS = 50
D6_MAX_ROLLS = 100
D20_MIN_ROLLS = 30
D20_MAX_ROLLS = 60


class Login(Page):
    """Represents the login page of the app"""

    def __init__(self, ctx):
        menu = [
            (t("Load Mnemonic"), self.load_key),
            (t("New Mnemonic"), self.new_key),
            (t("Settings"), self.settings),
            (t("About"), self.about),
            (t("Shutdown"), self.shutdown),
        ]
        if settings.log.level <= DEBUG:
            menu.append((t("DEBUG"), lambda: MENU_CONTINUE))
        Page.__init__(self, ctx, Menu(ctx, menu))

    def load_key(self):
        """Handler for the 'load mnemonic' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("Via QR Code"), self.load_key_from_qr_code),
                (t("Via Text"), self.load_key_from_text),
                (t("Via Numbers"), self.load_key_from_digits),
                (t("Via Bits"), self.load_key_from_bits),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
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
        return self._new_key_from_die(D6_STATES, D6_MIN_ROLLS, D6_MAX_ROLLS)

    def new_key_from_d20(self):
        """Handler for the 'via D20' menu item"""
        return self._new_key_from_die(D20_STATES, D20_MIN_ROLLS, D20_MAX_ROLLS)

    def _new_key_from_die(self, states, min_rolls, max_rolls):
        self.ctx.display.draw_hcentered_text(
            t(
                "Roll die %d or %d times to generate a 12- or 24-word mnemonic, respectively."
            )
            % (min_rolls, max_rolls)
        )
        btn = self.prompt(t("Proceed?"), self.ctx.display.bottom_prompt_line)
        if btn == BUTTON_ENTER:
            entropy = ""
            num_rolls = max_rolls
            for i in range(max_rolls):
                if i == min_rolls:
                    self.ctx.display.clear()
                    btn = self.prompt(t("Done?"), self.ctx.display.bottom_prompt_line)
                    if btn == BUTTON_ENTER:
                        num_rolls = min_rolls
                        break

                roll = ""
                while True:
                    roll = self.capture_from_keypad(
                        t("Roll %d") % (i + 1), states, lambda r: r
                    )
                    if roll == MENU_CONTINUE:
                        self.ctx.display.clear()
                        btn = self.prompt(t("Are you sure?"), self.ctx.display.bottom_prompt_line)
                        if btn == BUTTON_ENTER:
                            return MENU_CONTINUE
                        else:
                            roll = ""
                    if roll != "" and roll in states:
                        break

                entropy += roll if entropy == "" else "-" + roll

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
            num_bytes = 16 if num_rolls == min_rolls else 32
            words = to_mnemonic_words(
                hashlib.sha256(entropy_bytes).digest()[:num_bytes]
            )
            return self._load_key_from_words(words)

        return MENU_CONTINUE

    def _load_key_from_words(self, words):
        mnemonic = " ".join(words)
        self.display_mnemonic(mnemonic)
        btn = self.prompt(t("Continue?"), self.ctx.display.bottom_prompt_line)
        if btn == BUTTON_ENTER:
            submenu = Menu(
                self.ctx,
                [
                    (t("Single-key"), lambda: MENU_EXIT),
                    (t("Multisig"), lambda: MENU_EXIT),
                ],
            )
            index, _ = submenu.run_loop()
            multisig = index == 1
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Loading.."))
            self.ctx.wallet = Wallet(
                Key(mnemonic, multisig, network=NETWORKS[settings.network])
            )
            try:
                self.ctx.printer = create_printer()
            except:
                self.ctx.log.exception("Exception occurred connecting to printer")
            return MENU_EXIT
        return MENU_CONTINUE

    def load_key_from_qr_code(self):
        """Handler for the 'via qr code' menu item"""
        data, qr_format = self.capture_qr_code()
        if data is None:
            self.ctx.display.flash_text(t("Failed to load mnemonic"), lcd.RED)
            return MENU_CONTINUE

        words = []
        if qr_format == FORMAT_UR:
            words = urtypes.crypto.BIP39.from_cbor(data.cbor).words
        else:
            if " " in data:
                words = data.split(" ")
            elif len(data) == 48 or len(data) == 96:
                for i in range(0, len(data), 4):
                    words.append(WORDLIST[int(data[i : i + 4])])

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
        btn = self.prompt(t("Proceed?"), self.ctx.display.bottom_prompt_line)
        if btn == BUTTON_ENTER:
            for i in range(24):
                if i == 12:
                    self.ctx.display.clear()
                    btn = self.prompt(t("Done?"), self.ctx.display.bottom_prompt_line)
                    if btn == BUTTON_ENTER:
                        break

                word = ""
                while True:
                    word = self.capture_from_keypad(
                        t("Word %d") % (i + 1),
                        charset,
                        autocomplete_fn,
                        possible_keys_fn,
                    )
                    if word == MENU_CONTINUE:
                        self.ctx.display.clear()
                        btn = self.prompt(t("Are you sure?"), self.ctx.display.bottom_prompt_line)
                        if btn == BUTTON_ENTER:
                            return MENU_CONTINUE
                        else:
                            word = ""
                    # If the last 'word' is blank,
                    # pick a random final word that is a valid checksum
                    if (i in (11, 23)) and word == "":
                        break
                    # If the first 'word' is the test phrase sentinel,
                    # we're testing and just want the test words
                    if (
                        i == 0
                        and test_phrase_sentinel is not None
                        and word == test_phrase_sentinel
                    ):
                        break
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
                        word = pick_final_word(self.ctx, words)

                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(word)
                self.ctx.input.wait_for_button()

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

    def load_key_from_digits(self):
        """Handler for the 'via numbers' menu item"""
        title = t("Enter each word of your BIP-39 mnemonic as a number from 1 to 2048.")

        def to_word(user_input):
            word_num = int(user_input)
            if 0 < word_num <= 2048:
                return WORDLIST[word_num - 1]
            return ""

        return self._load_key_from_keypad(title, DIGITS, to_word, SENTINEL_DIGITS)

    def load_key_from_bits(self):
        """Handler for the 'via bits' menu item"""
        title = t(
            "Enter each word of your BIP-39 mnemonic as a series of binary digits."
        )

        def to_word(user_input):
            word_index = int("0b" + user_input, 0)
            if 0 <= word_index < 2048:
                return WORDLIST[word_index]
            return ""

        return self._load_key_from_keypad(title, BITS, to_word)

    def _draw_settings_pad(self):
        """Draws buttons to change settings with touch"""
        if self.ctx.input.has_touch:
            self.ctx.input.touch.clear_regions()
            offset_y = self.ctx.display.height() * 2 // 3
            self.ctx.input.touch.add_y_delimiter(offset_y)
            self.ctx.input.touch.add_y_delimiter(
                offset_y
                + self.ctx.display.font_height * 3
                )
            button_width = (self.ctx.display.width() - 2 * DEFAULT_PADDING) // 3
            for i in range(4):
                self.ctx.input.touch.add_x_delimiter(DEFAULT_PADDING + button_width * i)
            offset_y += self.ctx.display.font_height
            keys = ["<", "Back", ">"] 
            for i, x in enumerate(self.ctx.input.touch.x_regions[:-1]):
                self.ctx.display.outline(
                    x,
                    self.ctx.input.touch.y_regions[0],
                    button_width - 1,
                    self.ctx.display.font_height * 3,
                    lcd.DARKGREY,
                )
                #assuming inverted X coordinates
                offset_x = self.ctx.display.width() - (x + button_width)
                offset_x += (button_width - len(keys[i]) * self.ctx.display.font_width) // 2
                lcd.draw_string(offset_x, offset_y, keys[i], lcd.WHITE)

    def _touch_to_physical(self):
        """Mimics touch presses into phisical buttons presses"""
        if self.ctx.input.touch.index == 0:
            return BUTTON_PAGE_PREV
        elif self.ctx.input.touch.index == 1:
            return BUTTON_ENTER
        elif self.ctx.input.touch.index == 2:
            return BUTTON_PAGE

    def settings(self):
        """Handler for the 'settings' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("Network"), self.network),
                (t("Printer"), self.printer),
                (t("Locale"), self.locale),
                (t("Debug"), self.debug),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        index, status = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return MENU_CONTINUE
        return status

    def network(self):
        """Handler for the 'network' menu item"""
        networks = settings.networks

        starting_network = settings.network
        while True:
            current_network = settings.network

            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Network\n%snet") % current_network)
            self._draw_settings_pad()
            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_TOUCH:
                btn = self._touch_to_physical()
            if btn == BUTTON_ENTER:
                break
            else:
                for i, network in enumerate(networks):
                    if current_network == network:
                        if btn == BUTTON_PAGE:
                            new_network = networks[(i + 1) % len(networks)]
                        else: #BUTTON_PAGE_PREV
                            new_network = networks[(i - 1) % len(networks)]
                        settings.network = new_network
                        break
        if settings.network == starting_network:
            return MENU_CONTINUE
        # Force a page refresh if the setting was changed
        return MENU_EXIT

    def printer(self):
        """Handler for the 'printer' menu item"""
        baudrates = settings.printer.thermal.baudrates

        starting_baudrate = settings.printer.thermal.baudrate
        while True:
            current_baudrate = settings.printer.thermal.baudrate

            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Baudrate\n%s") % current_baudrate)

            self._draw_settings_pad()
            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_TOUCH:
                btn = self._touch_to_physical()
            if btn == BUTTON_ENTER:
                break
            else:
                for i, baudrate in enumerate(baudrates):
                    if current_baudrate == baudrate:
                        if btn == BUTTON_PAGE:
                            new_baudrate = baudrates[(i + 1) % len(baudrates)]
                        else: #BUTTON_PAGE_PREV
                            new_baudrate = baudrates[(i - 1) % len(baudrates)]
                        settings.printer.thermal.baudrate = new_baudrate
                        break
        if settings.printer.thermal.baudrate == starting_baudrate:
            return MENU_CONTINUE
        # Force a page refresh if the setting was changed
        return MENU_EXIT

    def locale(self):
        """Handler for the 'locale' menu item"""
        locales = settings.i18n.locales

        starting_locale = settings.i18n.locale
        while True:
            current_locale = settings.i18n.locale

            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Locale\n%s") % current_locale)

            self._draw_settings_pad()
            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_TOUCH:
                btn = self._touch_to_physical()
            if btn == BUTTON_ENTER:
                break
            else:
                for i, locale in enumerate(locales):
                    if current_locale == locale:
                        if btn == BUTTON_PAGE:
                            new_locale = locales[(i + 1) % len(locales)]
                        else: #BUTTON_PAGE_PREV
                            new_locale = locales[(i - 1) % len(locales)]
                        # Don't let the user change the locale if translations can't be looked up
                        if translations(new_locale):
                            settings.i18n.locale = new_locale
                        break
        if settings.i18n.locale == starting_locale:
            return MENU_CONTINUE
        # Force a page refresh if the setting was changed
        return MENU_EXIT

    def debug(self):
        """Handler for the 'debug' menu item"""
        levels = sorted(LEVEL_NAMES.keys())

        starting_level = settings.log.level
        while True:
            current_level = settings.log.level

            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Log Level\n%s") % level_name(current_level)
            )

            self._draw_settings_pad()
            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_TOUCH:
                btn = self._touch_to_physical()
            if btn == BUTTON_ENTER:
                break
            else:
                for i, level in enumerate(levels):
                    if current_level == level:
                        if btn == BUTTON_PAGE:
                            new_level = levels[(i + 1) % len(levels)]
                        else: #BUTTON_PAGE_PREV
                            new_level = levels[(i - 1) % len(levels)]
                        settings.log.level = new_level
                        self.ctx.log = Logger(settings.log.path, settings.log.level)
                        break
        if settings.log.level == starting_level:
            return MENU_CONTINUE
        # Force a page refresh if the setting was changed
        return MENU_EXIT

    def about(self):
        """Handler for the 'about' menu item"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Krux\n\n\nVersion\n%s") % VERSION)
        self.ctx.input.wait_for_button()
        return MENU_CONTINUE
