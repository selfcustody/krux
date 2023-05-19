# The MIT License (MIT)

# Copyright (c) 2021-2023 Krux contributors

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

import lcd
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

ENCRYPTION_KEY_MAX_LEN = 200

class EncryptionKey(Page):
    """Page to capture an encryption key"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        
    def encryption_key(self):
        """Loads and returns an ecnryption key from keypad or QR code"""
        submenu = Menu(
            self.ctx,
            [
                (t("Type Key"), self.load_key),
                (t("Scan Key QR code"), self.load_qr_encryption_key),
            ],
        )
        _, key = submenu.run_loop()
        if key in (ESC_KEY, MENU_CONTINUE):
            return None
        
        if key:
            self.ctx.display.clear()
            continue_string = t("Key: ") + key + "\n\n"
            continue_string +=  t("Continue?")
            if self.prompt(
                continue_string,
                self.ctx.display.height() // 2,
            ):
                return key
        return None

    def load_key(self):
        """Loads and returns a key from keypad"""
        return self.capture_from_keypad(
            t("key"), [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2]
        )

    def load_qr_encryption_key(self):
        """Loads and returns a key from a QR code"""
        data, _ = self.capture_qr_code()
        if data is None:
            self.ctx.display.flash_text(t("Failed to load key"), lcd.RED)
            return MENU_CONTINUE
        if len(data) > ENCRYPTION_KEY_MAX_LEN:
            self.ctx.display.flash_text(
                t("Maximum length exceeded (%s)") % ENCRYPTION_KEY_MAX_LEN,
                lcd.RED,
            )
            return MENU_CONTINUE
        return data