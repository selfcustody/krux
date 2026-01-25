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
import os

# avoids importing from flash VSF
os.chdir("/")

VERSION = "1.0"
NAME = "Steganography"

from krux.pages import (
    Menu,
    MENU_CONTINUE,
    MENU_EXIT,
    ESC_KEY,
    LETTERS,
    UPPERCASE_LETTERS,
    NUM_SPECIAL_1,
    NUM_SPECIAL_2,
)
from krux.krux_settings import t
from krux.display import (
    STATUS_BAR_HEIGHT,
    FONT_HEIGHT,
    DEFAULT_PADDING,
    BOTTOM_PROMPT_LINE,
)
from krux.themes import theme
from krux.kboard import kboard
from krux.wdt import wdt
from krux.pages.device_tests import DeviceTests
from krux.sd_card import BMP_IMAGE_EXTENSION
from krux.pages.file_operations import SaveFile
from krux.settings import SD_PATH
from krux.pages.utils import Utils
import image
import lcd
import gc


# 16 bits - 2 bytes - 565
# 65535 - white 1111 1111 1111 1111
# 248 - red     0000 0000 1111 1000
# 57351 - green 1110 0000 0000 0111
# 7936 - blue   0001 1111 0000 0000

PAYLOAD_LEN_BYTES = 3  # sufficient to ~4000x4000 px (OOM already with 600x550 px)
PAYLOAD_ENDIAN = "big"

LSB_SHIFTS = [13, 3, 8]  # 13G, 3R, 8B
BITS_PER_PIXEL = len(LSB_SHIFTS)
MASKS = [1 << s for s in LSB_SHIFTS]

# -------------------


class KMenu(Menu):
    """Customizes the page's menu"""

    def __init__(
        self,
        ctx,
        menu,
        offset=None,
        disable_statusbar=False,
        back_label="Back",
        back_status=lambda: MENU_EXIT,
    ):
        super().__init__(ctx, menu, offset, disable_statusbar, back_label, back_status)
        self.disable_statusbar = False
        if offset is None:
            self.menu_offset = STATUS_BAR_HEIGHT
        else:
            # Always disable status bar if menu has non standard offset
            self.disable_statusbar = True
            self.menu_offset = offset if offset >= 0 else DEFAULT_PADDING

    def new_draw_wallet_indicator(self):
        """Customize the top bar"""
        if not kboard.is_m5stickv:
            self.ctx.display.draw_hcentered_text(
                NAME,
                STATUS_BAR_HEIGHT - FONT_HEIGHT - 1,
                theme.highlight_color,
                theme.info_bg_color,
            )
        else:
            self.ctx.display.draw_string(
                24,
                STATUS_BAR_HEIGHT - FONT_HEIGHT - 1,
                NAME,
                theme.highlight_color,
                theme.info_bg_color,
            )

    def new_draw_network_indicator(self):
        """Don't draw testnet"""

    # Overwrite Menu top bar functions to allow code reuse
    Menu.draw_wallet_indicator = new_draw_wallet_indicator
    Menu.draw_network_indicator = new_draw_network_indicator


# -------------------


class Kapp(DeviceTests):
    """Represents the page of the kapp"""

    def __init__(self, ctx):
        shtn_reboot_label = (
            t("Shutdown") if ctx.power_manager.has_battery() else t("Reboot")
        )
        super().__init__(
            ctx,
        )
        self.menu = KMenu(
            ctx,
            [
                (t("BMP Via Camera"), self.camera),
                (t("SD Card"), self.sd_menu),
                (t("Hide Data in BMP"), self.hide_menu),
                (t("Reveal Data"), self.reveal_menu),
                (t("About"), self.about),
                (shtn_reboot_label, self.shutdown),
            ],
            back_label=None,
        )

    def camera(self):
        """Capture a BMP by camera"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("TOUCH or ENTER to capture"))
        self.ctx.display.to_landscape()
        self.ctx.camera.initialize_run()
        self.ctx.display.clear()

        # Flush events ocurred while loading camera
        self.ctx.input.reset_ios_state()

        leave = False
        while True:
            wdt.feed()

            img = self.ctx.camera.snapshot()

            if self.ctx.input.enter_event() or self.ctx.input.touch_event(
                validate_position=False
            ):
                break
            if self.ctx.input.page_event() or self.ctx.input.page_prev_event():
                leave = True
                break

            self.ctx.display.render_image(img)

        self.ctx.display.to_portrait()
        self.ctx.camera.stop_sensor()

        # User cancelled
        if leave:
            self.flash_error(t("Capture cancelled"))
            return MENU_CONTINUE

        self.ctx.input.reset_ios_state()
        if self.prompt(
            t("Save to SD card?"),
            BOTTOM_PROMPT_LINE,
        ):
            sf = SaveFile(self.ctx)
            new_filename = sf.set_filename(
                empty_filename="photo",
                file_extension=BMP_IMAGE_EXTENSION,
            )

            if new_filename == ESC_KEY:
                return MENU_CONTINUE

            # if user defined a filename and it is ok, save!
            if new_filename:
                # clear and say something to the user
                self.ctx.display.clear()
                self.ctx.display.draw_centered_text(t("Processing…"))

                # Now save the file
                img.save("/%s/%s" % (SD_PATH, new_filename))

                # Show the user the filename
                self.flash_text(
                    t("Saved to SD card:") + "\n\n%s" % new_filename,
                    highlight_prefix=":",
                )
                return MENU_CONTINUE
        else:
            self.flash_error(t("Capture cancelled"))

        return MENU_CONTINUE

    def sd_menu(self):
        """Handler for the 'SD card' menu item"""
        submenu = Menu(
            self.ctx,
            [
                (t("Check SD Card"), self.sd_check),
                (t("View BMP"), self.view),
            ],
        )
        index, status = submenu.run_loop()
        if index == submenu.back_index:
            return MENU_CONTINUE
        return status

    def view(self):
        """Handler for the 'View BMP' menu item"""
        if not self.has_sd_card():
            self.flash_error(t("SD card not detected."))
            return MENU_CONTINUE

        utils = Utils(self.ctx)
        img_path, _ = utils.load_file(
            file_ext=BMP_IMAGE_EXTENSION,
            prompt=False,
            only_get_filename=True,
        )

        # pressed Back, no file selected
        if img_path == "":
            return MENU_CONTINUE

        self.ctx.display.clear()
        # idea: use img.width(), img.height() to rotate or not
        self.ctx.display.to_landscape()
        try:
            img = image.Image("/%s/%s" % (SD_PATH, img_path))
            lcd.display(img)
        except:
            self.ctx.display.to_portrait()
            self.flash_error(t("Image is too big!"))
            return MENU_CONTINUE

        self.ctx.input.wait_for_button()
        self.ctx.display.to_portrait()
        return MENU_CONTINUE

    def about(self):
        """Handler for the 'about' menu item"""

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(
            "Kapp %s\n%s: %s\n\n" % (NAME, t("Version"), VERSION)
            + t("Conceal data within BMP.")
        )
        self.ctx.input.wait_for_button()
        return MENU_CONTINUE

    def hide_menu(self):
        """Handler for the 'Hide Data in BMP' menu item"""
        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Provide the data to hide"))
        if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
            return MENU_CONTINUE

        submenu = KMenu(
            self.ctx,
            [
                (t("Via Camera"), self.scan_qr),
                (t("Via Manual Input"), self.text_entry),
                (t("From Storage"), self.read_file),
            ],
        )
        index, status = submenu.run_loop()
        if index == submenu.back_index or status == MENU_CONTINUE:
            return MENU_CONTINUE

        secret = status

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Select the BMP file"))
        if not self.prompt(t("Proceed?"), BOTTOM_PROMPT_LINE):
            return MENU_CONTINUE

        if not self.has_sd_card():
            self.flash_error(t("SD card not detected."))
            return MENU_CONTINUE

        utils = Utils(self.ctx)
        img_path, _ = utils.load_file(
            file_ext=BMP_IMAGE_EXTENSION,
            prompt=False,
            only_get_filename=True,
        )

        # pressed Back, no file selected
        if img_path == "":
            return MENU_CONTINUE

        split_img_path = img_path.split("/")
        sf = SaveFile(self.ctx)
        new_filename = sf.set_filename(
            curr_filename=split_img_path[-1],
            file_extension=BMP_IMAGE_EXTENSION,
            suffix="-hid",
        )

        if new_filename == ESC_KEY:
            return MENU_CONTINUE

        # if user defined a filename and it is ok, save!
        if new_filename:
            # clear and say something to the user
            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(t("Processing…"))

            new_filename_path = SD_PATH + "/"
            if len(split_img_path) > 1:
                new_filename_path += "/".join(split_img_path[:-1]) + "/"
            new_filename_path += new_filename

            self.hide_data(secret, "/%s/%s" % (SD_PATH, img_path), new_filename_path)
            gc.collect()

            # Show the user the filename
            self.flash_text(
                t("Saved to SD card:") + "\n\n%s" % new_filename,
                highlight_prefix=":",
            )

            retrieved = self.extract_data(new_filename_path)
            if retrieved != secret:
                self.flash_error(t("Could not retrieve secret from %s") % new_filename)

        return MENU_CONTINUE

    def hide_data(self, secret: bytes, cover_path: str, stego_path: str):
        """Hide secret into cover_path file and output result to stego_path file"""

        def _bits_generator(payload):
            for b in payload:
                # for every bit in a byte
                for i in range(7, -1, -1):
                    yield (b >> i) & 1

        try:
            img = image.Image(cover_path)
        except:
            self.flash_error(t("Image is too big!"))
            return MENU_CONTINUE
        w, h = img.width(), img.height()

        payload = len(secret).to_bytes(PAYLOAD_LEN_BYTES, PAYLOAD_ENDIAN) + secret
        bit_gen = _bits_generator(payload)
        bits_needed = len(payload) * 8  # each char in binary is 1 byte
        pixels_needed = -(-bits_needed // BITS_PER_PIXEL)  # ceil of division
        if pixels_needed > w * h:
            raise ValueError("Need %s px, image has %s" % (pixels_needed, w * h))

        # encode all bits in the img
        bit_idx = 0
        for y in range(h):
            for x in range(w):
                if bit_idx >= bits_needed:
                    break
                pixel = img.get_pixel(x, y, rgbtuple=False)  # raw 16-bit int

                for i in range(BITS_PER_PIXEL):
                    if bit_idx >= bits_needed:
                        break
                    try:
                        bit = next(bit_gen)
                    except StopIteration:
                        break
                    shift = LSB_SHIFTS[i]
                    mask = MASKS[i]
                    pixel = (pixel & ~mask) | (bit << shift)
                    bit_idx += 1
                img.set_pixel(x, y, pixel)
            if bit_idx >= bits_needed:
                break

        img.save(stego_path)
        return MENU_CONTINUE

    def extract_data(self, stego_path: str):
        """Return secret extracted from stego_path"""
        try:
            img = image.Image(stego_path)
        except:
            self.flash_error(t("Image is too big!"))
            return MENU_CONTINUE
        w, h = img.width(), img.height()

        # Read total_bits length
        payload_len = 0
        bits_read = 0
        pos_x = pos_y = 0
        total_bits = PAYLOAD_LEN_BYTES * 8
        while bits_read < total_bits:
            pixel = img.get_pixel(pos_x, pos_y, rgbtuple=False)

            for i in range(BITS_PER_PIXEL):
                if bits_read >= total_bits:
                    break
                shift = LSB_SHIFTS[i]
                bit = (pixel >> shift) & 1
                payload_len = (payload_len << 1) | bit
                bits_read += 1

            # Advance position
            pos_x += 1
            if pos_x >= w:
                pos_x = 0
                pos_y += 1
                if pos_y >= h:
                    raise ValueError("Not enough px to retrieve data")

        # Read payload byte-by-byte
        payload = bytearray()
        cur = cur_bits = 0
        total_bits = 0
        bits_needed = payload_len * 8
        while total_bits < bits_needed:
            pixel = img.get_pixel(pos_x, pos_y, rgbtuple=False)

            for i in range(BITS_PER_PIXEL):
                if total_bits >= bits_needed:
                    break
                shift = LSB_SHIFTS[i]
                bit = (pixel >> shift) & 1
                cur = (cur << 1) | bit
                cur_bits += 1

                if cur_bits == 8:
                    payload.append(cur)
                    total_bits += 8
                    cur = cur_bits = 0

            # Advance position
            pos_x += 1
            if pos_x >= w:
                pos_x = 0
                pos_y += 1
                if pos_y >= h:
                    break

        if len(payload) < payload_len:
            raise ValueError("Payload truncated")
        return bytes(payload[:payload_len])

    def reveal_menu(self):
        """Handler for the 'Reveal Data' menu item"""
        utils = Utils(self.ctx)
        img_path, _ = utils.load_file(
            file_ext=BMP_IMAGE_EXTENSION,
            prompt=False,
            only_get_filename=True,
        )

        # pressed Back, no file selected
        if img_path == "":
            return MENU_CONTINUE

        secret = self.extract_data("/%s/%s" % (SD_PATH, img_path))

        self.ctx.display.clear()
        if not secret or secret == b"\x00":
            self.flash_error(t("No secret found!"))
            return MENU_CONTINUE

        self.flash_text(t("Found secret:") + "\n%s bytes" % len(secret))

        from krux.pages.datum_tool import DatumTool

        page = DatumTool(self.ctx)
        page.contents = secret
        page.title = img_path.rsplit("/", 1)[-1]
        return page.view_contents()

    def scan_qr(self):
        """Handler for the 'Scan a QR' menu item"""

        from krux.pages.qr_capture import QRCodeCapture
        import urtypes

        qr_scanner = QRCodeCapture(self.ctx)
        contents, fmt = qr_scanner.qr_capture_loop()
        if contents is None:
            self.flash_error(t("Failed to load"))
            return MENU_CONTINUE

        if fmt == 2:
            if contents.type == "bytes":
                contents = urtypes.bytes.Bytes.from_cbor(contents.cbor).data

        if isinstance(contents, str):
            contents = contents.encode("utf-8")

        return contents

    def text_entry(self):
        """Handler for the 'Text Entry' menu item"""

        text = ""
        while True:
            # Loop until user types a valid data or press ESC
            text = self.capture_from_keypad(
                t("Filename"),
                [LETTERS, UPPERCASE_LETTERS, NUM_SPECIAL_1, NUM_SPECIAL_2],
                starting_buffer=text,
            )

            if text == ESC_KEY:
                return MENU_CONTINUE

            self.ctx.display.clear()
            self.ctx.display.draw_centered_text(
                t("Proceed?") + " " + text, highlight_prefix="?"
            )
            if self.prompt("", BOTTOM_PROMPT_LINE):
                return text.encode("utf-8")

        return MENU_CONTINUE

    def read_file(self):
        """Handler for the 'Read File' menu item"""
        if not self.has_sd_card():
            self.flash_error(t("SD card not detected."))
            return MENU_CONTINUE

        utils = Utils(self.ctx)
        try:
            _, contents = utils.load_file(prompt=False)
        except OSError:
            pass

        if not contents:
            return MENU_CONTINUE

        self.ctx.display.clear()
        self.ctx.display.draw_centered_text(t("Processing…"))

        # utils.load_file() always returns binary
        return contents


# -------------------


def run(ctx):
    """Runs this kapp"""

    Kapp(ctx).run()
