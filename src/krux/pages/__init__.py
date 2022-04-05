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
import gc
import math
import time
import lcd
import board
from ur.ur import UR
from ..input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PREVIOUS, BUTTON_TOUCH
from ..display import DEFAULT_PADDING, DEL, GO, BUTTON_HEIGHT
from ..qr import to_qr_codes
from ..i18n import t

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
        # context has its own keypad mapping in case touch is not used
        self.y_keypad_map = []
        self.x_keypad_map = []

    def _keypad_offset(self):
        return DEFAULT_PADDING + self.ctx.display.font_height * 3

    def _map_keys_array(self, width, height):
        """Maps an arry of regions for keys to be placed in
        Returns horizontal and vertican spacing of keys
        """
        self.y_keypad_map = []
        self.x_keypad_map = []
        key_h_spacing = self.ctx.display.usable_width() // width
        key_v_spacing = BUTTON_HEIGHT  # later could be more dinamic
        for y in range(height + 1):
            region = y * key_v_spacing + self._keypad_offset()
            region -= self.ctx.display.font_height // 2
            self.y_keypad_map.append(region)
        for x in range(width + 1):
            region = x * key_h_spacing + DEFAULT_PADDING
            self.x_keypad_map.append(region)
        if self.ctx.input.has_touch:
            self.ctx.input.touch.y_regions = self.y_keypad_map
            self.ctx.input.touch.x_regions = self.x_keypad_map
        return key_h_spacing, key_v_spacing

    def _draw_keys(
        self, key_h_spacing, key_v_spacing, keys, possible_keys, cur_key_index
    ):
        key_index = 0
        for y in self.y_keypad_map[:-1]:
            offset_y = y + (key_v_spacing - self.ctx.display.font_height) // 2
            for x in self.x_keypad_map[:-1]:
                key = None
                if key_index < len(keys):
                    key = keys[key_index]
                elif key_index == len(keys):
                    key = DEL
                elif key_index == len(keys) + 1:
                    key = GO
                if key is not None:
                    offset_x = x
                    if board.config["lcd"]["invert"]:  # inverted X coodinates
                        offset_x = self.ctx.display.width() - offset_x
                        offset_x -= key_h_spacing
                    key_offset_x = (
                        key_h_spacing - len(key) * self.ctx.display.font_width
                    ) // 2
                    key_offset_x += offset_x
                    if key_index < len(keys) and keys[key_index] not in possible_keys:

                        lcd.draw_string(key_offset_x, offset_y, key, 0x0842)
                    else:
                        if self.ctx.input.has_touch:
                            lcd.fill_rectangle(
                                offset_x,
                                y,
                                key_h_spacing - 1,
                                key_v_spacing - 1,
                                lcd.DARKGREY,
                            )
                            lcd.draw_string(
                                key_offset_x, offset_y, key, lcd.WHITE, lcd.DARKGREY
                            )
                        else:
                            lcd.draw_string(key_offset_x, offset_y, key, lcd.WHITE)
                    if key_index == cur_key_index:
                        self.ctx.display.outline(
                            offset_x,
                            y,
                            key_h_spacing - 1,
                            key_v_spacing - 1,
                        )
                key_index += 1

    def _get_valid_index(self, cur_key_index, keys, possible_keys, moving_forward):
        while cur_key_index < len(keys) and keys[cur_key_index] not in possible_keys:
            if moving_forward:
                cur_key_index = (cur_key_index + 1) % (len(keys) + 2)
            else:
                if cur_key_index:
                    cur_key_index -= 1
                else:
                    cur_key_index = len(keys) + 1
        return cur_key_index

    def capture_from_keypad(
        self, title, keys, autocomplete_fn=None, possible_keys_fn=None
    ):
        """Displays a key pad and captures a series of keys until the user returns.
        Returns a string.
        """
        pad_width = math.floor(math.sqrt(len(keys) + 2))
        pad_height = math.ceil((len(keys) + 2) / pad_width)
        key_h_spacing, key_v_spacing = self._map_keys_array(pad_width, pad_height)
        buffer = ""
        cur_key_index = 0
        moving_forward = True
        while True:
            self.ctx.display.clear()
            offset_y = DEFAULT_PADDING
            self.ctx.display.draw_hcentered_text(title, offset_y)
            offset_y += self.ctx.display.font_height
            self.ctx.display.draw_hcentered_text(buffer, offset_y)
            offset_y = self._keypad_offset()
            possible_keys = keys
            if possible_keys_fn is not None:
                possible_keys = possible_keys_fn(buffer)
            cur_key_index = self._get_valid_index(
                cur_key_index, keys, possible_keys, moving_forward
            )
            self._draw_keys(
                key_h_spacing, key_v_spacing, keys, possible_keys, cur_key_index
            )

            btn = self.ctx.input.wait_for_button()
            if self.ctx.input.has_touch:
                if btn == BUTTON_TOUCH:
                    if self.ctx.input.touch.index < len(keys):
                        cur_key_index = self.ctx.input.touch.index
                        if keys[cur_key_index] in possible_keys:
                            btn = BUTTON_ENTER
                        else:
                            btn = BUTTON_PAGE
                    elif self.ctx.input.touch.index < len(keys) + 2:
                        cur_key_index = self.ctx.input.touch.index
                        btn = BUTTON_ENTER
                    else:
                        btn = BUTTON_PAGE
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
                if changed and autocomplete_fn is not None:
                    new_buffer = autocomplete_fn(buffer)
                    if new_buffer is not None:
                        buffer = new_buffer
                        cur_key_index = len(keys) + 1
            elif btn == BUTTON_PAGE:
                moving_forward = True
                cur_key_index = (cur_key_index + 1) % (len(keys) + 2)
            elif btn == BUTTON_PREVIOUS:
                moving_forward = False
                cur_key_index = (cur_key_index - 1) % (len(keys) + 2)
        if self.ctx.input.has_touch:
            self.ctx.input.touch.clear_regions()
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

    def display_qr_codes(self, data, qr_format, title=None):
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
            offset_y = self.ctx.display.qr_offset()
            if title is not None:
                offset_y += self.ctx.display.font_height
            self.ctx.display.draw_hcentered_text(subtitle, offset_y, color=lcd.WHITE)
            i = (i + 1) % num_parts
            btn = self.ctx.input.wait_for_button(block=num_parts == 1)
            if btn in (BUTTON_ENTER, BUTTON_TOUCH):
                done = True
            # interval done in input.py using timers

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
            offset_y = 40 + (i * self.ctx.display.font_height)
            if board.config["lcd"]["invert"]:
                offset_x = self.ctx.display.width() - DEFAULT_PADDING
                offset_x -= len(word) * self.ctx.display.font_width
            else:
                offset_x = DEFAULT_PADDING
            lcd.draw_string(offset_x, offset_y, word, lcd.WHITE, lcd.BLACK)
        if len(word_list) > 12:
            self.ctx.input.wait_for_button()
            self.ctx.display.clear()
            self.ctx.display.draw_hcentered_text(t("BIP39 Mnemonic"))
            for i, word in enumerate(word_list[12:]):
                offset_y = 40 + (i * self.ctx.display.font_height)
                if board.config["lcd"]["invert"]:
                    offset_x = self.ctx.display.width() - DEFAULT_PADDING
                    offset_x -= len(word) * self.ctx.display.font_width
                else:
                    offset_x = DEFAULT_PADDING
                lcd.draw_string(offset_x, offset_y, word, lcd.WHITE, lcd.BLACK)

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
        if btn in (BUTTON_ENTER, BUTTON_TOUCH):
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

    def prompt(self, text, offset_y=0):
        """Prompts user to answaer Yes or No"""
        self.ctx.display.draw_hcentered_text(text, offset_y)
        if self.ctx.input.has_touch:
            self.ctx.input.touch.clear_regions()
            offset_y += (
                len(self.ctx.display.to_lines(text)) * self.ctx.display.font_height
            )
            self.ctx.input.touch.add_y_delimiter(offset_y)
            self.ctx.display.draw_touch_button(t("No"), offset_y)
            offset_y += 2 * self.ctx.display.font_height
            self.ctx.input.touch.add_y_delimiter(offset_y)
            self.ctx.display.draw_touch_button(t("Yes"), offset_y)
            offset_y += 2 * self.ctx.display.font_height
            self.ctx.input.touch.add_y_delimiter(offset_y)
        btn = self.ctx.input.wait_for_button()
        if self.ctx.input.has_touch:
            self.ctx.input.touch.clear_regions()
            if btn == BUTTON_TOUCH:
                if self.ctx.input.touch.index:  # index 1 = Yes = ENTER
                    btn = BUTTON_ENTER
                else:  # index 0 = No = PAGE
                    btn = BUTTON_PAGE
        return btn

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
            gc.collect()
            self.ctx.display.clear()
            self._draw_menu(selected_item_index)

            btn = self.ctx.input.wait_for_button(block=True)
            if self.ctx.input.has_touch:
                if btn == BUTTON_TOUCH:
                    selected_item_index = self.ctx.input.touch.index
                    btn = BUTTON_ENTER
                self.ctx.input.touch.clear_regions()
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
            elif btn == BUTTON_PAGE:
                selected_item_index = (selected_item_index + 1) % len(self.menu)
            elif btn == BUTTON_PREVIOUS:
                if selected_item_index == 0:
                    selected_item_index = len(self.menu) - 1
                else:
                    selected_item_index = selected_item_index - 1

    def _draw_menu(self, selected_item_index):
        offset_y = len(self.menu) * self.ctx.display.font_height * 2
        offset_y = self.ctx.display.height() - offset_y
        offset_y //= 2
        if self.ctx.input.has_touch:
            self.ctx.input.touch.clear_regions()
            self.ctx.input.touch.add_y_delimiter(offset_y)
        for i, menu_item in enumerate(self.menu):
            menu_item_lines = self.ctx.display.to_lines(menu_item[0])
            delta_y = (len(menu_item_lines) + 1) * self.ctx.display.font_height
            if self.ctx.input.has_touch:
                self.ctx.display.draw_touch_button(menu_item_lines, offset_y)
                self.ctx.input.touch.add_y_delimiter(offset_y + delta_y)
            else:
                for j, text in enumerate(menu_item_lines):
                    self.ctx.display.draw_hcentered_text(
                        text,
                        offset_y
                        + self.ctx.display.font_height // 2
                        + self.ctx.display.font_height * j,
                    )
            if selected_item_index == i:
                self.ctx.display.outline(
                    DEFAULT_PADDING,
                    offset_y + 1,
                    self.ctx.display.usable_width(),
                    delta_y - 2,
                )
            offset_y += delta_y
