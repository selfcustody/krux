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
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
    # ESC_KEY,
    # LETTERS,
    # UPPERCASE_LETTERS,
    # NUM_SPECIAL_1,
    # NUM_SPECIAL_2,
)
from ..krux_settings import t
import sys


# TODO: re-enable "Create a QR Code" (and keypads ^^^) once encryption is possible w/o Datum Tool


class Tools(Page):
    """Krux generic tools"""

    def __init__(self, ctx):
        self.ctx = ctx

        super().__init__(
            ctx,
            Menu(
                ctx,
                [
                    (t("Load Krux app"), self.load_krux_app),
                    (t("Datum Tool"), self.datum_tool),
                    (t("Device Tests"), self.device_tests),
                    # (t("Create QR Code"), self.create_qr),
                    (t("Descriptor Addresses"), self.descriptor_addresses),
                    (t("Flash Tools"), self.flash_tools),
                    (t("Remove Mnemonic"), self.rm_stored_mnemonic),
                ],
            ),
        )

    def load_krux_app(self):
        """Handler for the 'Load Krux app' menu item"""

        # Check if Krux app is enabled
        from krux.krux_settings import Settings

        if not Settings().security.allow_kapp:
            self.flash_error(t("Allow in settings first!"))
            return MENU_CONTINUE

        from krux.pages.kapps import Kapps

        Kapps(self.ctx).run()

        # Unimport kapps
        sys.modules.pop("krux.pages.kapps")
        del sys.modules["krux.pages"].kapps

        return MENU_CONTINUE

    def flash_tools(self):
        """Handler for the 'Flash Tools' menu item"""

        from .flash_tools import FlashTools

        flash_tools = FlashTools(self.ctx)
        flash_tools.flash_tools_menu()
        return MENU_CONTINUE

    def rm_stored_mnemonic(self):
        """Lists and allow deletion of stored mnemonics"""
        from .encryption_ui import LoadEncryptedMnemonic

        encrypted_mnemonics = LoadEncryptedMnemonic(self.ctx)
        while True:
            ret = encrypted_mnemonics.load_from_storage(remove_opt=True)
            if ret == MENU_CONTINUE:
                del encrypted_mnemonics
                return ret

    def datum_tool(self):
        """Handler for the 'Datum Tool' menu item"""
        from .datum_tool import DatumToolMenu

        while True:
            if DatumToolMenu(self.ctx).run() == MENU_EXIT:
                break

        sys.modules.pop("krux.pages.datum_tool")
        del sys.modules["krux.pages"].datum_tool
        return MENU_CONTINUE

    # def create_qr(self):
    #    """Handler for the 'Create QR Code' menu item"""
    #    if self.prompt(
    #        t("Create QR code from text?"),
    #        self.ctx.display.height() // 2,
    #    ):
    #        text = self.capture_from_keypad(
    #            t("Text"), [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2]
    #        )
    #        if text in ("", ESC_KEY):
    #            return MENU_CONTINUE
    #
    #        from .qr_view import SeedQRView
    #
    #        title = t("Custom QR Code")
    #        seed_qr_view = SeedQRView(self.ctx, data=text, title=title)
    #        return seed_qr_view.display_qr(allow_export=True)
    #    return MENU_CONTINUE

    def descriptor_addresses(self):
        """Handler for the 'Descriptor Addresses' menu item"""
        from .home_pages.wallet_descriptor import WalletDescriptor
        from .home_pages.addresses import Addresses
        from ..wallet import Wallet

        self.ctx.wallet = Wallet(None)
        menu_result = WalletDescriptor(self.ctx).wallet()
        if self.ctx.wallet.is_loaded():
            menu_result = Addresses(self.ctx).addresses_menu()
        return menu_result

    def device_tests(self):
        """Handler for the 'Device Tests' menu item"""
        from .device_tests import DeviceTests

        page = DeviceTests(self.ctx)
        page.run()
        sys.modules.pop("krux.pages.device_tests")
        del sys.modules["krux.pages"].device_tests
        return MENU_CONTINUE
