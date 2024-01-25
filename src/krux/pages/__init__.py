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
import math
import time
import board
from .keypads import Keypad
from ..themes import theme, WHITE, RED, GREEN, DARKGREEN, ORANGE, MAGENTA
from ur.ur import UR
from ..input import (
    BUTTON_ENTER,
    BUTTON_PAGE,
    BUTTON_PAGE_PREV,
    BUTTON_TOUCH,
    SWIPE_DOWN,
    SWIPE_UP,
    PRESSED,
)
from ..display import DEFAULT_PADDING
from ..qr import to_qr_codes
from ..krux_settings import t, Settings, LoggingSettings, BitcoinSettings
from ..sd_card import SDHandler

MENU_CONTINUE = 0
MENU_EXIT = 1
MENU_SHUTDOWN = 2

FLASH_MSG_TIME = 2000

ESC_KEY = 1
FIXED_KEYS = 3  # 'More' key only appears when there are multiple keysets

ANTI_GLARE_WAIT_TIME = 500
QR_CODE_STEP_TIME = 100
SHUTDOWN_WAIT_TIME = 300

TOGGLE_BRIGHTNESS = (BUTTON_PAGE, BUTTON_PAGE_PREV)
PROCEED = (BUTTON_ENTER, BUTTON_TOUCH)

LETTERS = "abcdefghijklmnopqrstuvwxyz"
UPPERCASE_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NUM_SPECIAL_1 = "0123456789 !#$%&'()*"
NUM_SPECIAL_2 = '+,-./:;<=>?@[\\]^_"{|}~'


class Page:
    """Represents a page in the app, with helper methods for common display and
    input operations.

    Must be subclassed.
    """

    def __init__(self, ctx, menu):
        self.ctx = ctx
        self.menu = menu
        self._time_frame = 0
        # context has its own keypad mapping in case touch is not used
        self.y_keypad_map = []
        self.x_keypad_map = []

    def esc_prompt(self):
        """Prompts user for leaving"""
        self.ctx.display.clear()
        answer = self.prompt(t("Are you sure?"), self.ctx.display.height() // 2)
        if self.ctx.input.touch is not None:
            self.ctx.input.touch.clear_regions()
        if answer:
            return ESC_KEY
        return None

    def flash_text(
        self,
        text,
        color=theme.fg_color,
        bg_color=theme.bg_color,
        duration=FLASH_MSG_TIME,
    ):
        """Flashes text centered on the display for duration ms"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(text, color, bg_color)
        time.sleep_ms(duration)
        self.ctx.display.clear()
        self.ctx.input.flush_events()

    def capture_from_keypad(
        self,
        title,
        keysets,
        autocomplete_fn=None,
        possible_keys_fn=None,
        delete_key_fn=None,
        progress_bar_fn=None,
        go_on_change=False,
        starting_buffer="",
        esc_prompt=True,
    ):
        """Displays a key pad and captures a series of keys until the user returns.
        Returns a string.
        """
        buffer = starting_buffer
        pad = Keypad(self.ctx, keysets)
        while True:
            self.ctx.display.clear()
            offset_y = DEFAULT_PADDING
            if (
                len(buffer) + 1
            ) * self.ctx.display.font_width < self.ctx.display.width():
                self.ctx.display.draw_hcentered_text(title, offset_y)
                offset_y += self.ctx.display.font_height * 3 // 2
            self.ctx.display.draw_hcentered_text(buffer, offset_y)

            # offset_y = pad.keypad_offset()  # Dead code?
            if progress_bar_fn:
                progress_bar_fn()
            possible_keys = pad.keys
            if possible_keys_fn is not None:
                possible_keys = possible_keys_fn(buffer)
                pad.get_valid_index(possible_keys)
            pad.draw_keys(possible_keys)
            btn = self.ctx.input.wait_for_button()
            if self.ctx.input.touch is not None:
                if btn == BUTTON_TOUCH:
                    btn = pad.touch_to_physical(possible_keys)
            if btn == BUTTON_ENTER:
                pad.moving_forward = True
                changed = False
                if pad.cur_key_index == pad.del_index:
                    if delete_key_fn is not None:
                        buffer = delete_key_fn(buffer)
                    else:
                        buffer = buffer[: len(buffer) - 1]
                    changed = True
                elif pad.cur_key_index == pad.esc_index:
                    if esc_prompt:
                        if self.esc_prompt() == ESC_KEY:
                            return ESC_KEY
                    else:
                        return ESC_KEY
                    # remap keypad touch array
                    pad.map_keys_array(pad.width, pad.height)
                elif pad.cur_key_index == pad.go_index:
                    break
                elif pad.cur_key_index == pad.more_index:
                    pad.next_keyset()
                elif pad.cur_key_index < len(pad.keys):
                    buffer += pad.keys[pad.cur_key_index]
                    changed = True

                    # Don't autocomplete if deleting
                    if autocomplete_fn is not None:
                        new_buffer = autocomplete_fn(buffer)
                        if new_buffer is not None:
                            buffer = new_buffer
                            break  # auto-Go for load "Via Text"

                if changed and go_on_change:
                    break

            else:
                pad.navigate(btn)

        if self.ctx.input.touch is not None:
            self.ctx.input.touch.clear_regions()
        return buffer

    def capture_qr_code(self):
        """Captures a singular or animated series of QR codes and displays progress to the user.
        Returns the contents of the QR code(s).
        """
        self._time_frame = time.ticks_ms()

        def callback(part_total, num_parts_captured, new_part):
            # Turn on the light as long as the enter button is held down (M5stickV and Amigo)
            if self.ctx.light:
                if self.ctx.input.enter_value() == PRESSED:
                    self.ctx.light.turn_on()
                else:
                    self.ctx.light.turn_off()
            # If board don't have light, ENTER stops the capture
            elif self.ctx.input.enter_event():
                return 1

            # Anti-glare mode (M5stickV and Amigo)
            if self.ctx.input.page_event():
                if self.ctx.camera.has_antiglare():
                    self._time_frame = time.ticks_ms()
                    self.ctx.display.to_portrait()
                    if not self.ctx.camera.antiglare_enabled:
                        self.ctx.camera.enable_antiglare()
                        self.ctx.display.draw_centered_text(t("Anti-glare enabled"))
                    else:
                        self.ctx.camera.disable_antiglare()
                        self.ctx.display.draw_centered_text(t("Anti-glare disabled"))
                    time.sleep_ms(ANTI_GLARE_WAIT_TIME)
                    self.ctx.display.to_landscape()
                    self.ctx.input.flush_events()
                    return 0
                return 1

            # Exit the capture loop with PAGE_PREV or TOUCH
            if self.ctx.input.page_prev_event() or self.ctx.input.touch_event():
                return 1

            # Indicate progress to the user that a new part was captured
            if new_part:
                self.ctx.display.to_portrait()
                filled = self.ctx.display.width() * num_parts_captured
                filled //= part_total
                # self.ctx.display.width()  # Dead code?
                if self.ctx.display.height() < 320:  # M5StickV
                    height = 210
                elif self.ctx.display.height() > 320:  # Amigo
                    height = 380
                else:
                    height = 305
                self.ctx.display.fill_rectangle(
                    0,
                    height,
                    filled,
                    15,
                    theme.fg_color,
                )
                time.sleep_ms(QR_CODE_STEP_TIME)
                self.ctx.display.to_landscape()

            return 0

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Loading Camera.."))
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

    def display_qr_codes(self, data, qr_format, title=""):
        """Displays a QR code or an animated series of QR codes to the user, encoding them
        in the specified format
        """
        done = False
        i = 0
        code_generator = to_qr_codes(data, self.ctx.display.qr_data_width(), qr_format)
        self.ctx.display.clear()
        bright = theme.bg_color == WHITE
        while not done:
            code = None
            num_parts = 0
            try:
                code, num_parts = next(code_generator)
            except:
                code_generator = to_qr_codes(
                    data, self.ctx.display.qr_data_width(), qr_format
                )
                code, num_parts = next(code_generator)
            if bright:
                self.ctx.display.draw_qr_code(0, code, light_color=WHITE)
            else:
                self.ctx.display.draw_qr_code(0, code)
            subtitle = t("Part\n%d / %d") % (i + 1, num_parts) if not title else title
            offset_y = self.ctx.display.qr_offset()
            if title:
                offset_y += self.ctx.display.font_height
            # Clean area below QR code to refresh subtitle/part
            self.ctx.display.fill_rectangle(
                0,
                offset_y,
                self.ctx.display.width(),
                self.ctx.display.height() - offset_y,
                theme.bg_color,
            )
            self.ctx.display.draw_hcentered_text(subtitle, offset_y)
            i = (i + 1) % num_parts
            self.ctx.input.buttons_active = True
            btn = self.ctx.input.wait_for_button(num_parts == 1)
            if btn in TOGGLE_BRIGHTNESS:
                bright = not bright
            elif btn in PROCEED:
                if self.ctx.input.touch is not None:
                    self.ctx.input.buttons_active = False
                done = True
            # interval done in input.py using timers

    def display_mnemonic(self, mnemonic, suffix=""):
        """Displays the 12 or 24-word list of words to the user"""
        words = mnemonic.split(" ")
        word_list = [
            str(i + 1) + "." + ("  " if i + 1 < 10 else " ") + word
            for i, word in enumerate(words)
        ]
        header = t("BIP39") + " " + suffix
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(header)
        starting_y_offset = DEFAULT_PADDING // 4 + (
            len(self.ctx.display.to_lines(header)) * self.ctx.display.font_height
            + self.ctx.display.font_height
        )
        for i, word in enumerate(word_list[:12]):
            offset_x = DEFAULT_PADDING
            offset_y = starting_y_offset + (i * self.ctx.display.font_height)
            self.ctx.display.draw_string(offset_x, offset_y, word)
        if len(word_list) > 12:
            if board.config["type"] == "m5stickv":
                self.ctx.input.wait_for_button()
                self.ctx.display.clear()
                self.ctx.display.draw_hcentered_text(header)
                for i, word in enumerate(word_list[12:]):
                    offset_x = DEFAULT_PADDING
                    offset_y = starting_y_offset + (i * self.ctx.display.font_height)
                    self.ctx.display.draw_string(offset_x, offset_y, word)
            else:
                for i, word in enumerate(word_list[12:]):
                    offset_x = self.ctx.display.width() // 2
                    offset_y = starting_y_offset + (i * self.ctx.display.font_height)
                    self.ctx.display.draw_string(offset_x, offset_y, word)

    def print_qr_prompt(self):
        """Prompts the user to print a QR code in the specified format
        if a printer is connected
        """
        if not self.has_printer():
            return False

        self.ctx.display.clear()
        if self.prompt(
            t("Print to QR?\n\n%s\n\n") % Settings().hardware.printer.driver,
            self.ctx.display.height() // 2,
        ):
            return True
        return False

    def prompt(self, text, offset_y=0):
        """Prompts user to answer Yes or No"""
        # Go up if question has multiple lines
        offset_y -= (
            len(self.ctx.display.to_lines(text)) - 1
        ) * self.ctx.display.font_height
        self.ctx.display.draw_hcentered_text(
            text, offset_y, theme.fg_color, theme.bg_color
        )
        self.y_keypad_map = []
        self.x_keypad_map = []
        if board.config["type"] == "m5stickv":
            return self.ctx.input.wait_for_button() == BUTTON_ENTER
        offset_y += (
            len(self.ctx.display.to_lines(text)) + 1
        ) * self.ctx.display.font_height
        self.x_keypad_map.append(DEFAULT_PADDING)
        self.x_keypad_map.append(self.ctx.display.width() // 2)
        self.x_keypad_map.append(self.ctx.display.width() - DEFAULT_PADDING)
        y_key_map = offset_y - self.ctx.display.font_height // 2
        self.y_keypad_map.append(y_key_map)
        y_key_map += 2 * self.ctx.display.font_height
        self.y_keypad_map.append(y_key_map)
        if self.ctx.input.touch is not None:
            self.ctx.input.touch.clear_regions()
            self.ctx.input.touch.x_regions = self.x_keypad_map
            self.ctx.input.touch.y_regions = self.y_keypad_map

        btn = None
        answer = True
        while btn != BUTTON_ENTER:
            offset_x = self.ctx.display.width() // 4
            offset_x -= (len(t("Yes")) * self.ctx.display.font_width) // 2
            self.ctx.display.draw_string(
                offset_x, offset_y, t("Yes"), theme.go_color, theme.bg_color
            )
            offset_x = (self.ctx.display.width() * 3) // 4
            offset_x -= (len(t("No")) * self.ctx.display.font_width) // 2
            self.ctx.display.draw_string(
                offset_x, offset_y, t("No"), theme.no_esc_color, theme.bg_color
            )
            if self.ctx.input.buttons_active:
                if answer:
                    self.ctx.display.outline(
                        DEFAULT_PADDING,
                        offset_y - self.ctx.display.font_height // 2,
                        self.ctx.display.usable_width() // 2,
                        2 * self.ctx.display.font_height - 2,
                        theme.go_color,
                    )
                else:
                    self.ctx.display.outline(
                        self.ctx.display.width() // 2,
                        offset_y - self.ctx.display.font_height // 2,
                        self.ctx.display.usable_width() // 2,
                        2 * self.ctx.display.font_height - 2,
                        theme.no_esc_color,
                    )
            elif self.ctx.input.touch is not None:
                for region in self.x_keypad_map:
                    self.ctx.display.fill_rectangle(
                        region,
                        self.y_keypad_map[0],
                        1,
                        2 * self.ctx.display.font_height,
                        theme.frame_color,
                    )
            btn = self.ctx.input.wait_for_button()
            if btn in (BUTTON_PAGE, BUTTON_PAGE_PREV):
                answer = not answer
                # erase yes/no area for next loop
                self.ctx.display.fill_rectangle(
                    0,
                    offset_y - self.ctx.display.font_height,
                    self.ctx.display.width() + 1,
                    3 * self.ctx.display.font_height,
                    theme.bg_color,
                )
            elif btn == BUTTON_TOUCH:
                self.ctx.input.touch.clear_regions()
                # index 0 = Yes
                # index 1 = No
                if self.ctx.input.touch.current_index():
                    return False
                return True
        # BUTTON_ENTER
        return answer

    def fit_to_line(self, text, prefix="", fixed_chars=0):
        """Fits text with prefix plus fixed_chars at the beginning into one line,
        removing the central content and leaving the ends"""

        add_chars_amount = (
            self.ctx.display.usable_width() // self.ctx.display.font_width
        )
        add_chars_amount -= len(prefix) + fixed_chars + 2
        add_chars_amount //= 2
        return (
            prefix
            + text[: add_chars_amount + fixed_chars]
            + ".."
            + text[-add_chars_amount:]
        )

    def has_printer(self):
        """Checks if the device has a printer setup"""
        return Settings().hardware.printer.driver != "none"

    def has_sd_card(self):
        """Checks if the device has a SD card inserted"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Checking for SD card.."))
        try:
            # Check for SD hot-plug
            with SDHandler():
                return True
        except:
            return False

    def shutdown(self):
        """Handler for the 'shutdown' menu item"""
        if self.prompt(t("Are you sure?"), self.ctx.display.height() // 2):
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Shutting down.."))
            time.sleep_ms(SHUTDOWN_WAIT_TIME)
            return MENU_SHUTDOWN
        return MENU_CONTINUE

    def run(self, start_from_index=None):
        """Runs the page's menu loop"""
        _, status = self.menu.run_loop(start_from_index)
        return status != MENU_SHUTDOWN


class ListView:
    """Acts as a fixed-size, sliding window over an underlying list"""

    def __init__(self, lst, max_size):
        self.list = lst
        self.max_size = max_size
        self.offset = 0
        self.iter_index = 0

    def __getitem__(self, key):
        return self.list[self.offset + key]

    def __iter__(self):
        self.iter_index = 0
        return self

    def __next__(self):
        if self.iter_index < len(self):
            self.iter_index += 1
            return self.__getitem__(self.iter_index - 1)
        raise StopIteration

    def __len__(self):
        return min(self.max_size, len(self.list[self.offset :]))

    def move_forward(self):
        """Slides the window one size-increment forward, wrapping around"""
        self.offset += self.max_size
        if self.offset >= len(self.list):
            self.offset = 0

    def move_backward(self):
        """Slides the window one size-increment backward, wrapping around"""
        self.offset -= self.max_size
        if self.offset < 0:
            self.offset = int(
                (math.ceil(len(self.list) / self.max_size) - 1) * self.max_size
            )

    def index(self, i):
        """Returns the true index of an element in the underlying list"""
        return self.offset + i


class Menu:
    """Represents a menu that can render itself to the screen, handle item selection,
    and invoke menu item callbacks that return a status
    """

    def __init__(self, ctx, menu, offset=0):
        self.ctx = ctx
        self.menu = menu
        self.menu_offset = offset
        max_viewable = min(
            self.ctx.display.max_menu_lines(self.menu_offset),
            len(self.menu),
        )
        self.menu_view = ListView(self.menu, max_viewable)

    def screensaver(self):
        """Loads and starts screensaver"""
        from .screensaver import ScreenSaver

        screen_saver = ScreenSaver(self.ctx)
        screen_saver.start()

    def run_loop(self, start_from_index=None):
        """Runs the menu loop until one of the menu items returns either a MENU_EXIT
        or MENU_SHUTDOWN status
        """
        start_from_submenu = False
        selected_item_index = 0
        if start_from_index is not None:
            start_from_submenu = True
            selected_item_index = start_from_index
        while True:
            gc.collect()
            if self.menu_offset:
                self.ctx.display.fill_rectangle(
                    0,
                    self.menu_offset,
                    self.ctx.display.width(),
                    self.ctx.display.height() - self.menu_offset,
                    theme.bg_color,
                )
            else:
                self.ctx.display.clear()
            if self.ctx.input.touch is not None:
                self._draw_touch_menu(selected_item_index)
            else:
                self._draw_menu(selected_item_index)

            self.draw_status_bar()
            self.ctx.input.flush_events()

            if start_from_submenu:
                status = self._clicked_item(selected_item_index)
                if status != MENU_CONTINUE:
                    return (self.menu_view.index(selected_item_index), status)
                start_from_submenu = False
            else:
                btn = self.ctx.input.wait_for_button(
                    # Block if screen saver not active
                    block=Settings().appearance.screensaver_time == 0,
                    wait_duration=Settings().appearance.screensaver_time * 60000,
                )
                if self.ctx.input.touch is not None:
                    if btn == BUTTON_TOUCH:
                        selected_item_index = self.ctx.input.touch.current_index()
                        btn = BUTTON_ENTER
                    self.ctx.input.touch.clear_regions()
                if btn == BUTTON_ENTER:
                    status = self._clicked_item(selected_item_index)
                    if status != MENU_CONTINUE:
                        return (self.menu_view.index(selected_item_index), status)
                elif btn == BUTTON_PAGE:
                    selected_item_index = (selected_item_index + 1) % len(
                        self.menu_view
                    )
                    if selected_item_index == 0:
                        self.menu_view.move_forward()
                elif btn == BUTTON_PAGE_PREV:
                    selected_item_index = (selected_item_index - 1) % len(
                        self.menu_view
                    )
                    if selected_item_index == len(self.menu_view) - 1:
                        self.menu_view.move_backward()
                        # Update selected item index to be the last viewable item,
                        # which may be a different index than before we moved backward
                        selected_item_index = len(self.menu_view) - 1
                elif btn == SWIPE_UP:
                    self.menu_view.move_forward()
                elif btn == SWIPE_DOWN:
                    self.menu_view.move_backward()
                elif btn is None and not self.menu_offset:
                    # Activates screensaver if there's no info_box(other things draw on the screen)
                    self.screensaver()

    def _clicked_item(self, selected_item_index):
        if self.menu_view[selected_item_index][1] is None:
            return MENU_CONTINUE
        try:
            self.ctx.display.clear()
            status = self.menu_view[selected_item_index][1]()
            if status != MENU_CONTINUE:
                return status
        except Exception as e:
            self.ctx.log.exception(
                'Exception occurred in menu item "%s"'
                % self.menu_view[selected_item_index][0]
            )
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Error:\n%s") % repr(e), theme.error_color
            )
            self.ctx.input.wait_for_button()
        return MENU_CONTINUE

    def draw_status_bar(self):
        """Draws a status bar along the top of the UI"""
        if self.menu_offset == 0:  # Only draws if menu is full screen
            self.draw_logging_indicator()
            self.draw_battery_indicator()
            self.draw_network_indicator()

    #     self.draw_ram_indicator()

    # def draw_ram_indicator(self):
    #     gc.collect()
    #     ram_text = "RAM: " + str(gc.mem_free())
    #     self.ctx.display.draw_string(12, 0, ram_text, GREEN)

    def draw_logging_indicator(self):
        """Draws a square mark if logging is enabled"""
        log_level = Settings().logging.level

        if log_level == LoggingSettings.NONE_TXT:
            return

        color = RED  # ERROR
        if log_level == LoggingSettings.WARN_TXT:
            color = ORANGE
        if log_level == LoggingSettings.INFO_TXT:
            color = DARKGREEN
        if log_level == LoggingSettings.DEBUG_TXT:
            color = MAGENTA

        # print the square at the top left
        self.ctx.display.fill_rectangle(3, 3, 6, 6, color)

    def draw_battery_indicator(self):
        """Draws a battery icon with depletion proportional to battery voltage"""
        if not self.ctx.power_manager.has_battery():
            return

        charge = self.ctx.power_manager.battery_charge_remaining()
        if self.ctx.power_manager.usb_connected():
            battery_color = theme.go_color
        else:
            if charge < 0.3:
                battery_color = theme.error_color
            else:
                battery_color = theme.frame_color

        # Draw (filled) outline of battery in top-right corner of display
        padding = 4
        cylinder_length = 22
        cylinder_height = 7
        self.ctx.display.outline(
            self.ctx.display.width() - padding - cylinder_length,
            padding,
            cylinder_length,
            cylinder_height,
            battery_color,
        )
        self.ctx.display.fill_rectangle(
            self.ctx.display.width() - padding + 1,
            padding + 2,
            2,
            cylinder_height - 3,
            battery_color,
        )

        # Indicate how much battery is depleted
        charge_length = int((cylinder_length - 3) * charge)
        self.ctx.display.fill_rectangle(
            self.ctx.display.width() - padding - cylinder_length + 2,
            padding + 2,
            charge_length,
            cylinder_height - 3,
            theme.go_color,
        )

    def draw_network_indicator(self):
        """Draws test at top if testnet is enabled"""
        if Settings().bitcoin.network == BitcoinSettings.TEST_TXT:
            self.ctx.display.draw_string(12, 0, "test", GREEN)

    def _draw_touch_menu(self, selected_item_index):
        # map regions with dynamic height to fill screen
        self.ctx.input.touch.clear_regions()
        offset_y = 0
        Page.y_keypad_map = [offset_y]
        for menu_item in self.menu_view:
            offset_y += len(self.ctx.display.to_lines(menu_item[0])) + 1
            Page.y_keypad_map.append(offset_y)
        height_multiplier = (
            self.ctx.display.height() - 2 * DEFAULT_PADDING - self.menu_offset
        )
        height_multiplier //= max(offset_y, 1)
        Page.y_keypad_map = [
            n * height_multiplier + DEFAULT_PADDING + self.menu_offset
            for n in Page.y_keypad_map
        ]
        self.ctx.input.touch.y_regions = Page.y_keypad_map

        # draw dividers and outline
        for i, y in enumerate(Page.y_keypad_map[:-1]):
            if i and not self.ctx.input.buttons_active:
                self.ctx.display.fill_rectangle(
                    0, y, self.ctx.display.width(), 1, theme.frame_color
                )

        # draw centralized strings in regions
        for i, menu_item in enumerate(self.menu_view):
            menu_item_lines = self.ctx.display.to_lines(menu_item[0])
            offset_y = Page.y_keypad_map[i + 1] - Page.y_keypad_map[i]
            offset_y -= len(menu_item_lines) * self.ctx.display.font_height
            offset_y //= 2
            offset_y += Page.y_keypad_map[i]
            fg_color = (
                theme.fg_color if menu_item[1] is not None else theme.disabled_color
            )
            for j, text in enumerate(menu_item_lines):
                if selected_item_index == i and self.ctx.input.buttons_active:
                    self.ctx.display.fill_rectangle(
                        0,
                        offset_y + 1 - self.ctx.display.font_height // 2,
                        self.ctx.display.width(),
                        (len(menu_item_lines) + 1) * self.ctx.display.font_height,
                        fg_color,
                    )
                    self.ctx.display.draw_hcentered_text(
                        text,
                        offset_y + self.ctx.display.font_height * j,
                        theme.bg_color,
                        fg_color,
                    )
                else:
                    self.ctx.display.draw_hcentered_text(
                        text, offset_y + self.ctx.display.font_height * j, fg_color
                    )

    def _draw_menu(self, selected_item_index):
        if self.menu_offset:
            offset_y = self.menu_offset + self.ctx.display.font_height // 2
        else:
            offset_y = len(self.menu_view) * 2
            extra_lines = 0
            for menu_item in self.menu_view:
                extra_lines += len(self.ctx.display.to_lines(menu_item[0])) - 1
            offset_y += extra_lines
            offset_y *= self.ctx.display.font_height
            offset_y = self.ctx.display.height() - offset_y
            offset_y //= 2
            offset_y += self.ctx.display.font_height // 2
        for i, menu_item in enumerate(self.menu_view):
            fg_color = (
                theme.fg_color if menu_item[1] is not None else theme.disabled_color
            )
            menu_item_lines = self.ctx.display.to_lines(menu_item[0])
            delta_y = (len(menu_item_lines) + 1) * self.ctx.display.font_height
            if selected_item_index == i:
                self.ctx.display.fill_rectangle(
                    0,
                    offset_y + 1 - self.ctx.display.font_height // 2,
                    self.ctx.display.width(),
                    delta_y - 2,
                    fg_color,
                )
                for j, text in enumerate(menu_item_lines):
                    self.ctx.display.draw_hcentered_text(
                        text,
                        offset_y + self.ctx.display.font_height * j,
                        theme.bg_color,
                        fg_color,
                    )
            else:
                for j, text in enumerate(menu_item_lines):
                    self.ctx.display.draw_hcentered_text(
                        text, offset_y + self.ctx.display.font_height * j, fg_color
                    )
            offset_y += delta_y
