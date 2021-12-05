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
import time
import math
import lcd
from machine import I2C

DEFAULT_PADDING = const(10)

MAX_BACKLIGHT = const(8)
MIN_BACKLIGHT = const(1)

DEL = ( 'Del' )
GO  = ( 'Go' )

class Display:
    """Display is a singleton interface for interacting with the device's display"""

    def __init__(self, font_size=7):
        self.font_size = font_size
        self.rot = 0
        self.initialize_lcd()
        self.i2c = I2C(I2C.I2C0, freq=400000, scl=28, sda=29)
        self.set_backlight(MIN_BACKLIGHT)

    def initialize_lcd(self):
        """Initializes the LCD"""
        lcd.init(type=3)
        lcd.register(0x3A, 0x05)
        lcd.register(0xB2, [0x05, 0x05, 0x00, 0x33, 0x33])
        lcd.register(0xB7, 0x23)
        lcd.register(0xBB, 0x22)
        lcd.register(0xC0, 0x2C)
        lcd.register(0xC2, 0x01)
        lcd.register(0xC3, 0x13)
        lcd.register(0xC4, 0x20)
        lcd.register(0xC6, 0x0F)
        lcd.register(0xD0, [0xA4, 0xA1])
        lcd.register(0xD6, 0xA1)
        lcd.register(0xE0,
            [0x23, 0x70, 0x06, 0x0C, 0x08,
             0x09, 0x27, 0x2E, 0x34, 0x46,
             0x37, 0x13, 0x13, 0x25, 0x2A]
        )
        lcd.register(0xE1,
            [0x70, 0x04, 0x08, 0x09, 0x07, 0x03, 0x2C,
             0x42, 0x42, 0x38, 0x14, 0x14, 0x27, 0x2C]
        )

    def line_height(self):
        """Returns the pixel height of a line on the display"""
        return self.font_size * 2

    def width(self):
        """Returns the width of the display, taking into account rotation"""
        if self.rot == 0:
            return lcd.height()
        return lcd.width()

    def height(self):
        """Returns the height of the display, taking into account rotation"""
        if self.rot == 0:
            return lcd.width()
        return lcd.height()

    def qr_data_width(self):
        """Returns a smaller width for the QR to be generated
           within, which will then be scaled up to fit the display's width.
           We do this because the QR would be too dense to be readable
           by most devices otherwise.
        """
        return self.width() // 4

    def rotation(self, rot):
        """Returns the rotation of the display"""
        lcd.rotation(rot)
        self.rot = rot

    def to_landscape(self):
        """Changes the rotation of the display to landscape"""
        self.clear()
        self.rotation(2)

    def to_portrait(self):
        """Changes the rotation of the display to portrait"""
        self.clear()
        self.initialize_lcd()
        self.rot = 0

    def to_lines(self, text, word_wrap=True, padding=DEFAULT_PADDING):
        """Takes a string of text and converts it to lines to display on
           the screen, taking into account padding
        """
        screen_width = self.width() - padding * 2
        lines = []
        columns = math.floor(screen_width / self.font_size)
        cur_column = 0
        for i, char in enumerate(text):
            if word_wrap and char == ' ':
                next_word_end = text.find(' ', i+1)
                if next_word_end == -1:
                    next_word_end = text.find('\n', i+1)
                    if next_word_end == -1:
                        next_word_end = len(text)
                next_word = text[i+1:next_word_end]
                if len(next_word) < columns:
                    if cur_column + 1 + len(next_word) >= columns:
                        cur_column = 0
            if char == '\n':
                cur_column = 0
            cur_column = (cur_column + 1) % columns
            if cur_column == 1:
                if char in (' ', '\n'):
                    char = ''
                lines.append(char)
            else:
                lines[len(lines)-1] += char
        return lines

    def clear(self):
        """Clears the display"""
        lcd.clear()

    def draw_hcentered_text(self, text, offset_y=DEFAULT_PADDING, color=lcd.WHITE,
                            word_wrap=True, padding=DEFAULT_PADDING):
        """Draws text horizontally-centered on the display, taking padding
           into account, at the given offset_y
        """
        screen_width = self.width() - padding * 2
        lines = self.to_lines(text, word_wrap, padding)
        for i, line in enumerate(lines):
            offset_x = max(0, (screen_width - (self.font_size * len(line))) // 2) + 1
            lcd.draw_string(offset_x, offset_y + (i * self.line_height()), line, color, lcd.BLACK)

    def draw_centered_text(self, text, color=lcd.WHITE, word_wrap=True, padding=DEFAULT_PADDING):
        """Draws text horizontally and vertically centered on the display,
           taking padding into account
        """
        lines = self.to_lines(text, word_wrap, padding)
        screen_height = self.height() - padding * 2
        lines_height = len(lines) * self.line_height()
        offset_y = max(0, (screen_height - lines_height) // 2)
        self.draw_hcentered_text(text, offset_y, color, word_wrap, padding)

    def flash_text(self, text, color=lcd.WHITE, word_wrap=True, padding=DEFAULT_PADDING,
                   duration=3000):
        """Flashes text centered on the display for duration ms"""
        self.clear()
        self.draw_centered_text(text, color, word_wrap, padding)
        time.sleep_ms(duration)
        self.clear()

    def draw_qr_code(self, offset_y, qr_code):
        """Draws a QR code on the screen"""
        # Add a 1px white border around the code before displaying
        qr_code = qr_code.strip()
        lines = qr_code.split('\n')
        size = len(lines)
        new_lines = ['0' * (size + 2)]
        for line in lines:
            new_lines.append('0' + line + '0')
        new_lines.append('0' * (size + 2))
        qr_code = '\n'.join(new_lines)
        lcd.draw_qr_code(offset_y, qr_code, self.width())

    def set_backlight(self, level):
        """Sets the backlight of the display to the given power level, from 0 to 8"""
        # Ranges from 0 to 8
        level = max(0, min(level, 8))
        val = (level+7) << 4
        self.i2c.writeto_mem(0x34, 0x91, int(val))
