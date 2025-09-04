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

import hashlib
import binascii

from embit.util import secp256k1
from .. import Menu, MENU_CONTINUE  # LOAD_FROM_CAMERA, LOAD_FROM_SD,
from .. import Page
from ..utils import Utils
from ...display import (
    BOTTOM_PROMPT_LINE,
)
from ...baseconv import base_encode
from ...krux_settings import t
from ...qr import FORMAT_NONE


PGP_KEY_LEN = 32
PGP_KEY_BITS_LEN = 256
PGP_BIP85_RSA_PATH = 828365

# Using derivation suggested in BIP85 for RSA, although we are using ECDSA curves:
# m/83696968'/828365'/{key_bits}'/{key_index}
# https://github.com/bitcoin/bips/blob/master/bip-0085.mediawiki#rsa
# Currently using parent key to certificate and sign
# TODO:
#   - Implement sub keys:
#      (Sub keys:  <code>m/83696968'/828365'/{key_bits}'/{key_index}'/{sub_key}'</code>)

#     - key_index is the parent key for CERTIFY capability
#     - sub_key <code>0'</code> is used as the ENCRYPTION key
#     - sub_key <code>1'</code> is used as the AUTHENTICATION key
#     - sub_key <code>2'</code> is usually used as SIGNATURE key

#   - Optimize code
#   - Analyze possibility of integrating code with OpenSSL signing
#   - Add support for signing using SD card


class GPG(Page):
    """GPG signing user interface"""

    def __init__(self, ctx, child_index):
        super().__init__(ctx)
        self.ctx = ctx
        self.private_key = self._derive_pgp_key(child_index)

    def gpg_menu(self):
        """Handler for the 'sign file' menu item"""
        return Menu(
            self.ctx,
            [
                (t("Create GPG Public Key"), self.export_pgp_pubkey),
                (t("Sign File with GPG"), self.sign_pgp_from_qr),
            ],
        ).run_loop()

    def _derive_pgp_key(self, key_index=0):
        from embit import bip85

        return bip85.derive_entropy(
            self.ctx.wallet.key.root,
            PGP_BIP85_RSA_PATH,
            [PGP_KEY_BITS_LEN, key_index],
        )[:PGP_KEY_LEN]

    def export_pgp_pubkey(self):
        """Creates a PGP public key"""
        pubkey_material = secp256k1.ec_pubkey_create(self.private_key)
        public_key = binascii.hexlify(pubkey_material).decode()
        self._display_and_export_pubkey(public_key)
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Scan and sign GPG public key metadata"))
        if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
            return MENU_CONTINUE
        return self.sign_pgp_from_qr()

    def sign_pgp_from_qr(self):
        """Signs PGP from QR code data"""
        from ..qr_capture import QRCodeCapture

        data, _ = QRCodeCapture(self.ctx).qr_capture_loop()
        self.sign_pgp_file_hash(data)

        return MENU_CONTINUE

    def _display_signature(self, encoded_sig):
        """Helper to display the signature"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            t("Signature:") + "\n\n%s" % encoded_sig, highlight_prefix=":"
        )
        self.ctx.input.wait_for_button()

    def _compute_message_hash(self, data):
        """Computes the hash for the message"""
        if len(data) == 32:
            return data
        if len(data) == 64:
            try:
                return binascii.unhexlify(data)
            except:
                pass
        return hashlib.sha256(data).digest()

    def sign_pgp_file_hash(self, data):
        """Signs a standard message"""

        if data is None:
            return

        message_hash = self._compute_message_hash(data)
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            "SHA256:\n\n%s" % binascii.hexlify(message_hash).decode(),
            highlight_prefix=":",
        )
        if not self.prompt(t("Sign?"), BOTTOM_PROMPT_LINE):
            return

        signature = secp256k1.ecdsa_sign(message_hash, self.private_key)
        encoded_sig = base_encode(signature, 64)
        self._display_signature(encoded_sig)
        self._export_to_qr(encoded_sig)

    def _export_to_qr(self, encoded_sig):
        """Exports the signature to QR code"""
        title = t("Signature:")
        self.display_qr_codes(encoded_sig, FORMAT_NONE, title)
        Utils(self.ctx).print_standard_qr(encoded_sig, FORMAT_NONE, title)

    def _display_and_export_pubkey(self, pubkey):
        """Displays and exports the public key as QR code"""
        title = t("Hex Public Key:")
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            title + "\n\n%s" % pubkey, highlight_prefix=":"
        )
        self.ctx.input.wait_for_button()

        self.display_qr_codes(pubkey, FORMAT_NONE, title)
        Utils(self.ctx).print_standard_qr(pubkey, FORMAT_NONE, title)
