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

import gc
from embit import bip32, compact
import hashlib
import binascii
from .. import MENU_CONTINUE, LOAD_FROM_CAMERA, LOAD_FROM_SD, Menu
from ...themes import theme
from ...display import (
    DEFAULT_PADDING,
    MINIMAL_DISPLAY,
    FONT_HEIGHT,
    TOTAL_LINES,
    BOTTOM_PROMPT_LINE,
)
from ...baseconv import base_encode
from ...krux_settings import t
from ...qr import FORMAT_NONE
from ...sd_card import (
    SIGNATURE_FILE_EXTENSION,
    SIGNED_FILE_SUFFIX,
    PUBKEY_FILE_EXTENSION,
)
from ..utils import Utils


class SignMessage(Utils):
    """Message Signing user interface"""

    def load_message(self):
        """Loads a message from camera or SD card"""

        load_method = self.load_method()

        if load_method > LOAD_FROM_SD:
            return (None, None, "")

        if load_method == LOAD_FROM_CAMERA:
            from ..qr_capture import QRCodeCapture

            qr_capture = QRCodeCapture(self.ctx)
            data, qr_format = qr_capture.qr_capture_loop()
            return (data, qr_format, "")

        # If load_method == LOAD_FROM_SD
        message_filename, data = self.load_file(prompt=False)
        return (data, FORMAT_NONE, message_filename)

    def sign_at_address(self, data):
        """Message signed at a derived Bitcoin address - Sparrow/Specter"""

        if data.startswith(b"signmessage"):
            data_blocks = data.split(b" ")
            if len(data_blocks) >= 3:
                derivation = data_blocks[1].decode()
                message = b" ".join(data_blocks[2:])
                message = message.split(b":")
                if len(message) >= 2 and message[0] == b"ascii":
                    message = b" ".join(message[1:])
                    derivation = bip32.parse_path(derivation)
                    self.ctx.display.clear()
                    address = self.ctx.wallet.descriptor.derive(
                        derivation[4], branch_index=0
                    ).address(network=self.ctx.wallet.key.network)
                    short_address = self.fit_to_line(
                        address, str(derivation[4]) + ". ", fixed_chars=3
                    )

                    # Maximum lines available for message
                    max_lines = TOTAL_LINES
                    if MINIMAL_DISPLAY:
                        max_lines -= 7
                    else:
                        max_lines -= 10

                    offset_y = DEFAULT_PADDING
                    offset_y += (
                        self.ctx.display.draw_hcentered_text(
                            t("Message:"), offset_y, theme.highlight_color
                        )
                        * FONT_HEIGHT
                    )
                    offset_y += (
                        self.ctx.display.draw_hcentered_text(
                            message.decode(), offset_y, max_lines=max_lines
                        )
                        + 1
                    ) * FONT_HEIGHT
                    offset_y += (
                        self.ctx.display.draw_hcentered_text(
                            t("Address") + ":", offset_y, theme.highlight_color
                        )
                        * FONT_HEIGHT
                    )
                    self.ctx.display.draw_hcentered_text(short_address, offset_y)
                    if not self.prompt(t("Sign?"), BOTTOM_PROMPT_LINE):
                        return ""
                    message_hash = hashlib.sha256(
                        hashlib.sha256(
                            b"\x18Bitcoin Signed Message:\n"
                            + compact.to_bytes(len(message))
                            + message
                        ).digest()
                    ).digest()
                    sig = self.ctx.wallet.key.sign_at(derivation, message_hash)

                    # Encode sig as base64 string
                    encoded_sig = base_encode(sig, 64).strip().decode()
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(
                        t("Signature") + ":\n\n%s" % encoded_sig
                    )
                    self.ctx.input.wait_for_button()
                    return sig
        return None

    def sign_standard_message(self, data):
        """Signs a standard message"""
        message_hash = None
        if len(data) == 32:
            # It's a sha256 hash already
            message_hash = data
        else:
            if len(data) == 64:
                # It may be a hex-encoded sha256 hash
                try:
                    message_hash = binascii.unhexlify(data)
                except:
                    pass
            if message_hash is None:
                # It's a message, so compute its sha256 hash
                message_hash = hashlib.sha256(data).digest()

        # memory management
        del data
        gc.collect()

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            "SHA256:\n%s" % binascii.hexlify(message_hash).decode()
        )
        if not self.prompt(t("Sign?"), BOTTOM_PROMPT_LINE):
            return ""

        # User confirmed to sign!
        sig = self.ctx.wallet.key.sign(message_hash).serialize()

        # Encode sig as base64 string
        encoded_sig = base_encode(sig, 64).decode()
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Signature") + ":\n\n%s" % encoded_sig)
        self.ctx.input.wait_for_button()
        return sig

    def sign_message(self):
        """Sign message user interface"""

        # Load a Message
        data, qr_format, message_filename = self.load_message()

        if data is None:
            self.flash_error(t("Failed to load message"))
            return MENU_CONTINUE

        # message read OK!
        data = data.encode() if isinstance(data, str) else data

        sign_at_address = False
        sig = self.sign_at_address(data)
        if sig is None:  # Not a message to sign at an address
            sig = self.sign_standard_message(data)
        else:
            sign_at_address = True
        if sig == "":  # If user declined to sign
            return MENU_CONTINUE

        sign_menu = Menu(
            self.ctx,
            [
                (t("Sign to QR code"), lambda: None),
                (
                    t("Sign to SD card"),
                    None if not self.has_sd_card() else lambda: None,
                ),
            ],
            back_status=lambda: None,
        )
        index, _ = sign_menu.run_loop()

        if index == 2:  # Back
            return MENU_CONTINUE

        pubkey = binascii.hexlify(self.ctx.wallet.key.account.sec()).decode()

        if index == 0:
            # Show the base64 signed message as a QRCode
            title = t("Signed Message")
            encoded_sig = base_encode(sig, 64).strip().decode()
            self.display_qr_codes(encoded_sig, qr_format, title)
            self.print_standard_qr(encoded_sig, qr_format, title)

            if not sign_at_address:
                # Show the public key as a QRCode
                self.ctx.display.clear()
                title = t("Hex Public Key")
                self.ctx.display.draw_centered_text(title + ":\n\n%s" % pubkey)
                self.ctx.input.wait_for_button()

                # Show the public key in hexadecimal format as a QRCode
                self.display_qr_codes(pubkey, qr_format, title)
                self.print_standard_qr(pubkey, qr_format, title)
            return MENU_CONTINUE

        # If index == 1 save the signature file on the SD card
        if self.has_sd_card():
            from ..file_operations import SaveFile

            save_page = SaveFile(self.ctx)
            save_page.save_file(
                sig,
                "message",
                message_filename,
                t("Signature") + ":",
                SIGNATURE_FILE_EXTENSION,
                SIGNED_FILE_SUFFIX,
            )

            if not sign_at_address:
                # Save the public key on the SD card
                title = t("Hex Public Key")
                save_page.save_file(
                    pubkey, "pubkey", "", title + ":", PUBKEY_FILE_EXTENSION, "", False
                )

        return MENU_CONTINUE
