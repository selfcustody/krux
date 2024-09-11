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

from . import Page, ESC_KEY, DIGITS
from ..krux_settings import t, PIN_PATH


class PinVerification(Page):
    """Pin Verification Page"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def capture(self, changing_pin=False, return_hash=False):
        """Capture PIN from user"""
        import hashlib
        from machine import unique_id

        label = t("Current PIN") if changing_pin else t("PIN")
        pin = self.capture_from_keypad(label, [DIGITS])
        if pin == ESC_KEY:
            return False
        # Double hashes the PIN
        pin_bytes = pin.encode()
        pin_hash = hashlib.sha256(pin_bytes).digest()
        sha256 = hashlib.sha256()
        sha256.update(pin_hash)
        sha256.update(unique_id())
        secret_hash = sha256.digest()
        # Read the contents of PIN file
        with open(PIN_PATH, "rb") as f:
            file_hash = f.read()
        if secret_hash == file_hash:
            if return_hash:
                return pin_hash
            return True
        self.flash_error(t("Invalid PIN"))
        return False
