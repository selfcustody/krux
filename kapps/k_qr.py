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
import os

# avoids importing from flash VSF
os.chdir("/")

VERSION = "1.0"
NAME = "QR Code"
ALLOW_STARTUP = True


def run(ctx):
    """Inconspicuous QR scanner app"""
    from krux.pages.qr_capture import QRCodeCapture
    from binascii import hexlify

    while True:
        try:
            qr_capture = QRCodeCapture(ctx)
            data, _ = qr_capture.qr_capture_loop()
            if data is None:
                continue

            if isinstance(data, bytes):
                try:
                    data = data.decode()
                except:
                    data = "0x" + hexlify(data).decode()

            if data == "krux":
                break

            ctx.display.clear()
            ctx.display.draw_centered_text(data)
            ctx.input.wait_for_button()
        except:
            pass
