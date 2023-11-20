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

import board
import gc
from embit import bip32, compact
import hashlib
import binascii
from . import Page, MENU_CONTINUE
from ..themes import theme
from ..baseconv import base_encode
from ..krux_settings import t
from ..qr import FORMAT_NONE
from ..sd_card import (
    SIGNATURE_FILE_EXTENSION,
    SIGNED_FILE_SUFFIX,
    PUBKEY_FILE_EXTENSION,
)
from .utils import Utils


class SignMessage(Page):
    """Message Signing user interface"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.utils = Utils(self.ctx)

    def sign_at_address(self, data, qr_format):
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
                    # Amount of lines to subtract for free room for message
                    subtract_lines = 6 if board.config["type"] == "m5stickv" else 10

                    message_to_display = self.ctx.display.to_lines(message.decode())
                    if (
                        len(message_to_display)
                        > self.ctx.display.total_lines - subtract_lines
                    ):
                        message_cut = (
                            self.ctx.display.total_lines - subtract_lines
                        ) // 2
                        message_to_display = (
                            message_to_display[:message_cut]
                            + ["\n...\n"]
                            + message_to_display[-message_cut:]
                        )
                        message_to_display = "".join(message_to_display)
                    else:
                        message_to_display = message.decode()

                    self.ctx.display.draw_hcentered_text(
                        t("Message:")
                        + "\n"
                        + message_to_display
                        + "\n\n"
                        + "Address:"
                        + "\n"
                        + short_address
                    )
                    if not self.prompt(t("Sign?"), self.ctx.display.bottom_prompt_line):
                        return True
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
                    title = t("Signed Message")
                    self.display_qr_codes(encoded_sig, qr_format, title)
                    self.utils.print_standard_qr(encoded_sig, qr_format, title)
                    return True
        return False

    def sign_message(self):
        """Sign message user interface"""

        # Try to read a message from camera
        message_filename = ""
        data, qr_format = self.capture_qr_code()

        if data is None:
            # Try to read a message from a file on the SD card
            qr_format = FORMAT_NONE
            try:
                message_filename, data = self.utils.load_file()
            except OSError:
                pass

        if data is None:
            self.flash_text(t("Failed to load message"), theme.error_color)
            return MENU_CONTINUE

        # message read OK!
        data = data.encode() if isinstance(data, str) else data

        if self.sign_at_address(data, qr_format):
            return MENU_CONTINUE

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
            t("SHA256:\n%s") % binascii.hexlify(message_hash).decode()
        )
        if not self.prompt(t("Sign?"), self.ctx.display.bottom_prompt_line):
            return MENU_CONTINUE

        # User confirmed to sign!
        sig = self.ctx.wallet.key.sign(message_hash).serialize()

        # Encode sig as base64 string
        encoded_sig = base_encode(sig, 64).decode()
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Signature") + ":\n\n%s" % encoded_sig)
        self.ctx.input.wait_for_button()

        # Show the base64 signed message as a QRCode
        title = t("Signed Message")
        self.display_qr_codes(encoded_sig, qr_format, title)
        self.utils.print_standard_qr(encoded_sig, qr_format, title)

        # memory management
        del encoded_sig
        gc.collect()

        # Show the public key as a QRCode
        pubkey = binascii.hexlify(self.ctx.wallet.key.account.sec()).decode()
        self.ctx.display.clear()

        title = t("Hex Public Key")
        self.ctx.display.draw_centered_text(title + ":\n\n%s" % pubkey)
        self.ctx.input.wait_for_button()

        # Show the public key in hexadecimal format as a QRCode
        self.display_qr_codes(pubkey, qr_format, title)
        self.utils.print_standard_qr(pubkey, qr_format, title)

        # memory management
        gc.collect()

        # Try to save the signature file on the SD card
        if self.has_sd_card():
            from .files_operations import SaveFile

            save_page = SaveFile(self.ctx)
            save_page.save_file(
                sig,
                "message",
                message_filename,
                t("Signature") + ":",
                SIGNATURE_FILE_EXTENSION,
                SIGNED_FILE_SUFFIX,
            )

            # Try to save the public key on the SD card
            save_page.save_file(
                pubkey, "pubkey", "", title + ":", PUBKEY_FILE_EXTENSION, "", False
            )

        return MENU_CONTINUE
