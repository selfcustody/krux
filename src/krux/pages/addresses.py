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

import gc
from ..krux_settings import t
from ..themes import theme
from ..qr import FORMAT_NONE
from .utils import Utils
from . import (
    Page,
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
)

SCAN_ADDRESS_LIMIT = 20


class Addresses(Page):
    """UI to show and scan wallet addresses"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.utils = Utils(self.ctx)

    def addresses_menu(self):
        """Handler for the 'address' menu item"""
        # only show address for single-sig or multisig with wallet output descriptor loaded
        if not self.ctx.wallet.is_loaded() and self.ctx.wallet.is_multisig():
            self.flash_text(
                t("Please load a wallet output descriptor"), theme.error_color
            )
            return MENU_CONTINUE

        submenu = Menu(
            self.ctx,
            [
                (t("Scan Address"), self.pre_scan_address),
                (t("Receive Addresses"), self.list_address_type),
                (t("Change Addresses"), lambda: self.list_address_type(1)),
                (t("Back"), lambda: None),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def list_address_type(self, addr_type=0):
        """Handler for the 'receive addresses' or 'change addresses' menu item"""
        # only show address for single-sig or multisig with wallet output descriptor loaded
        if self.ctx.wallet.is_loaded() or not self.ctx.wallet.is_multisig():
            loading_txt = t("Loading receive address %d..")
            if addr_type == 1:
                loading_txt = t("Loading change address %d..")

            max_addresses = self.ctx.display.max_menu_lines() - 3

            num_checked = 0
            while True:
                items = []
                if num_checked + 1 > max_addresses:
                    items.append(
                        (
                            "%d..%d" % (num_checked - max_addresses + 1, num_checked),
                            lambda: MENU_EXIT,
                        )
                    )

                for addr in self.ctx.wallet.obtain_addresses(
                    num_checked, limit=max_addresses, branch_index=addr_type
                ):
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(loading_txt % (num_checked + 1))

                    pos_str = str(num_checked + 1) + "." + " "  # thin space
                    qr_title = pos_str + addr
                    items.append(
                        (
                            self.fit_to_line(addr, pos_str, fixed_chars=3),
                            lambda address=addr, title=qr_title: self.show_address(
                                address, title
                            ),
                        )
                    )

                    num_checked += 1

                items.append(
                    (
                        "%d..%d" % (num_checked + 1, num_checked + max_addresses),
                        lambda: MENU_EXIT,
                    )
                )
                items.append((t("Back"), lambda: MENU_EXIT))

                submenu = Menu(self.ctx, items)
                stay_on_this_addr_menu = True
                while stay_on_this_addr_menu:
                    index, _ = submenu.run_loop()

                    # Back
                    if index == len(submenu.menu) - 1:
                        del submenu, items
                        gc.collect()
                        return MENU_CONTINUE
                    # Next
                    if index == len(submenu.menu) - 2:
                        stay_on_this_addr_menu = False
                    # Prev
                    if index == 0 and num_checked > max_addresses:
                        stay_on_this_addr_menu = False
                        num_checked -= 2 * max_addresses

        return MENU_CONTINUE

    def show_address(self, addr, title="", quick_exit=False):
        """Show addr provided as a QRCode"""
        from .qr_view import SeedQRView

        seed_qr_view = SeedQRView(self.ctx, data=addr, title=title)
        seed_qr_view.display_qr(
            allow_export=True, transcript_tools=False, quick_exit=quick_exit
        )
        return MENU_CONTINUE

    def pre_scan_address(self):
        """Handler for the 'scan address' menu item"""
        # only show address for single-sig or multisig with wallet output descriptor loaded
        if not self.ctx.wallet.is_loaded() and self.ctx.wallet.is_multisig():
            self.flash_text(
                t("Please load a wallet output descriptor"), theme.error_color
            )
            return MENU_CONTINUE

        submenu = Menu(
            self.ctx,
            [
                (t("Receive"), self.scan_address),
                (t("Change"), lambda: self.scan_address(1)),
                (t("Back"), lambda: MENU_EXIT),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def scan_address(self, addr_type=0):
        """Handler for the 'receive' or 'change' menu item"""
        data, qr_format = self.capture_qr_code()
        if data is None or qr_format != FORMAT_NONE:
            self.flash_text(t("Failed to load address"), theme.error_color)
            return MENU_CONTINUE

        addr = None
        try:
            from ..wallet import parse_address

            addr = parse_address(data)
        except:
            self.flash_text(t("Invalid address"), theme.error_color)
            return MENU_CONTINUE

        self.show_address(data, title=addr, quick_exit=True)

        if self.ctx.wallet.is_loaded() or not self.ctx.wallet.is_multisig():
            self.ctx.display.clear()
            if not self.prompt(
                t("Check that address belongs to this wallet?"),
                self.ctx.display.height() // 2,
            ):
                return MENU_CONTINUE

            checking_match_txt = t("Checking receive address %d for match..")
            checked_no_match_txt = t("Checked %d receive addresses with no matches.")
            is_valid_txt = t("%s\n\nis a valid receive address!")
            not_found_txt = t("%s\n\nwas NOT FOUND in the first %d receive addresses")
            if addr_type == 1:
                checking_match_txt = t("Checking change address %d for match..")
                checked_no_match_txt = t("Checked %d change addresses with no matches.")
                is_valid_txt = t("%s\n\nis a valid change address!")
                not_found_txt = t(
                    "%s\n\nwas NOT FOUND in the first %d change addresses"
                )

            found = False
            num_checked = 0
            while not found:
                for some_addr in self.ctx.wallet.obtain_addresses(
                    num_checked, limit=SCAN_ADDRESS_LIMIT, branch_index=addr_type
                ):
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(
                        checking_match_txt % (num_checked + 1)
                    )

                    num_checked += 1

                    found = addr == some_addr
                    if found:
                        break

                gc.collect()

                if not found:
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(
                        checked_no_match_txt % num_checked
                    )
                    if not self.prompt(
                        t("Try more?"), self.ctx.display.bottom_prompt_line
                    ):
                        break

            self.ctx.display.clear()
            result_message = (
                is_valid_txt % (str(num_checked) + ". \n\n" + addr)
                if found
                else not_found_txt % (addr, num_checked)
            )
            self.ctx.display.draw_centered_text(result_message)
            self.ctx.input.wait_for_button()
        return MENU_CONTINUE
