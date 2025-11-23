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
from ...display import BOTTOM_PROMPT_LINE
from ...krux_settings import t
from ...settings import THIN_SPACE
from ...qr import FORMAT_NONE
from .. import (
    Page,
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
    ESC_KEY,
)
from ...format import format_address

SCAN_ADDRESS_LIMIT = 50
EXPORT_ADDRESS_LIMIT = SCAN_ADDRESS_LIMIT * 100


class Addresses(Page):
    """UI to show and scan wallet addresses"""

    def addresses_menu(self):
        """Handler for the 'address' menu item"""
        # only show address for single-sig or multisig with wallet output descriptor loaded
        if not self.ctx.wallet.is_loaded() and (
            self.ctx.wallet.is_multisig() or self.ctx.wallet.is_miniscript()
        ):
            self.flash_error(t("Please load a wallet output descriptor"))
            return MENU_CONTINUE

        submenu = Menu(
            self.ctx,
            [
                (
                    t("Scan Address"),
                    lambda: self._receive_change_menu(self.scan_address),
                ),
                (
                    t("List Addresses"),
                    lambda: self._receive_change_menu(self.list_address_type),
                ),
                (
                    t("Export Addresses"),
                    (
                        None
                        if not self.has_sd_card()
                        else lambda: self._receive_change_menu(self.export_address)
                    ),
                ),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def list_address_type(self, addr_type=0):
        """Handler for the 'receive addresses' or 'change addresses' menu item"""
        if not self.ctx.wallet.is_loaded() and (
            self.ctx.wallet.is_multisig() or self.ctx.wallet.is_miniscript()
        ):
            self.flash_error(t("Please load a wallet output descriptor"))
            return MENU_CONTINUE

        loading_txt = (
            t("Loading change addresses…")
            if addr_type == 1
            else t("Loading receive addresses…")
        )
        max_addresses = self.ctx.display.max_menu_lines() - 3
        address_index = 0
        while True:
            items = []
            if address_index >= max_addresses:
                items.append(
                    (
                        "%d…%d" % (address_index - max_addresses, address_index - 1),
                        lambda: MENU_EXIT,
                    )
                )

            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(loading_txt)
            addresses = self.ctx.wallet.obtain_addresses(
                address_index, limit=max_addresses, branch_index=addr_type
            )
            for addr in addresses:
                pos_str = str(address_index) + "." + THIN_SPACE
                qr_title = pos_str + format_address(addr)
                items.append(
                    (
                        self.fit_to_line(addr, pos_str, fixed_chars=3),
                        lambda address=addr, title=qr_title: self.show_address(
                            address, title
                        ),
                    )
                )
                address_index += 1

            items.append(
                (
                    "%d…%d" % (address_index, address_index + max_addresses - 1),
                    lambda: MENU_EXIT,
                )
            )

            submenu = Menu(self.ctx, items)
            stay_on_this_addr_menu = True
            while stay_on_this_addr_menu:
                next_index = len(submenu.menu) - 2
                prev_index = 0 if address_index > max_addresses else -1
                index, _ = submenu.run_loop(
                    swipe_up_fnc=lambda: (next_index, MENU_EXIT),
                    swipe_down_fnc=lambda: (prev_index, MENU_EXIT),
                )

                if index == submenu.back_index:  # Back
                    del submenu, items
                    gc.collect()
                    return MENU_CONTINUE
                if index == next_index:  # Next
                    stay_on_this_addr_menu = False
                if index == 0 and address_index > max_addresses:  # Prev
                    stay_on_this_addr_menu = False
                    address_index -= 2 * max_addresses

    def _qr_highlight_addr(self, formatted_text, y_offset):
        """Case highlight address for QR"""

        from ..utils import Utils

        utils = Utils(self.ctx)

        first_line_prefix = "." + THIN_SPACE
        lines = self.ctx.display.to_lines(formatted_text)
        highlight_state = True
        for i, line in enumerate(lines):
            x_offset = self.ctx.display.get_center_offset_x(line)
            addr_prefix = None
            # case for addr with index prefix
            if i == 0 and first_line_prefix in line:
                addr_prefix = line[: line.find(first_line_prefix)] + first_line_prefix

            highlight_state = utils.display_addr_highlighted(
                y_offset, x_offset, line, i, highlight_state, addr_prefix
            )

    def show_address(self, addr, title="", quick_exit=False):
        """Show addr provided as a QRCode"""
        from ..qr_view import SeedQRView

        seed_qr_view = SeedQRView(self.ctx, data=addr, title=title)
        seed_qr_view.display_qr(
            allow_export=True,
            transcript_tools=False,
            quick_exit=quick_exit,
            highlight_function=self._qr_highlight_addr,
        )

        return MENU_CONTINUE

    def _receive_change_menu(self, callback):
        submenu = Menu(
            self.ctx,
            [
                (t("Receive"), callback),
                (
                    t("Change"),
                    (
                        None
                        if not self.ctx.wallet.has_change_addr()
                        else lambda: callback(1)
                    ),
                ),
            ],
        )
        submenu.run_loop()
        return MENU_CONTINUE

    def export_address(self, addr_type=0):
        """Allow user to export addresses to SD card"""
        from ..utils import Utils
        from ...sd_card import SDHandler, ADDRESSES_FILE_EXTENSION
        from ..file_operations import SaveFile
        from ...wdt import wdt

        utils = Utils(self.ctx)

        start_address = ""
        while start_address == "":
            start_address = utils.capture_index_from_keypad(t("Index"), initial_val=0)
        if start_address is None:
            return

        quantity = ""
        while quantity == "":
            quantity = utils.capture_index_from_keypad(
                t("Quantity"),
                initial_val=SCAN_ADDRESS_LIMIT,
                range_min=1,
                range_max=EXPORT_ADDRESS_LIMIT,
            )
        if quantity is None:
            return

        default_filename = "Receive" if addr_type == 0 else "Change"
        default_filename += "-" + self.ctx.wallet.key.fingerprint_hex_str()
        save_page = SaveFile(self.ctx)
        filename = save_page.set_filename(
            default_filename,
            file_extension=ADDRESSES_FILE_EXTENSION,
        )
        if filename == ESC_KEY:
            return

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing…"))

        try:
            with SDHandler():
                with open(SDHandler.PATH_STR % filename, "w") as file:
                    i = start_address
                    for addr in self.ctx.wallet.obtain_addresses(
                        start_address, limit=quantity, branch_index=addr_type
                    ):
                        file.write(str(i) + "," + addr + "\n")
                        i += 1

                        if i % SCAN_ADDRESS_LIMIT == 0:
                            self.ctx.display.clear()
                            self.ctx.display.draw_centered_text(
                                t("Processing…")
                                + "\n\n%d%%" % int((i - start_address) / quantity * 100)
                            )
                            wdt.feed()

                self.flash_text(
                    t("Saved to SD card:") + "\n\n%s" % filename,
                    highlight_prefix=":",
                )
        except OSError:
            self.flash_text(t("SD card not detected."))

    def _scan_highlight_addr(self, result_message):
        """Case highlight address for scan"""
        from ..utils import Utils

        utils = Utils(self.ctx)

        lines = self.ctx.display.to_lines(result_message)
        y_offset = self.ctx.display.get_center_offset_y(len(lines))
        highlight = True
        count_empty = 0
        addr_highlighted = False
        for i, line in enumerate(lines):
            if len(line) > 0:
                if (count_empty == 0 and "." not in line) or count_empty == 1:
                    x_offset = self.ctx.display.get_center_offset_x(line)
                    highlight = utils.display_addr_highlighted(
                        y_offset, x_offset, line, i, highlight
                    )
                    addr_highlighted = True
            else:
                count_empty += 1
                if addr_highlighted:
                    break

    def scan_address(self, addr_type=0):
        """Handler for the 'receive' or 'change' menu item"""
        from ..qr_capture import QRCodeCapture
        from ..encryption_ui import decrypt_kef

        qr_capture = QRCodeCapture(self.ctx)
        data, qr_format = qr_capture.qr_capture_loop()
        if data is None or qr_format != FORMAT_NONE:
            self.flash_error(t("Failed to load"))
            return MENU_CONTINUE

        try:
            data = decrypt_kef(self.ctx, data)

            # Cpython raises UnicodeDecodeError, MaixPy raises TypeError
            try:
                data = data.decode()
            except:
                self.flash_error(t("Failed to load"))
                return MENU_CONTINUE
        except KeyError:
            self.flash_error(t("Failed to decrypt"))
            return MENU_CONTINUE
        except ValueError:
            # ValueError=not KEF or declined to decrypt
            pass

        addr = None
        try:
            from ...wallet import parse_address

            addr = parse_address(data)
        except:
            self.flash_error(t("Invalid address"))
            return MENU_CONTINUE

        self.show_address(data, title=format_address(addr), quick_exit=True)

        if self.ctx.wallet.is_loaded() or not self.ctx.wallet.is_multisig():
            self.ctx.display.clear()
            if not self.prompt(
                t("Check that address belongs to this wallet?"),
                self.ctx.display.height() // 2,
            ):
                return MENU_CONTINUE

            checking_match_txt = t("Verifying…") + " " + t("%d to %d")
            checked_no_match_txt = t("Checked %d addresses with no matches.")
            is_valid_txt = "%s\n\n" + t("is a valid address!")
            not_found_txt = "%s\n\n" + t("was NOT FOUND in the first %d addresses")

            found = False
            num_checked = 0
            while not found:
                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(
                    checking_match_txt
                    % (num_checked, num_checked + SCAN_ADDRESS_LIMIT - 1)
                )
                for some_addr in self.ctx.wallet.obtain_addresses(
                    num_checked, limit=SCAN_ADDRESS_LIMIT, branch_index=addr_type
                ):
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
                    if not self.prompt(t("Try more?"), BOTTOM_PROMPT_LINE):
                        break

            self.ctx.display.clear()
            result_message = (
                is_valid_txt % (str(num_checked - 1) + ".\n\n" + format_address(addr))
                if found
                else not_found_txt % (format_address(addr), num_checked)
            )
            self.ctx.display.draw_centered_text(result_message)
            self._scan_highlight_addr(result_message)
            self.ctx.input.wait_for_button()
        return MENU_CONTINUE
