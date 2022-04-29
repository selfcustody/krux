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
from ..input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_TOUCH
from ..display import DEFAULT_PADDING, DEL, GO, ESC, FIXED_KEYS
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

    def wait_for_proceed(self, block=True):
        """Wrap acknowledgements which can be answared with multiple buttons"""
        return self.ctx.input.wait_for_button(block) in (BUTTON_ENTER, BUTTON_TOUCH)

    def _keypad_offset(self):
        return DEFAULT_PADDING + self.ctx.display.font_height * 3

    def _map_keys_array(self, width, height):
        """Maps an array of regions for keys to be placed in
        Returns horizontal and vertical spacing of keys
        """
        self.y_keypad_map = []
        self.x_keypad_map = []
        key_h_spacing = self.ctx.display.width() - DEFAULT_PADDING
        key_h_spacing //= width
        key_v_spacing = (
            self.ctx.display.height() - DEFAULT_PADDING - self._keypad_offset()
        )
        key_v_spacing //= height
        for y in range(height + 1):
            region = y * key_v_spacing + self._keypad_offset()
            self.y_keypad_map.append(region)
        for x in range(width + 1):
            region = x * key_h_spacing + DEFAULT_PADDING // 2
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
                    key = ESC
                elif key_index == len(keys) + 2:
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
                        # faded text
                        lcd.draw_string(key_offset_x, offset_y, key, lcd.LIGHTBLACK)
                    else:
                        if self.ctx.input.has_touch:
                            self.ctx.display.outline(
                                offset_x + 1,
                                y + 1,
                                key_h_spacing - 2,
                                key_v_spacing - 2,
                                lcd.DARKGREY,
                            )
                            lcd.draw_string(key_offset_x, offset_y, key, lcd.WHITE)
                        else:
                            lcd.draw_string(key_offset_x, offset_y, key, lcd.WHITE)
                    if key_index == cur_key_index and self.ctx.input.buttons_active:
                        if self.ctx.input.has_touch:
                            self.ctx.display.outline(
                                offset_x + 1,
                                y + 1,
                                key_h_spacing - 2,
                                key_v_spacing - 2,
                            )
                        else:
                            self.ctx.display.outline(
                                offset_x - 2, y, key_h_spacing + 1, key_v_spacing - 1
                            )
                key_index += 1

    def _get_valid_index(self, cur_key_index, keys, possible_keys, moving_forward):
        while cur_key_index < len(keys) and keys[cur_key_index] not in possible_keys:
            if moving_forward:
                cur_key_index = (cur_key_index + 1) % (len(keys) + FIXED_KEYS)
            else:
                if cur_key_index:
                    cur_key_index -= 1
                else:
                    cur_key_index = len(keys) + FIXED_KEYS - 1
        return cur_key_index

    def capture_from_keypad(
        self, title, keys, autocomplete_fn=None, possible_keys_fn=None
    ):
        """Displays a key pad and captures a series of keys until the user returns.
        Returns a string.
        """
        pad_width = math.floor(math.sqrt(len(keys) + FIXED_KEYS))
        pad_height = math.ceil((len(keys) + FIXED_KEYS) / pad_width)
        key_h_spacing, key_v_spacing = self._map_keys_array(pad_width, pad_height)
        buffer = ""
        cur_key_index = 0
        moving_forward = True
        go_position = len(keys) + 2
        while True:
            self.ctx.display.clear()
            offset_y = DEFAULT_PADDING
            self.ctx.display.draw_hcentered_text(title, offset_y)
            offset_y += self.ctx.display.font_height * 3 // 2
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
                    self.ctx.input.buttons_active = False
                    if self.ctx.input.touch.index < len(keys):
                        cur_key_index = self.ctx.input.touch.index
                        if keys[cur_key_index] in possible_keys:
                            btn = BUTTON_ENTER
                        else:
                            btn = BUTTON_PAGE
                    elif self.ctx.input.touch.index < len(keys) + FIXED_KEYS:
                        cur_key_index = self.ctx.input.touch.index
                        btn = BUTTON_ENTER
                    else:
                        btn = BUTTON_PAGE
            if btn == BUTTON_ENTER:
                changed = False
                if cur_key_index == len(keys):
                    buffer = buffer[: len(buffer) - 1]
                    changed = True
                elif cur_key_index == len(keys) + 1:
                    return MENU_CONTINUE
                elif cur_key_index == go_position:
                    break
                else:
                    buffer += keys[cur_key_index]
                    changed = True

                    # Don't autocomplete if deleting
                    if changed and autocomplete_fn is not None:
                        new_buffer = autocomplete_fn(buffer)
                        if new_buffer is not None:
                            buffer = new_buffer
                            cur_key_index = go_position

                    # moves index to Go on dice presses
                    if len(buffer) > 0 and (len(keys) == 6 or len(keys) == 20):
                        cur_key_index = go_position

            elif btn == BUTTON_PAGE:
                moving_forward = True
                cur_key_index = (cur_key_index + 1) % (len(keys) + FIXED_KEYS)
            elif btn == BUTTON_PAGE_PREV:
                moving_forward = False
                cur_key_index = (cur_key_index - 1) % (len(keys) + FIXED_KEYS)
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
            if self.wait_for_proceed(block=num_parts == 1):
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
        if self.wait_for_proceed():
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
        """Prompts user to answer Yes or No"""
        # Go up if question has multiple lines
        offset_y -= (
            len(self.ctx.display.to_lines(text)) - 1
        ) * self.ctx.display.font_height
        self.ctx.display.draw_hcentered_text(text, offset_y)
        if self.ctx.input.has_touch:
            self.ctx.input.touch.clear_regions()
            offset_y += (
                len(self.ctx.display.to_lines(text)) * self.ctx.display.font_height
                + DEFAULT_PADDING
            )

            self.ctx.input.touch.add_y_delimiter(offset_y)
            lcd.fill_rectangle(
                0,
                offset_y,
                self.ctx.display.width(),
                1,
                lcd.DARKGREY,
            )
            self.ctx.display.draw_hcentered_text(
                t("Yes"), offset_y + self.ctx.display.font_height // 2, lcd.WHITE
            )
            offset_y += 2 * self.ctx.display.font_height
            self.ctx.input.touch.add_y_delimiter(offset_y)
            lcd.fill_rectangle(
                0,
                offset_y,
                self.ctx.display.width(),
                1,
                lcd.DARKGREY,
            )
            self.ctx.display.draw_hcentered_text(
                t("No"), offset_y + self.ctx.display.font_height // 2, lcd.WHITE
            )
            offset_y += 2 * self.ctx.display.font_height
            self.ctx.input.touch.add_y_delimiter(offset_y)
            lcd.fill_rectangle(
                0,
                offset_y,
                self.ctx.display.width(),
                1,
                lcd.DARKGREY,
            )
        btn = self.ctx.input.wait_for_button()
        if self.ctx.input.has_touch:
            self.ctx.input.touch.clear_regions()
            if btn == BUTTON_TOUCH:
                # index 0 = Yes = ENTER
                # index 1 = No = PAGE
                btn = self.ctx.input.touch.index
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
            if self.ctx.input.has_touch:
                self._draw_touch_menu(selected_item_index)
            else:
                self._draw_menu(selected_item_index)

            btn = self.ctx.input.wait_for_button(block=True)
            if self.ctx.input.has_touch:
                if btn == BUTTON_TOUCH:
                    self.ctx.input.buttons_active = False
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
            elif btn == BUTTON_PAGE_PREV:
                if selected_item_index == 0:
                    selected_item_index = len(self.menu) - 1
                else:
                    selected_item_index = selected_item_index - 1

    def _draw_touch_menu(self, selected_item_index):
        # map regions with dynamic height to fill screen
        self.ctx.input.touch.clear_regions()
        offset_y = 0
        Page.y_keypad_map = [offset_y]
        for menu_item in self.menu:
            offset_y += len(self.ctx.display.to_lines(menu_item[0])) + 1
            Page.y_keypad_map.append(offset_y)
        height_multiplier = self.ctx.display.height() - 2 * DEFAULT_PADDING
        height_multiplier //= offset_y
        for n in Page.y_keypad_map:
            self.ctx.input.touch.add_y_delimiter(
                n * height_multiplier + DEFAULT_PADDING
            )

        # draw dividers and outline
        for i, y in enumerate(self.ctx.input.touch.y_regions[:-1]):
            if i and not self.ctx.input.buttons_active:
                lcd.fill_rectangle(0, y, self.ctx.display.width(), 1, lcd.DARKGREY)
            height = self.ctx.input.touch.y_regions[i + 1] - y
            if selected_item_index == i and self.ctx.input.buttons_active:
                self.ctx.display.outline(
                    DEFAULT_PADDING - 1,
                    y + 1,
                    self.ctx.display.usable_width(),
                    height - 2,
                )

        # draw centralized strings in regions
        for i, menu_item in enumerate(self.menu):
            menu_item_lines = self.ctx.display.to_lines(menu_item[0])
            offset_y = (
                self.ctx.input.touch.y_regions[i + 1]
                - self.ctx.input.touch.y_regions[i]
            )
            offset_y -= len(menu_item_lines) * self.ctx.display.font_height
            offset_y //= 2
            offset_y += self.ctx.input.touch.y_regions[i]
            for j, text in enumerate(menu_item_lines):
                self.ctx.display.draw_hcentered_text(
                    text, offset_y + self.ctx.display.font_height * j
                )

    def _draw_menu(self, selected_item_index):
        offset_y = len(self.menu) * self.ctx.display.font_height * 2
        offset_y = self.ctx.display.height() - offset_y
        offset_y //= 2
        for i, menu_item in enumerate(self.menu):
            menu_item_lines = self.ctx.display.to_lines(menu_item[0])
            delta_y = (len(menu_item_lines) + 1) * self.ctx.display.font_height
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
