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
from logging import LEVEL_NAMES, level_name, Logger
import lcd
from embit.networks import NETWORKS
from embit.wordlists.bip39 import WORDLIST
import urtypes
from printer import Printer
import settings
from page import Page
from menu import Menu, MENU_CONTINUE, MENU_EXIT
from input import BUTTON_ENTER, BUTTON_PAGE
from qr import FORMAT_UR
from key import Key, pick_final_word
from wallet import Wallet

TEST_PHRASE_DIGITS  = '11111'
TEST_PHRASE_LETTERS = 'aaaaa'
FINAL_WORD_DIGITS   = '99999'
FINAL_WORD_LETTERS  = 'zzzzz'

class Login(Page):
    """Represents the login page of the app"""

    def __init__(self, ctx):
        menu = [
            (( 'Load Mnemonic' ), self.load_key),
            (( 'Settings' ), self.settings),
            (( 'About' ), self.about),
            (( 'Shutdown' ), self.shutdown),
        ]
        if ctx.debugging():
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
            self.ctx.display.flash_text(( 'Loading..' ))
            self.ctx.wallet = Wallet(Key(' '.join(words), multisig, network=NETWORKS[self.ctx.net]))
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
                    word = self.capture_letters_from_keypad(( 'Word %d' ) % (i+1))
                    if word in WORDLIST:
                        break
                    # If the first 'word' is the TEST_PHRASE_LETTERS sentinel,
                    # we're testing and just want the test words
                    if i == 0 and word == TEST_PHRASE_LETTERS:
                        break
                    # If the last 'word' is the FINAL_WORD_LETTERS sentinel,
                    # pick a random final word that is a valid checksum
                    if (i in (11, 23)) and word == FINAL_WORD_LETTERS:
                        break

                if word == TEST_PHRASE_LETTERS:
                    words = [WORDLIST[0] if n + 1 < 12 else WORDLIST[1879] for n in range(12)]
                    break

                if word == FINAL_WORD_LETTERS:
                    word = pick_final_word(words)

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
                    digits = self.capture_digits_from_numpad(( 'Word %d' ) % (i+1))
                    if int(digits) >= 1 and int(digits) <= 2048:
                        break
                    # If the first 'word' is the TEST_PHRASE_DIGITS sentinel,
                    # we're testing and just want the test words
                    if i == 0 and digits == TEST_PHRASE_DIGITS:
                        break
                    # If the last 'word' is the FINAL_WORD_DIGITS sentinel,
                    # pick a random final word that is a valid checksum
                    if (i in (11, 23)) and digits == FINAL_WORD_DIGITS:
                        break

                if digits == TEST_PHRASE_DIGITS:
                    words = [WORDLIST[0] if n + 1 < 12 else WORDLIST[1879] for n in range(12)]
                    break

                word = ''
                if digits == FINAL_WORD_DIGITS:
                    word = pick_final_word(words)
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
                    bits = self.capture_bits_from_numpad(( 'Word %d' ) % (i+1))
                    if len(bits) == 11:
                        break

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
            current_network = settings.load('network', 'main')

            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(( 'Network\n%snet' ) % current_network)

            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_PAGE:
                for i, network in enumerate(networks):
                    if current_network == network:
                        new_network = networks[(i + 1) % len(networks)]
                        settings.save('network', new_network)
                        self.ctx.net = new_network
                        break
            elif btn == BUTTON_ENTER:
                break
        return MENU_CONTINUE

    def printer(self):
        """Handler for the 'printer' menu item"""
        baudrates = ['9600', '19200']

        while True:
            current_baudrate = settings.load('printer.baudrate', '9600')

            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(( 'Baudrate\n%s' ) % current_baudrate)

            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_PAGE:
                for i, baudrate in enumerate(baudrates):
                    if current_baudrate == baudrate:
                        settings.save('printer.baudrate', baudrates[(i + 1) % len(baudrates)])
                        self.ctx.printer = Printer()
                        break
            elif btn == BUTTON_ENTER:
                break
        return MENU_CONTINUE

    def debug(self):
        """Handler for the 'debug' menu item"""
        levels = sorted(LEVEL_NAMES.keys())

        while True:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                ( 'Log Level\n%s' ) % level_name(self.ctx.log.level)
            )

            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_PAGE:
                for i, level in enumerate(levels):
                    if self.ctx.log.level == level:
                        self.ctx.log = Logger(self.ctx.log.filepath, levels[(i + 1) % len(levels)])
                        break
            elif btn == BUTTON_ENTER:
                break
        return MENU_CONTINUE

    def about(self):
        """Handler for the 'about' menu item"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(( 'Krux\n\n\nVersion\n%s' ) % self.ctx.version)
        self.ctx.input.wait_for_button()
        return MENU_CONTINUE
