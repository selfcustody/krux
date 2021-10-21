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
import time
import lcd
from ur.ur import UR
from embit.wordlists.bip39 import WORDLIST
from input import BUTTON_ENTER, BUTTON_PAGE
from display import DEFAULT_PADDING, DEL, GO
from menu import MENU_SHUTDOWN
from qr import to_qr_codes

QR_ANIMATION_INTERVAL_MS = const(100)

class Page:
    """Represents a page in the app, with helper methods for common display and
       input operations.

       Must be subclassed.
    """

    def __init__(self, ctx, menu):
        self.ctx = ctx
        self.menu = menu
        self._enter_state = -1
        self._page_state = -1

    def capture_digits_from_numpad(self, title):
        """Displays a numpad and captures a series of digits until the user returns.
           Returns a string of digits.
        """
        digits = ''
        key = 0
        while True:
            self.ctx.display.clear()
            self.ctx.display.draw_hcentered_text(title)
            self.ctx.display.draw_numpad(key, digits, mask_digits=False, offset_y=60)

            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_ENTER:
                if key == 11: # Enter
                    break
                if key == 10: # Del
                    digits = digits[:len(digits)-1]
                else:
                    digits += str(key)
            elif btn == BUTTON_PAGE:
                key = (key + 1) % 12
        return digits

    def capture_bits_from_numpad(self, title):
        """Displays a bit pad and captures a series of binary digits until the user returns.
           Returns a string of bits.
        """
        bits = ''
        key = 0
        while True:
            self.ctx.display.clear()
            self.ctx.display.draw_hcentered_text(title)
            self.ctx.display.draw_hcentered_text(bits, offset_y=50)
            self.ctx.display.draw_hcentered_text(('> ' if key == 0 else '') + '0', offset_y=90)
            self.ctx.display.draw_hcentered_text(('> ' if key == 1 else '') + '1', offset_y=110)
            self.ctx.display.draw_hcentered_text(('> ' if key == 2 else '') + DEL, offset_y=130)
            self.ctx.display.draw_hcentered_text(('> ' if key == 3 else '') + GO, offset_y=150)

            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_ENTER:
                if key == 3: # Enter
                    break
                if key == 2: # Del
                    bits = bits[:len(bits)-1]
                else:
                    bits += str(key)
            elif btn == BUTTON_PAGE:
                key = (key + 1) % 4
        return bits

    def capture_letters_from_keypad(self, title):
        """Displays a key pad and captures a series of letters until the user returns.
           Returns a string of letters.
        """
        letters = ''
        key = 0
        while True:
            self.ctx.display.clear()

            self.ctx.display.draw_hcentered_text(title)
            self.ctx.display.draw_keypad(key, letters, mask_letters=False, offset_y=50)

            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_ENTER:
                changed = False
                if key == 27: # Enter
                    break
                if key == 26: # Del
                    letters = letters[:len(letters)-1]
                    changed = True
                else:
                    letters += chr(ord('a') + key)
                    changed = True
                if changed and len(letters) > 2:
                    matching_words = list(filter(lambda word: word.startswith(letters), WORDLIST))
                    if len(matching_words) == 1:
                        letters = matching_words[0]
                        key = 27
            elif btn == BUTTON_PAGE:
                key = (key + 1) % 28
        return letters

    def capture_qr_code(self):
        """Captures a singular or animated series of QR codes and displays progress to the user.
           Returns the contents of the QR code(s).
        """
        self._enter_state = -1
        self._page_state = -1
        def callback(part_total, num_parts_captured, new_part):
            # Turn on the light as long as the enter button is held down
            if self._enter_state == -1:
                self._enter_state = self.ctx.input.enter.value()
            elif self.ctx.input.enter.value() != self._enter_state:
                self._enter_state = self.ctx.input.enter.value()
                self.ctx.light.toggle()

            # Exit the capture loop if the page button is pressed
            if self._page_state == -1:
                self._page_state = self.ctx.input.page.value()
            elif self.ctx.input.page.value() != self._page_state:
                return True

            # Indicate progress to the user that a new part was captured
            if new_part:
                self.ctx.display.to_portrait()
                self.ctx.display.draw_centered_text(
                    '%.0f%%' % (100 * float(num_parts_captured) / float(part_total))
                )
                time.sleep_ms(100)
                self.ctx.display.to_landscape()

            return False

        self.ctx.display.to_landscape()
        code = None
        qr_format = None
        try:
            code, qr_format = self.ctx.camera.capture_qr_code_loop(callback)
        except:
            self.ctx.log.exception('Exception occurred capturing QR code')
        self.ctx.light.turn_off()
        self.ctx.display.to_portrait()
        if code is not None:
            data = code.cbor if isinstance(code, UR) else code
            self.ctx.log.debug('Captured QR Code in format "%d": %s' % (qr_format, data))
        return (code, qr_format)

    def display_qr_codes(self, data, qr_format, title=None, manual=False):
        """Displays a QR code or an animated series of QR codes to the user, encoding them
           in the specified format
        """
        done = False
        i = 0
        code_generator = to_qr_codes(data, self.ctx.display.qr_data_width(), qr_format)
        while not done:
            self.ctx.display.clear()

            code = None
            num_parts = 0
            try:
                code, num_parts = code_generator.__next__()
            except:
                code_generator = to_qr_codes(data, self.ctx.display.qr_data_width(), qr_format)
                code, num_parts = code_generator.__next__()

            self.ctx.display.draw_qr_code(5, code)
            if title is not None:
                self.ctx.display.draw_hcentered_text(title, offset_y=140)
            else:
                self.ctx.display.draw_hcentered_text(
                    ( 'Part %d / %d' ) % (i+1, num_parts), offset_y=175
                )
            i = (i + 1) % num_parts
            btn = self.ctx.input.wait_for_button(block=manual or num_parts == 1)
            done = btn == BUTTON_ENTER
            if not done:
                time.sleep_ms(QR_ANIMATION_INTERVAL_MS)

    def display_mnemonic(self, words):
        """Displays the 12 or 24-word list of words to the user"""
        word_list = [str(i+1) + '.' + ('  ' if i + 1 < 10 else ' ') + word
                     for i, word in enumerate(words)]
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(( 'BIP39 Mnemonic' ))
        for i, word in enumerate(word_list[:12]):
            offset_y = 35 + (i * self.ctx.display.line_height())
            lcd.draw_string(DEFAULT_PADDING, offset_y, word, lcd.WHITE, lcd.BLACK)
        if len(word_list) > 12:
            self.ctx.input.wait_for_button()
            self.ctx.display.clear()
            self.ctx.display.draw_hcentered_text(( 'BIP39 Mnemonic' ))
            for i, word in enumerate(word_list[12:]):
                offset_y = 35 + (i * self.ctx.display.line_height())
                lcd.draw_string(DEFAULT_PADDING, offset_y, word, lcd.WHITE, lcd.BLACK)

    def print_qr_prompt(self, data, qr_format):
        """Prompts the user to print a QR code in the specified format
           if a printer is connected
        """
        if not self.ctx.printer.is_connected():
            return
        self.ctx.display.clear()
        time.sleep_ms(1000)
        self.ctx.display.draw_centered_text(( 'Print to QR?' ))
        btn = self.ctx.input.wait_for_button()
        if btn == BUTTON_ENTER:
            i = 0
            for qr_code, count in to_qr_codes(data, self.ctx.display.qr_data_width(), qr_format):
                if i == count:
                    break
                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(( 'Printing\n%d / %d' ) % (i+1, count))
                self.ctx.printer.print_qr_code(qr_code)
                i += 1

    def shutdown(self):
        """Handler for the 'shutdown' menu item"""
        return MENU_SHUTDOWN

    def run(self):
        """Runs the page's menu loop"""
        _, status = self.menu.run_loop()
        return status != MENU_SHUTDOWN
