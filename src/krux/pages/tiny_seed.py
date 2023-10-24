import hashlib
import board
import lcd
import image
import sensor
import time
from embit.wordlists.bip39 import WORDLIST
from . import Page, FLASH_MSG_TIME
from ..themes import theme
from ..wdt import wdt
from ..krux_settings import t
from ..display import DEFAULT_PADDING
from ..camera import OV7740_ID, OV2640_ID, OV5642_ID
from ..input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV, BUTTON_TOUCH

# Tiny Seed last bit index positions according to checksums
TS_LAST_BIT_NO_CS = 143
TS_LAST_BIT_12W_CS = 139
TS_LAST_BIT_24W_CS = 135

TS_ESC_START_POSITION = 156
TS_ESC_END_POSITION = 161
TS_GO_POSITION = 167


class TinySeed(Page):
    """Class for handling Tinyseed fomat"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        self.x_offset = DEFAULT_PADDING // 2 + 2 * self.ctx.display.font_width
        self.printer = None
        # case for non m5stickv
        if self.ctx.display.width() > 135:
            self.y_offset = DEFAULT_PADDING + 3 * self.ctx.display.font_height
            self.x_pad = self.ctx.display.width() * 2 // 27
            self.y_pad = self.ctx.display.height() // 17
        else:
            # case for m5stickv
            self.y_offset = 2 * self.ctx.display.font_height
            self.x_pad = self.ctx.display.font_width + 1
            self.y_pad = self.ctx.display.font_height

    def _draw_grid(self):
        """Draws grid for import and export Tinyseed UI"""
        y_var = self.y_offset
        x_offset = self.x_offset
        for _ in range(13):
            self.ctx.display.fill_rectangle(
                x_offset,
                self.y_offset,
                1,
                12 * self.y_pad,
                theme.frame_color,
            )
            x_offset += self.x_pad
            self.ctx.display.fill_rectangle(
                self.x_offset,
                y_var,
                12 * (self.x_pad),
                1,
                theme.frame_color,
            )
            y_var += self.y_pad

    def _draw_labels(self, page):
        """Draws labels for import and export Tinyseed UI"""
        self.ctx.display.draw_hcentered_text(t("Tiny Seed"))

        # case for non m5stickv
        if self.ctx.display.width() > 135:
            self.ctx.display.to_landscape()
            bit_number = 2048
            bit_offset = DEFAULT_PADDING // 2 + 2 * self.ctx.display.font_height
            for _ in range(12):
                lcd.draw_string(
                    (7 - len(str(bit_number))) * self.ctx.display.font_width
                    - DEFAULT_PADDING // 2,
                    self.ctx.display.width() - bit_offset,
                    str(bit_number),
                    theme.fg_color,
                    theme.bg_color,
                )
                bit_number //= 2
                bit_offset += self.x_pad
            self.ctx.display.to_portrait()
        y_offset = self.y_offset
        y_offset += (self.y_pad - self.ctx.display.font_height) // 2
        for x in range(12):
            line = str(page * 12 + x + 1)
            if (page * 12 + x + 1) < 10:
                line = " " + line
            self.ctx.display.draw_string(DEFAULT_PADDING // 2, y_offset, line)
            y_offset += self.y_pad

    def _draw_punched(self, words, page):
        """Draws punched bits for import and export Tinyseed UI"""
        y_offset = self.y_offset
        for x in range(12):
            if isinstance(words[0], str):
                word_list_index = WORDLIST.index(words[page * 12 + x]) + 1
            else:
                word_list_index = words[page * 12 + x]
            for y in range(12):
                if (word_list_index >> (11 - y)) & 1:
                    x_offset = self.x_offset + 3
                    x_offset += y * (self.x_pad)
                    self.ctx.display.fill_rectangle(
                        x_offset,
                        y_offset + 3,
                        self.x_pad - 5,
                        self.y_pad - 5,
                        theme.highlight_color,
                    )
            y_offset += self.y_pad

    def export(self):
        """Shows seed as a punch pattern for Tiny Seed layout"""
        words = self.ctx.wallet.key.mnemonic.split(" ")
        for page in range(len(words) // 12):
            self._draw_labels(page)
            self._draw_grid()
            self._draw_punched(words, page)
            self.ctx.input.wait_for_button()
            self.ctx.display.clear()

    def print_tiny_seed(self):
        """Creates a bitmap image of a punched Tiny Seed and sends it to a thermal printer"""
        # Scale from original: 1.5X

        from ..printers import create_printer

        self.printer = create_printer()
        words = self.ctx.wallet.key.mnemonic.split(" ")
        image_size = 156
        border_y = 8
        border_x = 16
        grid_x_offset = border_x + 17  # border + 4,3mm*8px
        grid_y_offset = border_y + 26  # border + 6,5mm*8px
        pad_x = 7  # 1,75mm*8px
        pad_y = 8  # 2mm*8px
        self.ctx.display.clear()
        self.ctx.display.draw_hcentered_text(
            t("Printing ..."), self.ctx.display.height() // 2
        )
        self.printer.print_string("Tiny Seed\n\n")
        for page in range(len(words) // 12):
            # creates an image
            ts_image = image.Image(size=(image_size, image_size), copy_to_fb=True)
            ts_image.clear()
            # Frame
            # Upper
            ts_image.draw_rectangle(
                0,
                0,
                109 + 2 * border_x,  # 27,2mm*8px + ...
                border_y,
                lcd.WHITE,
                fill=True,
            )
            # Lower
            ts_image.draw_rectangle(
                0,
                138 + border_y,
                109 + 2 * border_x,  # 27,2mm*8px + ...
                border_y,
                lcd.WHITE,
                fill=True,
            )
            # Left
            ts_image.draw_rectangle(0, border_y, border_x, 138, lcd.WHITE, fill=True)
            # Right
            ts_image.draw_rectangle(
                109 + border_x, border_y, border_x, 138, lcd.WHITE, fill=True
            )

            # labels
            y_offset = grid_y_offset
            if self.ctx.display.font_height > pad_y:
                y_offset -= (self.ctx.display.font_height - pad_y) // 2 + 1

            # grid
            y_offset = grid_y_offset
            x_offset = grid_x_offset
            for _ in range(13):
                ts_image.draw_line(
                    x_offset,
                    y_offset,
                    x_offset,
                    y_offset + 12 * pad_y,
                    lcd.WHITE,
                )
                x_offset += pad_x
            for _ in range(13):
                ts_image.draw_line(
                    grid_x_offset,
                    y_offset,
                    grid_x_offset + 12 * pad_x,
                    y_offset,
                    lcd.WHITE,
                )
                y_offset += pad_y

            # draw punched
            y_offset = grid_y_offset
            for y in range(12):
                word_list_index = WORDLIST.index(words[page * 12 + y]) + 1
                for x in range(12):
                    if (word_list_index >> (11 - x)) & 1:
                        x_offset = grid_x_offset
                        x_offset += x * (pad_x)
                        ts_image.draw_rectangle(
                            x_offset, y_offset, pad_x, pad_y, lcd.WHITE, fill=True
                        )
                y_offset += pad_y

            # Convert image to bitmap bytes
            ts_image.to_grayscale()
            ts_image.binary([(125, 255)])
            # # Debug image
            # lcd.display(ts_image, roi=(0, 0, image_size, image_size))
            # self.ctx.input.wait_for_button()

            # Print
            self.printer.set_bitmap_mode(image_size // 8, image_size, 3)
            for y in range(image_size):
                line_bytes = bytes([])
                x = 0
                for _ in range(image_size // 8):
                    im_byte = 0
                    for _ in range(8):
                        im_byte <<= 1
                        if ts_image.get_pixel(x, y):
                            im_byte |= 1
                        x += 1
                    line_bytes += bytes([im_byte])
                # send line by line to be printed
                self.printer.print_bitmap_line(line_bytes)
                wdt.feed()
            grid_x_offset = border_x + 16  # 4,1mm*8px
            grid_y_offset = border_y + 25  # 6,2mm*8px
        self.printer.feed(4)
        self.ctx.display.clear()

    def _draw_index(self, index):
        """Outline index postition"""
        width = 6 * self.x_pad - 2
        height = self.y_pad - 2

        if index > TS_ESC_END_POSITION:
            x_position = self.x_offset + 6 * self.x_pad + 1
            # case for m5stickv
            if self.ctx.display.width() == 135:
                height = self.y_pad
        elif index >= TS_ESC_START_POSITION:
            x_position = self.x_offset + 1
            # case for m5stickv
            if self.ctx.display.width() == 135:
                height = self.y_pad
        else:
            x_position = index % 12
            x_position *= self.x_pad
            x_position += self.x_offset + 1
            width = self.x_pad - 2
        y_position = index // 12
        y_position *= self.y_pad
        y_position += self.y_offset + 1
        self.ctx.display.outline(
            x_position,
            y_position,
            width,
            height,
            theme.fg_color,
        )

    def _draw_menu(self):
        """Draws options to leave and proceed"""
        if self.ctx.input.touch is not None:
            y_offset = self.ctx.input.touch.y_regions[13]
            y_pad = self.ctx.input.touch.y_regions[14] - y_offset
        else:
            y_offset = self.y_offset + 13 * self.y_pad
            y_pad = self.y_pad
        x_offset = self.x_offset
        esc_x_offset = round(x_offset + 1.9 * self.x_pad)

        # case for non m5stickv
        if self.ctx.display.width() > 135:
            esc_x_offset = round(x_offset + 2.3 * self.x_pad)

        text_offset = y_offset + y_pad // 2 - self.ctx.display.font_height // 2
        self.ctx.display.draw_string(
            esc_x_offset, text_offset, t("Esc"), theme.no_esc_color
        )
        self.ctx.display.draw_string(
            round(x_offset + 8.4 * self.x_pad), text_offset, t("Go"), theme.go_color
        )
        # print border around buttons only on touch devices
        if self.ctx.input.touch is not None:
            self.ctx.display.fill_rectangle(
                x_offset,
                y_offset,
                12 * self.x_pad,
                1,
                theme.frame_color,
            )
            self.ctx.display.fill_rectangle(
                x_offset,
                y_offset + y_pad,
                12 * self.x_pad,
                1,
                theme.frame_color,
            )
            for _ in range(3):
                self.ctx.display.fill_rectangle(
                    x_offset,
                    y_offset,
                    1,
                    y_pad,
                    theme.frame_color,
                )
                x_offset += 6 * self.x_pad

    def _map_keys_array(self):
        """Maps an array of regions for keys to be placed in"""
        if self.ctx.input.touch is not None:
            x_region = self.x_offset
            for _ in range(13):
                self.ctx.input.touch.x_regions.append(x_region)
                x_region += self.x_pad
            y_region = self.y_offset
            for count in range(15):
                self.ctx.input.touch.y_regions.append(y_region)
                if count == 12:
                    y_region += self.y_pad // 4
                elif count == 13:
                    y_region += self.y_pad * 7 // 4
                else:
                    y_region += self.y_pad

    def _draw_disabled(self, w24=False):
        """Draws disabled section where checksum is automatically filled"""
        if not w24:
            self.ctx.display.fill_rectangle(
                self.x_offset + 8 * self.x_pad,
                self.y_offset + 11 * self.y_pad,
                4 * self.x_pad,
                self.y_pad,
                theme.frame_color,
            )
            self.ctx.display.fill_rectangle(
                self.x_offset + 7 * self.x_pad,
                self.y_offset + 11 * self.y_pad,
                1 * self.x_pad,
                self.y_pad,
                theme.disabled_color,
            )
        else:
            self.ctx.display.fill_rectangle(
                self.x_offset + 4 * self.x_pad,
                self.y_offset + 11 * self.y_pad,
                8 * self.x_pad,
                self.y_pad,
                theme.frame_color,
            )
            self.ctx.display.fill_rectangle(
                self.x_offset + 3 * self.x_pad,
                self.y_offset + 11 * self.y_pad,
                1 * self.x_pad,
                self.y_pad,
                theme.disabled_color,
            )

    def check_sum(self, tiny_seed_numbers):
        """Dinamically calculates checksum"""
        # Inspired in Jimmy Song's HDPrivateKey.from_mnemonic() method
        binary_seed = bytearray()
        offset = 0
        for tiny_seed_number in tiny_seed_numbers:
            index = tiny_seed_number - 1 if tiny_seed_number > 1 else 0
            remaining = 11
            while remaining > 0:
                bits_needed = 8 - offset
                if remaining == bits_needed:
                    if bits_needed == 8:
                        binary_seed.append(index)
                    else:
                        binary_seed[-1] |= index
                    offset = 0
                    remaining = 0
                elif remaining > bits_needed:
                    if bits_needed == 8:
                        binary_seed.append(index >> (remaining - 8))
                    else:
                        binary_seed[-1] |= index >> (remaining - bits_needed)
                    remaining -= bits_needed
                    offset = 0
                    # lop off the top 8 bits
                    index &= (1 << remaining) - 1
                else:
                    binary_seed.append(index << (8 - remaining))
                    offset = remaining
                    remaining = 0
        checksum_length_bits = len(tiny_seed_numbers) * 11 // 33
        num_remainder = checksum_length_bits % 8
        if num_remainder:
            checksum_length = checksum_length_bits // 8 + 1
            bits_to_ignore = 8 - num_remainder
        else:
            checksum_length = checksum_length_bits // 8
            bits_to_ignore = 0
        raw = bytes(binary_seed)
        data = raw[:-checksum_length]
        computed_checksum = bytearray(hashlib.sha256(data).digest()[:checksum_length])
        computed_checksum[-1] &= 256 - (1 << (bits_to_ignore + 1) - 1)
        checksum = int.from_bytes(computed_checksum, "big")
        checksum = checksum >> (8 - checksum_length_bits)
        return checksum

    def toggle_bit(self, word, bit):
        """Toggle bit state according to pressed index"""
        return word ^ (1 << bit)

    def to_words(self, tiny_seed_numbers):
        """Converts a list of numbers 1-2048 to a list of respective BIP39 words"""
        words = []
        for number in tiny_seed_numbers:
            words.append(WORDLIST[number - 1])
        return words

    def _auto_checksum(self, word_numbers):
        """Automatically modify last word do add checksum"""
        checksum = self.check_sum(word_numbers)
        if len(word_numbers) == 12:
            word_numbers[11] -= 1
            word_numbers[11] &= 0b11111110000
            word_numbers[11] += checksum + 1
        else:
            word_numbers[23] -= 1
            word_numbers[23] &= 0b11100000000
            word_numbers[23] += checksum + 1
        return word_numbers

    def _new_index(self, index, btn, w24, page):
        def _last_editable_bit():
            if w24:
                if page == 0:
                    return TS_LAST_BIT_NO_CS
                return TS_LAST_BIT_24W_CS
            return TS_LAST_BIT_12W_CS

        if btn == BUTTON_PAGE:
            if index >= TS_GO_POSITION:
                index = 0
            elif index >= TS_ESC_END_POSITION:
                index = TS_GO_POSITION
            elif index >= _last_editable_bit():
                index = TS_ESC_END_POSITION
            else:
                index += 1
        elif btn == BUTTON_PAGE_PREV:
            if index <= 0:
                index = TS_GO_POSITION
            elif index <= _last_editable_bit():
                index -= 1
            elif index <= TS_ESC_END_POSITION:
                if w24:
                    if not page:
                        index = TS_LAST_BIT_NO_CS
                    else:
                        index = TS_LAST_BIT_24W_CS
                else:
                    index = TS_LAST_BIT_12W_CS
            elif index <= TS_GO_POSITION:
                index = TS_ESC_END_POSITION
        return index

    def enter_tiny_seed(self, w24=False, seed_numbers=None, scanning_24=False):
        """UI to manually enter a Tiny Seed"""

        def _editable_bit():
            if w24:
                if page == 0:
                    if index <= TS_LAST_BIT_NO_CS:
                        return True
                elif index <= TS_LAST_BIT_24W_CS:
                    return True
            elif index <= TS_LAST_BIT_12W_CS:
                return True
            return False

        index = 0
        if seed_numbers:
            tiny_seed_numbers = seed_numbers
            # move index to Go position
            index = TS_GO_POSITION
        elif w24:
            tiny_seed_numbers = [2048] * 23 + [1]
        else:
            tiny_seed_numbers = [2048] * 11 + [433]
        btn = None
        self._map_keys_array()
        page = 0
        while True:
            self._draw_labels(page)
            self._draw_grid()
            if not w24 or page:
                self._draw_disabled(w24)
                tiny_seed_numbers = self._auto_checksum(tiny_seed_numbers)
            self._draw_punched(tiny_seed_numbers, page)
            self._draw_menu()
            if self.ctx.input.buttons_active:
                self._draw_index(index)
            btn = self.ctx.input.wait_for_button()
            if btn == BUTTON_TOUCH:
                btn = BUTTON_ENTER
                index = self.ctx.input.touch.current_index()
            if btn == BUTTON_ENTER:
                if index > TS_ESC_END_POSITION:  # go
                    if not w24 or (w24 and (page or scanning_24)):
                        if scanning_24:
                            return tiny_seed_numbers
                        return self.to_words(tiny_seed_numbers)
                    page += 1
                elif index >= TS_ESC_START_POSITION:  # ESC
                    self.ctx.display.clear()
                    if self.prompt(t("Are you sure?"), self.ctx.display.height() // 2):
                        break
                    self._map_keys_array()
                elif _editable_bit():
                    word_index = index // 12
                    word_index += page * 12
                    bit = 11 - (index % 12)
                    if bit == 11:
                        tiny_seed_numbers[word_index] = 2048
                    else:
                        tiny_seed_numbers[word_index] = (
                            self.toggle_bit(tiny_seed_numbers[word_index], bit) % 2048
                        )
                    if tiny_seed_numbers[word_index] == 0:
                        tiny_seed_numbers[word_index] = 2048
            index = self._new_index(index, btn, w24, page)
            self.ctx.display.clear()


class TinyScanner(Page):
    """Uses camera sensor to detect punch pattern on a Tiny Seed, in metal or paper"""

    def __init__(self, ctx):
        super().__init__(ctx, None)
        self.ctx = ctx
        # Capturing flag used for first page of 24 words seed
        self.capturing = False
        # X, Y array map for punched area
        self.x_regions = []
        self.y_regions = []
        self.time_frame = time.ticks_ms()
        self.previous_seed_numbers = [1] * 12
        self.tiny_seed = TinySeed(self.ctx)

    def _map_punches_region(self, rect_size, page=0):
        # Think in portrait mode, with Tiny Seed tilted 90 degrees
        self.x_regions = []
        self.y_regions = []
        if not page:
            if board.config["type"].startswith("amigo"):
                # Amigo has mirrored coordinates
                x_offset = rect_size[0] + (rect_size[2] * 39) / 345
                y_offset = rect_size[1] + (rect_size[3] * 44) / 272
            else:
                x_offset = rect_size[0] + (rect_size[2] * 65) / 345
                y_offset = rect_size[1] + (rect_size[3] * 17) / 272
        else:
            if board.config["type"].startswith("amigo"):
                x_offset = rect_size[0] + (rect_size[2] * 42) / 345
                y_offset = rect_size[1] + (rect_size[3] * 41) / 272
            else:
                x_offset = rect_size[0] + (rect_size[2] * 62) / 345
                y_offset = rect_size[1] + (rect_size[3] * 22) / 272
        self.x_regions.append(int(x_offset))
        self.y_regions.append(int(y_offset))
        x_pad = rect_size[2] * 240 / (12 * 345)
        y_pad = rect_size[3] * 210 / (12 * 272)
        for _ in range(12):
            x_offset += x_pad
            y_offset += y_pad
            self.x_regions.append(int(round(x_offset)))
            self.y_regions.append(int(round(y_offset)))

    def _valid_numbers(self, data):
        for n in data:
            if not n or n > 2048:
                return False
        return True

    def _gradient_corners(self, rect, img):
        """Calcule histogram for four corners of tinyseed to be later
        used as a gradient reference threshold"""

        # Regions: Upper left, upper right, lower left and lower right
        # are corner fractions of main TinySeed rectangle
        if not board.config["type"].startswith("amigo"):
            region_ul = (
                rect[0] + rect[2] // 8,
                rect[1] + rect[3] // 30,
                rect[2] // 4,
                rect[3] // 4,
            )
            region_ur = (
                rect[0] + 8 * rect[2] // 11,
                rect[1] + rect[3] // 30,
                rect[2] // 4,
                rect[3] // 4,
            )
            region_ll = (
                rect[0] + rect[2] // 8,
                rect[1] + (rect[3] * 5) // 7,
                rect[2] // 4,
                rect[3] // 4,
            )
            region_lr = (
                rect[0] + 8 * rect[2] // 11,
                rect[1] + (rect[3] * 5) // 7,
                rect[2] // 4,
                rect[3] // 4,
            )
        else:  # Amigo has mirrored coordinates
            region_ul = (
                rect[0] + 7 * rect[2] // 11,
                rect[1] + (rect[3] * 5) // 7,
                rect[2] // 4,
                rect[3] // 4,
            )
            region_ur = (
                rect[0] + rect[2] // 30,
                rect[1] + (rect[3] * 5) // 7,
                rect[2] // 4,
                rect[3] // 4,
            )
            region_ll = (
                rect[0] + 7 * rect[2] // 11,
                rect[1] + rect[3] // 8,
                rect[2] // 4,
                rect[3] // 4,
            )
            region_lr = (
                rect[0] + rect[2] // 30,
                rect[1] + rect[3] // 8,
                rect[2] // 4,
                rect[3] // 4,
            )

        # # Debug gradient corners
        # # Warning: These rectangles affect detection
        # img.draw_rectangle(region_ul, color=lcd.YELLOW, thickness=2)
        # img.draw_rectangle(region_ur, color=lcd.ORANGE, thickness=2)
        # img.draw_rectangle(region_ll, color=lcd.RED, thickness=2)
        # img.draw_rectangle(region_lr, color=lcd.MAGENTA, thickness=2)

        # # Debug corners luminosity
        # gradient_bg_ul = img.get_statistics(roi=region_ul).median()
        # gradient_bg_ur = img.get_statistics(roi=region_ur).median()
        # gradient_bg_ll = img.get_statistics(roi=region_ll).median()
        # gradient_bg_lr = img.get_statistics(roi=region_lr).median()
        # img.draw_string(10,40,str(gradient_bg_ul))
        # img.draw_string(70,40,str(gradient_bg_ur))
        # img.draw_string(10,55,str(gradient_bg_ll))
        # img.draw_string(70,55,str(gradient_bg_lr))

        return (
            img.get_statistics(roi=region_ul).median(),
            img.get_statistics(roi=region_ur).median(),
            img.get_statistics(roi=region_ll).median(),
            img.get_statistics(roi=region_lr).median(),
        )

    def _gradient_value(self, index, gradient_corners):
        """Calculates a reference threshold according to a linear
        interpolation gradient of luminosity from 4 corners of Tiny Seed"""
        (
            gradient_bg_ul,
            gradient_bg_ur,
            gradient_bg_ll,
            gradient_bg_lr,
        ) = gradient_corners

        y_position = index % 12
        x_position = index // 12
        gradient_upper_x = (
            gradient_bg_ul * (11 - x_position) + gradient_bg_ur * x_position
        ) // 11
        gradient_lower_x = (
            gradient_bg_ll * (11 - x_position) + gradient_bg_lr * x_position
        ) // 11
        gradient = (
            gradient_upper_x * (11 - y_position) + gradient_lower_x * y_position
        ) // 11

        # Average filter
        # Here you can change the relevance of the gradient vs medium luminance as a reference
        filtered = (
            gradient_bg_ul + gradient_bg_ur + gradient_bg_ll + gradient_bg_lr
        )  # weight 4/6 - 67% average
        filtered += 2 * gradient  # weight 2/6 = 33% raw gradient
        filtered //= 6
        return filtered

        # return gradient #pure gradient

    def _detect_tiny_seed(self, img):
        """Detects Tiny Seed as a bright blob against a dark surface"""

        def _choose_rect(rects):
            for rect in rects:
                aspect = rect[2] / rect[3]
                if (
                    rect[0]
                    and rect[1]
                    and (rect[0] + rect[2]) < img.width()
                    and (rect[1] + rect[3]) < img.height()
                    and aspect_low < aspect < 1.3
                ):
                    return rect
            return None

        # Big lenses cameras seems to distor aspect ratio to 1.1
        aspect_low = 1.1 if self.ctx.camera.cam_id in (OV2640_ID, OV5642_ID) else 1.2
        stats = img.get_statistics()
        # # Debug stats
        # img.draw_string(10,10,"Mean:"+str(stats.mean()))
        # img.draw_string(10,30,"Median:"+str(stats.median()))
        # img.draw_string(10,50,"UQ:"+str(stats.uq()))
        # img.draw_string(10,70,"LQ:"+str(stats.lq()))

        # Luminosity
        luminosity = stats.median() * 2
        attempts = 3
        while attempts:
            blob_threshold = [
                (luminosity, 255),
            ]
            blobs = img.find_blobs(
                blob_threshold,
                x_stride=50,
                y_stride=50,
                area_threshold=10000,
            )
            # Debug blobs
            # for blob in blobs:
            #     img.draw_rectangle(blob.rect(), color=(255,125*attempts,0), thickness=3)
            rects = []
            for blob in blobs:
                rects.append(blob.rect())
            rect = _choose_rect(rects)
            if rect:
                break
            attempts -= 1
            # Reduce luminosity threshold to try again
            luminosity *= 7
            luminosity //= 10
        # # Debug attempts
        # img.draw_string(10,10,"Attempts:"+str(attempts))
        if rect:
            # Outline Tiny Seed
            outline = (
                rect[0] - 1,
                rect[1] - 1,
                rect[2] + 1,
                rect[3] + 1,
            )
            if self.capturing:
                img.draw_rectangle(outline, lcd.WHITE, thickness=4)
            else:
                img.draw_rectangle(outline, lcd.WHITE, thickness=2)
        return rect

    def _draw_grid(self, img):
        if self.ctx.display.height() > 240:
            for i in range(13):
                img.draw_line(
                    self.x_regions[i],
                    self.y_regions[0],
                    self.x_regions[i],
                    self.y_regions[-1],
                    lcd.WHITE,
                )
                img.draw_line(
                    self.x_regions[0],
                    self.y_regions[i],
                    self.x_regions[-1],
                    self.y_regions[i],
                    lcd.WHITE,
                )

    def _detect_and_draw_punches(self, img, gradient_corners):
        """Applies gradient threshold to detect punched(black painted) bits"""
        page_seed_numbers = [0] * 12
        index = 0
        pad_x = self.x_regions[1] - self.x_regions[0]
        pad_y = self.y_regions[1] - self.y_regions[0]
        if pad_x < 4 or pad_y < 4:  # Punches are too small
            return page_seed_numbers
        y_map = self.y_regions[0:-1]
        x_map = self.x_regions[0:-1]
        if board.config["type"].startswith("amigo"):
            x_map.reverse()
        else:
            y_map.reverse()
        # Think in portrait mode, with Tiny Seed tilted 90 degrees
        # Loop ahead will sweep TinySeed bits/dots and evaluate its luminosity
        for x in x_map:
            for y in y_map:
                # Define the dot rectangle area to be evaluated
                eval_rect = (x + 2, y + 2, pad_x - 3, pad_y - 3)
                # Evaluate dot's median luminosity
                dot_l = img.get_statistics(roi=eval_rect).median()

                # # Debug gradient
                # if index == 0:
                #     img.draw_string(10,10,"0:"+str(gradient_ref))
                # if index == 11:
                #     img.draw_string(10,25,"11:"+str(gradient_ref))
                # if index == 132:
                #     img.draw_string(70,10,"132:"+str(gradient_ref))
                # if index == 143:
                #     img.draw_string(70,25,"143:"+str(gradient_ref))

                # Defines a threshold to evaluate if the dot is considered punched
                punch_threshold = (
                    self._gradient_value(index, gradient_corners) * 4
                ) // 5  # ~-20%
                # Sensor image will be downscaled on small displays
                punch_thickness = 1 if self.ctx.display.height() > 240 else 2
                # If the dot is punched, draws a rectangle and toggle respective bit
                if dot_l < punch_threshold:
                    _ = img.draw_rectangle(
                        eval_rect, thickness=punch_thickness, color=lcd.WHITE
                    )
                    word_index = index // 12
                    bit = 11 - (index % 12)
                    page_seed_numbers[word_index] = self.tiny_seed.toggle_bit(
                        page_seed_numbers[word_index], bit
                    )
                index += 1
        # print(page_seed_numbers)
        return page_seed_numbers

    def _set_camera_sensitivity(self):
        if self.ctx.camera.cam_id == OV7740_ID:
            # reduce sensitivity to avoid saturated reflactions
            # luminance high level, default=0x78
            sensor.__write_reg(0x24, 0x48)  # pylint: disable=W0212
            # luminance low level, default=0x68
            sensor.__write_reg(0x25, 0x44)  # pylint: disable=W0212
            # Disable frame integrtation (night mode)
            sensor.__write_reg(0x15, 0x00)  # pylint: disable=W0212

    def _run_camera(self):
        """Turns camera on, returns True if image fills full screen"""
        sensor.run(1)
        self.ctx.display.clear()
        if self.ctx.display.width() < 320:
            full_screen = True
        else:
            full_screen = False
            self.ctx.display.outline(
                39,
                1,
                241,
                321,
            )
        self.ctx.display.to_landscape()

        return full_screen

    def _exit_camera(self):
        sensor.run(0)
        self.ctx.display.to_portrait()
        self.ctx.display.clear()

    def _check_buttons(self, w24, page):
        enter_or_touch = self.ctx.input.enter_event() or self.ctx.input.touch_event()
        if w24:
            if page == 0 and enter_or_touch:
                self.capturing = True
        elif enter_or_touch:
            return True
        if self.ctx.input.page_event() or self.ctx.input.page_prev_event():
            return True
        return False

    def _process_12w_scan(self, page_seed_numbers):
        if (
            self.tiny_seed.check_sum(page_seed_numbers)
            == (page_seed_numbers[11] - 1) & 0b00000001111
        ):
            if page_seed_numbers == self.previous_seed_numbers:
                self._exit_camera()
                self.ctx.display.draw_centered_text(
                    t("Review scanned data, edit if necessary")
                )
                self.ctx.input.wait_for_button()
                self.ctx.display.clear()
                words = self.tiny_seed.enter_tiny_seed(seed_numbers=page_seed_numbers)
                if words:  # If words confirmed
                    return words
                # Else esc command was given, turn camera on again and reset words
                self.flash_text(
                    t("Scanning words 1-12 again") + "\n\n" + t("Wait for the capture")
                )
                self._run_camera()
                self.previous_seed_numbers = [1] * 12
            else:
                self.previous_seed_numbers = page_seed_numbers
        return None

    def _process_24w_pg0_scan(self, page_seed_numbers):
        if page_seed_numbers == self.previous_seed_numbers and self.capturing:
            self._exit_camera()
            self.ctx.display.draw_centered_text(
                t("Review scanned data, edit if necessary")
            )
            self.ctx.input.wait_for_button()
            self.ctx.display.clear()
            words = self.tiny_seed.enter_tiny_seed(True, page_seed_numbers, True)
            self.capturing = False
            if words is not None:  # Fisrt 12 words confirmed, moving to 13-24
                self.flash_text(
                    t("Scanning words 13-24") + "\n\n" + t("Wait for the capture")
                )
                self._run_camera()
                return words
            # Esc command was given
            self.flash_text(
                t("Scanning words 1-12 again") + "\n\n" + t("TOUCH or ENTER to capture")
            )
            self._run_camera()  # Run camera and rotate screen after message was given
        elif self._valid_numbers(page_seed_numbers):
            self.previous_seed_numbers = page_seed_numbers
        return None

    def scanner(self, w24=False):
        """Uses camera sensor to scan punched pattern on Tiny Seed format"""
        page = 0
        if w24:
            w24_seed_numbers = [0] * 24
        self.previous_seed_numbers = [1] * 12

        self.ctx.display.clear()
        message = t("Wait for the capture")
        if w24 and page == 0:
            message = t("TOUCH or ENTER to capture")
        self.ctx.display.draw_centered_text(message)
        precamera_ticks = time.ticks_ms()
        self.ctx.camera.initialize_sensor(grayscale=True)
        self._set_camera_sensitivity()
        full_screen = self._run_camera()
        postcamera_ticks = time.ticks_ms()
        # check how much time camera took to retain message on the screen
        if precamera_ticks + FLASH_MSG_TIME > postcamera_ticks:
            time.sleep_ms(precamera_ticks + FLASH_MSG_TIME - postcamera_ticks)
        del message, precamera_ticks, postcamera_ticks
        self.ctx.input.flush_events()
        # # Debug FPS 1/4
        # clock = time.clock()
        # fps = 0
        while True:
            # # Debug FPS 2/4
            # clock.tick()
            wdt.feed()
            page_seed_numbers = None
            img = self.ctx.camera.snapshot()
            rect = self._detect_tiny_seed(img)
            if rect:
                gradient_corners = self._gradient_corners(rect, img)
                # print(gradient_corners)
                # map_regions
                self._map_punches_region(rect, page)
                page_seed_numbers = self._detect_and_draw_punches(img, gradient_corners)
                self._draw_grid(img)
            if board.config["type"] == "m5stickv":
                img.lens_corr(strength=1.0, zoom=0.56)
            # # Debug FPS 3/4
            # img.draw_string(10,100,str(fps))
            if full_screen:
                lcd.display(img)
            else:
                lcd.display(img, oft=(2, 40))  # Centralize image in Amigo

            if page_seed_numbers:
                if w24:
                    if page == 0:  # Scanning first 12 words (page 0)
                        first_page = self._process_24w_pg0_scan(page_seed_numbers)
                        if first_page:  # If page 0 confirmed, move to page 1
                            w24_seed_numbers[0:12] = first_page
                            page = 1
                    else:  # Scanning words 13-24 (page 1)
                        w24_seed_numbers[12:24] = page_seed_numbers
                        if (
                            self.tiny_seed.check_sum(w24_seed_numbers)
                            == (w24_seed_numbers[23] - 1) & 0b00011111111
                        ):
                            if page_seed_numbers == self.previous_seed_numbers:
                                self._exit_camera()
                                return self.tiny_seed.to_words(w24_seed_numbers)
                            self.previous_seed_numbers = page_seed_numbers
                else:
                    words = self._process_12w_scan(page_seed_numbers)
                    if words:
                        return words
            if self._check_buttons(w24, page):
                break
            # # Debug FPS 4/4
            # fps = clock.fps()

        self._exit_camera()
        return None
