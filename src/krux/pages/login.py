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
from ..settings import Settings
from ..input import BUTTON_ENTER, BUTTON_PAGE
from ..qr import FORMAT_UR
from ..key import Key, pick_final_word, to_mnemonic_words
from ..wallet import Wallet
from . import Page, Menu, MENU_CONTINUE, MENU_EXIT

TEST_PHRASE_DIGITS  = '11111'
TEST_PHRASE_LETTERS = 'aaaaa'

DIGITS  = '0123456789'
LETTERS = 'abcdefghijklmnopqrstuvwxyz'
BITS    = '01'

D6_STATES   = '123456'
D20_STATES  = [str(i+1) for i in range(20)]

D6_MIN_ROLLS  = 50
D6_MAX_ROLLS  = 100
D20_MIN_ROLLS = 30
D20_MAX_ROLLS = 60

class Login(Page):
    """Represents the login page of the app"""

    def __init__(self, ctx):
        menu = [
            (( 'Load Mnemonic' ), self.load_key),
            (( 'New Mnemonic' ), self.new_key),
            (( 'Settings' ), self.settings),
            (( 'About' ), self.about),
            (( 'Shutdown' ), self.shutdown),
        ]
        if Settings.Log.level <= DEBUG:
            menu.append((( 'DEBUG' ), lambda: MENU_CONTINUE))
        Page.__init__(self, ctx, Menu(ctx, menu))

    def load_key(self):
        """Handler for the 'load mnemonic' menu item"""
        submenu = Menu(self.ctx, [
            (( 'Via QR Code' ), self.load_key_from_qr_code),
            (( 'Via Text' ), self.load_key_from_text),
            (( 'Via Numbers' ), self.load_key_from_digits),
            (( 'Via Bits' ), self.load_key_from_bits),
            (( 'Back' ), lambda: MENU_EXIT)
        ])
        index, status = submenu.run_loop()
        if index == len(submenu.menu)-1:
            return MENU_CONTINUE
        return status

    def new_key(self):
        """Handler for the 'new mnemonic' menu item"""
        submenu = Menu(self.ctx, [
            (( 'Via D6' ), self.new_key_from_d6),
            (( 'Via D20' ), self.new_key_from_d20),
            (( 'Back' ), lambda: MENU_EXIT)
        ])
        index, status = submenu.run_loop()
        if index == len(submenu.menu)-1:
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
            ( 'Roll die %d or %d times to generate a 12- or 24-word mnemonic, respectively.' )
            % (min_rolls, max_rolls)
        )
        self.ctx.display.draw_hcentered_text(( 'Proceed?' ), offset_y=200)
        btn = self.ctx.input.wait_for_button()
        if btn == BUTTON_ENTER:
            entropy = ''
            num_rolls = max_rolls
            for i in range(max_rolls):
                if i == min_rolls:
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(( 'Done?' ))
                    btn = self.ctx.input.wait_for_button()
                    if btn == BUTTON_ENTER:
                        num_rolls = min_rolls
                        break

                roll = ''
                while True:
                    roll = self.capture_from_keypad(( 'Roll %d' ) % (i+1), states, lambda r: r)
                    if roll != '' and roll in states:
                        break

                entropy += roll if entropy == '' else '-' + roll

                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(( 'Rolls:\n\n%s' ) % entropy)
                self.ctx.input.wait_for_button()

            entropy_hash = binascii.hexlify(hashlib.sha256(entropy).digest()).decode()
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                ( 'SHA256 of rolls:\n\n%s' ) % entropy_hash
            )
            self.ctx.input.wait_for_button()
            num_bytes = 16 if num_rolls == min_rolls else 32
            words = to_mnemonic_words(hashlib.sha256(entropy).digest()[:num_bytes])
            return self._load_key_from_words(words)

        return MENU_CONTINUE

    def _load_key_from_words(self, words):
        self.display_mnemonic(words)
        self.ctx.display.draw_hcentered_text(( 'Continue?' ), offset_y=220)
        btn = self.ctx.input.wait_for_button()
        if btn == BUTTON_ENTER:
            submenu = Menu(self.ctx, [
                (( 'Single-key' ), lambda: MENU_EXIT),
                (( 'Multisig' ), lambda: MENU_EXIT)
            ])
            index, _ = submenu.run_loop()
            multisig = index == 1
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(( 'Loading..' ))
            self.ctx.wallet = Wallet(Key(' '.join(words), multisig, network=NETWORKS[Settings.network]))
            self.ctx.printer = getattr(__import__('..printers.%s' % Settings.Printer.module), Settings.Printer.cls)()
            return MENU_EXIT
        return MENU_CONTINUE

    def load_key_from_qr_code(self):
        """Handler for the 'via qr code' menu item"""
        data, qr_format = self.capture_qr_code()
        if data is None:
            self.ctx.display.flash_text(( 'Failed to load mnemonic' ), lcd.RED)
            return MENU_CONTINUE

        words = []
        if qr_format == FORMAT_UR:
            try:
                words = urtypes.crypto.BIP39.from_cbor(data.cbor).words
            except:
                words = urtypes.Bytes.from_cbor(data.cbor).data.decode().split(' ')
        else:
            if ' ' in data:
                words = data.split(' ')
            elif len(data) == 48 or len(data) == 96:
                for i in range(0, len(data), 4):
                    words.append(WORDLIST[int(data[i:i+4])])

        if not words or (len(words) != 12 and len(words) != 24):
            self.ctx.display.flash_text(( 'Invalid mnemonic length' ), lcd.RED)
            return MENU_CONTINUE
        return self._load_key_from_words(words)

    def load_key_from_text(self):
        """Handler for the 'via text' menu item"""
        def autocomplete(prefix):
            if len(prefix) > 2:
                matching_words = list(filter(lambda word: word.startswith(prefix), WORDLIST))
                if len(matching_words) == 1:
                    return matching_words[0]
            return None
        words = []
        self.ctx.display.draw_hcentered_text(( 'Enter each word of your BIP-39 mnemonic.' ))
        self.ctx.display.draw_hcentered_text(( 'Proceed?' ), offset_y=200)
        btn = self.ctx.input.wait_for_button()
        if btn == BUTTON_ENTER:
            for i in range(24):
                if i == 12:
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(( 'Done?' ))
                    btn = self.ctx.input.wait_for_button()
                    if btn == BUTTON_ENTER:
                        break

                word = ''
                while True:
                    word = self.capture_from_keypad(( 'Word %d' ) % (i+1), LETTERS, autocomplete)
                    if word != '' and word in WORDLIST:
                        break
                    # If the first 'word' is the TEST_PHRASE_LETTERS sentinel,
                    # we're testing and just want the test words
                    if i == 0 and word == TEST_PHRASE_LETTERS:
                        break
                    # If the last 'word' is blank,
                    # pick a random final word that is a valid checksum
                    if (i in (11, 23)) and word == '':
                        break

                if word == TEST_PHRASE_LETTERS:
                    words = [WORDLIST[0] if n + 1 < 12 else WORDLIST[1879] for n in range(12)]
                    break

                if word == '':
                    word = pick_final_word(self.ctx, words)

                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(word)
                self.ctx.input.wait_for_button()

                words.append(word)

            return self._load_key_from_words(words)

        return MENU_CONTINUE

    def load_key_from_digits(self):
        """Handler for the 'via numbers' menu item"""
        words = []
        self.ctx.display.draw_hcentered_text(
            ( 'Enter each word of your BIP-39 mnemonic as a number from 1 to 2048.' )
        )
        self.ctx.display.draw_hcentered_text(( 'Proceed?' ), offset_y=200)
        btn = self.ctx.input.wait_for_button()
        if btn == BUTTON_ENTER:
            for i in range(24):
                if i == 12:
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(( 'Done?' ))
                    btn = self.ctx.input.wait_for_button()
                    if btn == BUTTON_ENTER:
                        break

                digits = ''
                while True:
                    digits = self.capture_from_keypad(( 'Word %d' ) % (i+1), DIGITS)
                    if digits != '' and int(digits) >= 1 and int(digits) <= 2048:
                        break
                    # If the first 'word' is the TEST_PHRASE_DIGITS sentinel,
                    # we're testing and just want the test words
                    if i == 0 and digits == TEST_PHRASE_DIGITS:
                        break
                    # If the last 'word' is blank,
                    # pick a random final word that is a valid checksum
                    if (i in (11, 23)) and digits == '':
                        break

                if digits == TEST_PHRASE_DIGITS:
                    words = [WORDLIST[0] if n + 1 < 12 else WORDLIST[1879] for n in range(12)]
                    break

                word = ''
                if digits == '':
                    word = pick_final_word(self.ctx, words)
                else:
                    word = WORDLIST[int(digits)-1]

                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(word)
                self.ctx.input.wait_for_button()

                words.append(word)

            return self._load_key_from_words(words)

        return MENU_CONTINUE

    def load_key_from_bits(self):
        """Handler for the 'via bits' menu item"""
        words = []
        self.ctx.display.draw_hcentered_text(
            ( 'Enter each word of your BIP-39 mnemonic as a series of binary digits.' )
        )
        self.ctx.display.draw_hcentered_text(( 'Proceed?' ), offset_y=200)
        btn = self.ctx.input.wait_for_button()
        if btn == BUTTON_ENTER:
            for i in range(24):
                if i == 12:
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(( 'Done?' ))
                    btn = self.ctx.input.wait_for_button()
                    if btn == BUTTON_ENTER:
                        break

                bits = ''
                while True:
                    bits = self.capture_from_keypad(( 'Word %d' ) % (i+1), BITS)
                    if len(bits) == 11:
                        break
                    # If the last 'word' is blank,
                    # pick a random final word that is a valid checksum
                    if (i in (11, 23)) and bits == '':
                        break

                word = ''
                if bits == '':
                    word = pick_final_word(self.ctx, words)
                else:
                    word = WORDLIST[int('0b' + bits, 0)]

                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(word)
                self.ctx.input.wait_for_button()

                words.append(word)

            return self._load_key_from_words(words)

        return MENU_CONTINUE

    def settings(self):
        """Handler for the 'settings' menu item"""
        submenu = Menu(self.ctx, [
            (( 'Network' ), self.network),
            (( 'Printer' ), self.printer),
            (( 'Debug' ), self.debug),
            (( 'Back' ), lambda: MENU_EXIT)
        ])
        index, status = submenu.run_loop()
        if index == len(submenu.menu)-1:
            return MENU_CONTINUE
        return status

    def network(self):
        """Handler for the 'network' menu item"""
        networks = ['main', 'test']

        while True:
            current_network = Settings.network

            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(( 'Network\n%snet' ) % current_network)

            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_PAGE:
                for i, network in enumerate(networks):
                    if current_network == network:
                        new_network = networks[(i + 1) % len(networks)]
                        Settings.network = new_network
                        break
            elif btn == BUTTON_ENTER:
                break
        return MENU_CONTINUE

    def printer(self):
        """Handler for the 'printer' menu item"""
        baudrates = Settings.Printer.Adafruit.baudrates

        while True:
            current_baudrate = Settings.Printer.Adafruit.baudrate

            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(( 'Baudrate\n%s' ) % current_baudrate)

            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_PAGE:
                for i, baudrate in enumerate(baudrates):
                    if current_baudrate == baudrate:
                        new_baudrate = baudrates[(i + 1) % len(baudrates)]
                        Settings.Printer.Adafruit.baudrate = new_baudrate
                        break
            elif btn == BUTTON_ENTER:
                break
        return MENU_CONTINUE

    def debug(self):
        """Handler for the 'debug' menu item"""
        levels = sorted(LEVEL_NAMES.keys())

        while True:
            current_level = Settings.Log.level

            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                ( 'Log Level\n%s' ) % level_name(current_level)
            )

            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_PAGE:
                for i, level in enumerate(levels):
                    if current_level == level:
                        new_level = levels[(i + 1) % len(levels)]
                        Settings.Log.level = new_level
                        self.ctx.log = Logger(Settings.Log.path, Settings.Log.level)
                        break
            elif btn == BUTTON_ENTER:
                break
        return MENU_CONTINUE

    def about(self):
        """Handler for the 'about' menu item"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(( 'Krux\n\n\nVersion\n%s' ) % VERSION)
        self.ctx.input.wait_for_button()
        return MENU_CONTINUE
