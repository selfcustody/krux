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

from . import (
    Page,
    ESC_KEY,
    LETTERS,
    UPPERCASE_LETTERS,
    NUM_SPECIAL_1,
    NUM_SPECIAL_2,
)
from ..krux_settings import t, TC_CODE_PATH, TC_CODE_PBKDF2_ITERATIONS


class TCCodeVerification(Page):
    """Tamper Check Code Verification Page"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx

    def capture(self, changing_tc_code=False, return_hash=False):
        """Capture Tamper Check Code from user"""
        import uhashlib_hw
        from machine import unique_id

        label = (
            t("Current Tamper Check Code")
            if changing_tc_code
            else t("Tamper Check Code")
        )
        keysets = [NUM_SPECIAL_1, LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_2]
        scan_fn = None if changing_tc_code else self._load_qr_tc_code
        tc_code = self.capture_from_keypad(
            label,
            keysets,
            scan_fn=scan_fn,
        )
        if tc_code == ESC_KEY:
            return False
        # Hashes the tamper check code
        tc_code_bytes = tc_code.encode()
        # Tamper Check Code hash will be used in "TC Flash Hash"
        tc_code_hash = uhashlib_hw.sha256(tc_code_bytes).digest()

        # Read the contents of tamper check code file
        with open(TC_CODE_PATH, "rb") as f:
            file_secret = f.read()

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing…"))

        # Generate PBKDF2 stretched secret
        secret = uhashlib_hw.pbkdf2_hmac_sha256(
            tc_code_hash, unique_id(), TC_CODE_PBKDF2_ITERATIONS
        )
        if secret == file_secret:
            if return_hash:
                return tc_code_hash
            return True

        self.flash_error(t("Invalid Tamper Check Code"))
        return False

    def _load_qr_tc_code(self):
        """Loads and validates a Tamper Check Code from a QR code."""
        from .qr_capture import QRCodeCapture

        qr_capture = QRCodeCapture(self.ctx)
        data, _ = qr_capture.qr_capture_loop()
        tc_code = self._sanitize_qr_tc_code(data)
        if tc_code is None:
            self.flash_error(t("Failed to load"))
        return tc_code

    @staticmethod
    def _sanitize_qr_tc_code(tc_code):
        """Returns a single-line QR value supported by the TC keypad."""
        if isinstance(tc_code, bytes):
            try:
                tc_code = tc_code.decode()
            except (UnicodeError, TypeError):
                return None
        if not isinstance(tc_code, str):
            return None

        if not tc_code or "\n" in tc_code or "\r" in tc_code:
            return None

        allowed_chars = NUM_SPECIAL_1 + LETTERS + UPPERCASE_LETTERS + NUM_SPECIAL_2
        if any(char not in allowed_chars for char in tc_code):
            return None
        return tc_code
