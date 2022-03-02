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
import math
import time
import lcd
from ur.ur import UR
from ..input import BUTTON_ENTER, BUTTON_PAGE
from ..display import DEFAULT_PADDING, DEL, GO
from ..qr import to_qr_codes
from ..i18n import t

QR_ANIMATION_INTERVAL_MS = 100

MENU_CONTINUE = 0
MENU_EXIT = 1
MENU_SHUTDOWN = 2


class Page:
    """Represents a page in the app, with helper methods for common display and
    input operations.

    Must be subclassed.
    """

    def __init__(self, ctx, menu):
        self.ctx = ctx
        self.menu = menu
        self._enter_state = -1
        self._page_state = -1

    def capture_from_keypad(self, title, keys, autocomplete=None, possible_letters=None):
        """Displays a key pad and captures a series of keys until the user returns.
        Returns a string.
        """
        pad_width = math.floor(math.sqrt(len(keys) + 2))
        pad_height = math.ceil((len(keys) + 2) / pad_width)

        buffer = ""
        cur_key_index = 0
        valid_letters = keys
        while True:
            self.ctx.display.clear()
            self.ctx.display.draw_hcentered_text(title)
            self.ctx.display.draw_hcentered_text(buffer, 45)

            for y in range(pad_height):
                row_keys = ""
                for x in range(pad_width):
                    key_index = x + y * pad_width
                    key = None
                    if key_index < len(keys):
                        if keys[key_index] in valid_letters:
                            key = keys[key_index]
                        else:
                            key = '_'
                    elif key_index == len(keys):
                        key = DEL
                    elif key_index == len(keys) + 1:
                        key = GO
                    if key is not None:
                        if len(key) == 1:
                            row_keys += (
                                " >" + key if key_index == cur_key_index else "  " + key
                            )
                        else:
                            row_keys += (
                                ">" + key if key_index == cur_key_index else " " + key
                            )
                offset_y = 80 + y * self.ctx.display.font_size * 4
                self.ctx.display.draw_hcentered_text(row_keys, offset_y)

            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_ENTER:
                changed = False
                if cur_key_index == len(keys) + 1:  # Enter
                    break
                if cur_key_index == len(keys):  # Del
                    buffer = buffer[: len(buffer) - 1]
                    changed = True
                else:
                    buffer += keys[cur_key_index]
                    changed = True
                if changed and autocomplete is not None:
                    new_buffer = autocomplete(buffer)
                    if new_buffer is not None:
                        buffer = new_buffer
                        cur_key_index = len(keys) + 1
                valid_letters = possible_letters(buffer)
            elif btn == BUTTON_PAGE:
                cur_key_index = (cur_key_index + 1) % (len(keys) + 2)
            in_deactivated_key = True
            while in_deactivated_key:
                if cur_key_index >= len(keys):
                    in_deactivated_key = False
                else:
                    if keys[cur_key_index] in valid_letters:
                        in_deactivated_key = False
                    else:
                        cur_key_index = (cur_key_index + 1) % (len(keys) + 2)


        return buffer

    def capture_qr_code(self):
        """Captures a singular or animated series of QR codes and displays progress to the user.
        Returns the contents of the QR code(s).
        """
        self._enter_state = -1
        self._page_state = -1

        def callback(part_total, num_parts_captured, new_part):
            # Turn on the light as long as the enter button is held down
            if self._enter_state == -1:
                self._enter_state = self.ctx.input.enter.value()
            elif self.ctx.input.enter.value() != self._enter_state:
                self._enter_state = self.ctx.input.enter.value()
                if self.ctx.light:
                    self.ctx.light.toggle()

            # Exit the capture loop if the page button is pressed
            if self._page_state == -1:
                self._page_state = self.ctx.input.page.value()
            elif self.ctx.input.page.value() != self._page_state:
                return True

            # Indicate progress to the user that a new part was captured
            if new_part:
                self.ctx.display.to_portrait()
                self.ctx.display.draw_centered_text(
                    "%.0f%%" % (100 * float(num_parts_captured) / float(part_total))
                )
                time.sleep_ms(100)
                self.ctx.display.to_landscape()

            return False

        self.ctx.display.to_landscape()
        code = None
        qr_format = None
        try:
            code, qr_format = self.ctx.camera.capture_qr_code_loop(callback)
        except:
            self.ctx.log.exception("Exception occurred capturing QR code")
        if self.ctx.light:
            self.ctx.light.turn_off()
        self.ctx.display.to_portrait()
        if code is not None:
            data = code.cbor if isinstance(code, UR) else code
            self.ctx.log.debug(
                'Captured QR Code in format "%d": %s' % (qr_format, data)
            )
        return (code, qr_format)

    def display_qr_codes(
        self, data, qr_format, title=None, title_padding=DEFAULT_PADDING
    ):
        """Displays a QR code or an animated series of QR codes to the user, encoding them
        in the specified format
        """
        done = False
        i = 0
        code_generator = to_qr_codes(data, self.ctx.display.qr_data_width(), qr_format)
        while not done:
            self.ctx.display.clear()

            code = None
            num_parts = 0
            try:
                code, num_parts = next(code_generator)
            except:
                code_generator = to_qr_codes(
                    data, self.ctx.display.qr_data_width(), qr_format
                )
                code, num_parts = next(code_generator)
            self.ctx.display.draw_qr_code(5, code)
            subtitle = (
                t("Part\n%d / %d") % (i + 1, num_parts) if title is None else title
            )
            offset_y = 175 if title is None else 138
            self.ctx.display.draw_hcentered_text(
                subtitle, offset_y=offset_y, color=lcd.WHITE, padding=title_padding
            )
            i = (i + 1) % num_parts
            btn = self.ctx.input.wait_for_button(block=num_parts == 1)
            done = btn == BUTTON_ENTER
            if not done:
                time.sleep_ms(QR_ANIMATION_INTERVAL_MS)

    def display_mnemonic(self, mnemonic):
        """Displays the 12 or 24-word list of words to the user"""
        words = mnemonic.split(" ")
        word_list = [
            str(i + 1) + "." + ("  " if i + 1 < 10 else " ") + word
            for i, word in enumerate(words)
        ]
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(t("BIP39 Mnemonic"))
        for i, word in enumerate(word_list[:12]):
            offset_y = 40 + (i * self.ctx.display.line_height())
            lcd.draw_string(DEFAULT_PADDING, offset_y, word, lcd.WHITE, lcd.BLACK)
        if len(word_list) > 12:
            self.ctx.input.wait_for_button()
            self.ctx.display.clear()
            self.ctx.display.draw_hcentered_text(t("BIP39 Mnemonic"))
            for i, word in enumerate(word_list[12:]):
                offset_y = 40 + (i * self.ctx.display.line_height())
                lcd.draw_string(DEFAULT_PADDING, offset_y, word, lcd.WHITE, lcd.BLACK)

    def print_qr_prompt(self, data, qr_format):
        """Prompts the user to print a QR code in the specified format
        if a printer is connected
        """
        if self.ctx.printer is None:
            return
        self.ctx.display.clear()
        time.sleep_ms(1000)
        self.ctx.display.draw_centered_text(t("Print to QR?"))
        btn = self.ctx.input.wait_for_button()
        if btn == BUTTON_ENTER:
            i = 0
            for qr_code, count in to_qr_codes(
                data, self.ctx.printer.qr_data_width(), qr_format
            ):
                if i == count:
                    break
                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(
                    t("Printing\n%d / %d") % (i + 1, count)
                )
                self.ctx.printer.print_qr_code(qr_code)
                i += 1

    def shutdown(self):
        """Handler for the 'shutdown' menu item"""
        return MENU_SHUTDOWN

    def run(self):
        """Runs the page's menu loop"""
        _, status = self.menu.run_loop()
        return status != MENU_SHUTDOWN


class Menu:
    """Represents a menu that can render itself to the screen, handle item selection,
    and invoke menu item callbacks that return a status
    """

    def __init__(self, ctx, menu):
        self.ctx = ctx
        self.menu = menu

    def run_loop(self):
        """Runs the menu loop until one of the menu items returns either a MENU_EXIT
        or MENU_SHUTDOWN status
        """
        selected_item_index = 0
        while True:
            self.ctx.display.clear()
            self._draw_menu(selected_item_index)

            btn = self.ctx.input.wait_for_button(block=True)
            if btn == BUTTON_ENTER:
                try:
                    self.ctx.display.clear()
                    status = self.menu[selected_item_index][1]()
                    if status != MENU_CONTINUE:
                        return (selected_item_index, status)
                except Exception as e:
                    self.ctx.log.exception(
                        'Exception occurred in menu item "%s"'
                        % self.menu[selected_item_index][0]
                    )
                    self.ctx.display.clear()
                    self.ctx.display.draw_centered_text(
                        t("Error:\n%s") % repr(e), lcd.RED
                    )
                    self.ctx.input.wait_for_button()
            else:
                selected_item_index = (selected_item_index + 1) % len(self.menu)

    def _draw_menu(self, selected_item_index):
        menu_list = []
        for i, menu_item in enumerate(self.menu):
            menu_item_lines = self.ctx.display.to_lines(menu_item[0])
            if selected_item_index == i:
                selected_line = "- %s -" % menu_item_lines[0]
                if len(self.ctx.display.to_lines(selected_line)) > 1:
                    selected_line = "-%s-" % menu_item_lines[0]
                menu_item_lines[0] = selected_line
            menu_list_item = menu_item_lines[0]
            if len(menu_item_lines) > 1:
                menu_list_item += "\n" + "\n".join(menu_item_lines[1:])
            menu_list.append(menu_list_item)
        self.ctx.display.draw_centered_text(
            "\n\n".join(menu_list).split("\n"), color=lcd.WHITE
        )
