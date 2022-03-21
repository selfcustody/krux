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
import gc
import hashlib
import lcd
from ..baseconv import base_encode
from ..display import DEFAULT_PADDING
from ..psbt import PSBTSigner
from ..qr import FORMAT_NONE, FORMAT_PMOFN
from ..input import BUTTON_ENTER
from ..wallet import Wallet, parse_address
from ..i18n import t
from . import Page, Menu, MENU_CONTINUE, MENU_EXIT


class Home(Page):
    """Home is the main menu page of the app"""

    def __init__(self, ctx):
        Page.__init__(
            self,
            ctx,
            Menu(
                ctx,
                [
                    (t("Mnemonic"), self.mnemonic),
                    (t("Extended Public Key"), self.public_key),
                    (t("Wallet"), self.wallet),
                    (t("Scan Address"), self.scan_address),
                    (t("Sign"), self.sign),
                    (t("Shutdown"), self.shutdown),
                ],
            ),
        )

    def mnemonic(self):
        """Handler for the 'mnemonic' menu item"""
        self.display_mnemonic(self.ctx.wallet.key.mnemonic)
        self.ctx.input.wait_for_button()
        self.print_qr_prompt(self.ctx.wallet.key.mnemonic, FORMAT_NONE)
        return MENU_CONTINUE

    def public_key(self):
        """Handler for the 'xpub' menu item"""
        zpub = "Zpub" if self.ctx.wallet.key.multisig else "zpub"
        for version in [None, self.ctx.wallet.key.network[zpub]]:
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                self.ctx.wallet.key.key_expression(version, pretty=True)
            )
            self.ctx.input.wait_for_button()
            xpub = self.ctx.wallet.key.key_expression(version)
            self.display_qr_codes(xpub, FORMAT_NONE, None, DEFAULT_PADDING + 1)
            self.print_qr_prompt(xpub, FORMAT_NONE)
        return MENU_CONTINUE

    def wallet(self):
        """Handler for the 'wallet' menu item"""
        if not self.ctx.wallet.is_loaded():
            self.ctx.display.draw_centered_text(t("Wallet not found."))
            self.ctx.display.draw_hcentered_text(t("Load one?"), offset_y=200)
            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_ENTER:
                return self._load_wallet()
        else:
            self.display_wallet(self.ctx.wallet)
            wallet_data, qr_format = self.ctx.wallet.wallet_qr()
            self.print_qr_prompt(wallet_data, qr_format)
        return MENU_CONTINUE

    def _load_wallet(self):
        wallet_data, qr_format = self.capture_qr_code()
        if wallet_data is None:
            self.ctx.display.flash_text(t("Failed to load wallet"), lcd.RED)
            return MENU_CONTINUE

        try:
            wallet = Wallet(self.ctx.wallet.key)
            wallet.load(wallet_data, qr_format)
            self.display_wallet(wallet, include_qr=False)
            self.ctx.display.draw_hcentered_text(t("Load?"), offset_y=200)
            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_ENTER:
                self.ctx.wallet = wallet
                self.ctx.log.debug(
                    "Wallet descriptor: %s" % self.ctx.wallet.descriptor.to_string()
                )
                self.ctx.display.flash_text(t("Loaded wallet"))
        except Exception as e:
            self.ctx.log.exception("Exception occurred loading wallet")
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Invalid wallet:\n%s") % repr(e), lcd.RED
            )
            self.ctx.input.wait_for_button()
        return MENU_CONTINUE

    def scan_address(self):
        """Handler for the 'scan address' menu item"""
        data, qr_format = self.capture_qr_code()
        if data is None or qr_format != FORMAT_NONE:
            self.ctx.display.flash_text(t("Failed to load address"), lcd.RED)
            return MENU_CONTINUE

        addr = None
        try:
            addr = parse_address(data)
        except:
            self.ctx.display.flash_text(t("Invalid address"), lcd.RED)
            return MENU_CONTINUE

        self.display_qr_codes(data, qr_format, title=addr)
        self.print_qr_prompt(data, qr_format)

        if self.ctx.wallet.is_loaded() or not self.ctx.wallet.is_multisig():
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Check that address belongs to this wallet?")
            )
            btn = self.ctx.input.wait_for_button()
            if btn != BUTTON_ENTER:
                return MENU_CONTINUE

            gc.collect()

            found = False
            num_checked = 0
            for recv_addr in self.ctx.wallet.receive_addresses():
                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(
                    t("Checking receive address %d for match..") % num_checked
                )

                num_checked += 1

                found = addr == recv_addr
                if found:
                    break

                if num_checked % 100 == 0:
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(
                        t("Checked %d receive addresses with no matches.") % num_checked
                    )

                    self.ctx.display.draw_hcentered_text(t("Try more?"), offset_y=200)
                    btn = self.ctx.input.wait_for_button()
                    if btn != BUTTON_ENTER:
                        break

            gc.collect()

            self.ctx.display.clear()
            result_message = (
                t("%s\n\nis a valid receive address") % addr
                if found
                else t("%s\n\nwas NOT FOUND in the first %d receive addresses")
                % (addr, num_checked)
            )
            self.ctx.display.draw_centered_text(result_message)
            self.ctx.input.wait_for_button()
        return MENU_CONTINUE

    def sign(self):
        """Handler for the 'sign' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("PSBT"), self.sign_psbt),
                (t("Message"), self.sign_message),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        index, status = submenu.run_loop()
        if index == len(submenu.menu) - 1:
            return MENU_CONTINUE
        return status

    def sign_psbt(self):
        """Handler for the 'sign psbt' menu item"""
        if not self.ctx.wallet.is_loaded():
            self.ctx.display.draw_centered_text(
                t("WARNING:\nWallet not loaded.\n\nSome checks cannot be performed."),
                lcd.WHITE,
            )
            self.ctx.display.draw_hcentered_text(t("Proceed?"), offset_y=200)
            btn = self.ctx.input.wait_for_button()
            if btn != BUTTON_ENTER:
                return MENU_CONTINUE

        data, qr_format = self.capture_qr_code()
        qr_format = FORMAT_PMOFN if qr_format == FORMAT_NONE else qr_format
        if data is None:
            self.ctx.display.flash_text(t("Failed to load PSBT"), lcd.RED)
            return MENU_CONTINUE

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Loading.."))

        signer = PSBTSigner(self.ctx.wallet, data)
        self.ctx.log.debug("Received PSBT: %s" % signer.psbt)

        outputs = signer.outputs()
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text("\n\n".join(outputs))
        self.ctx.display.draw_hcentered_text(t("Sign?"), offset_y=200)

        btn = self.ctx.input.wait_for_button()
        if btn == BUTTON_ENTER:
            signed_psbt = signer.sign()
            self.ctx.log.debug("Signed PSBT: %s" % signer.psbt)
            signer = None
            gc.collect()
            self.display_qr_codes(signed_psbt, qr_format)
            self.print_qr_prompt(signed_psbt, qr_format)
        return MENU_CONTINUE

    def sign_message(self):
        """Handler for the 'sign message' menu item"""
        data, qr_format = self.capture_qr_code()
        if data is None or qr_format != FORMAT_NONE:
            self.ctx.display.flash_text(t("Failed to load message"), lcd.RED)
            return MENU_CONTINUE

        data = data.encode() if isinstance(data, str) else data

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

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            t("SHA256:\n%s\n\n\n\nSign?") % binascii.hexlify(message_hash).decode()
        )
        if self.ctx.input.wait_for_button() != BUTTON_ENTER:
            return MENU_CONTINUE

        sig = self.ctx.wallet.key.sign(message_hash)

        # Encode sig as base64 string
        encoded_sig = base_encode(sig.serialize(), 64).decode()
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Signature:\n\n%s") % encoded_sig)
        self.ctx.input.wait_for_button()
        self.display_qr_codes(encoded_sig, qr_format)
        self.print_qr_prompt(encoded_sig, qr_format)

        pubkey = binascii.hexlify(self.ctx.wallet.key.account.sec()).decode()
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Public Key:\n\n%s") % pubkey)
        self.ctx.input.wait_for_button()
        self.display_qr_codes(pubkey, qr_format)
        self.print_qr_prompt(pubkey, qr_format)

        return MENU_CONTINUE

    def display_wallet(self, wallet, include_qr=True):
        """Displays a wallet, including its label and abbreviated xpubs.
        If include_qr is True, a QR code of the wallet will be shown
        which will contain the same data as was originally loaded, in
        the same QR format
        """
        about = wallet.label + "\n"
        if wallet.is_multisig():
            xpubs = []
            for i, xpub in enumerate(wallet.policy["cosigners"]):
                xpubs.append(
                    str(i + 1)
                    + ". "
                    + xpub[4:7]
                    + ".."
                    + xpub[len(xpub) - 3 : len(xpub)]
                )
            about += "\n".join(xpubs)
        else:
            xpub = wallet.key.xpub()
            about += xpub[4:7] + ".." + xpub[len(xpub) - 3 : len(xpub)]
        if include_qr:
            wallet_data, qr_format = wallet.wallet_qr()
            self.display_qr_codes(wallet_data, qr_format, title=about)
        else:
            self.ctx.display.draw_hcentered_text(about, offset_y=DEFAULT_PADDING)
