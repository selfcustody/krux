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
import board
from machine import I2C

PORTRAIT = 1
LANDSCAPE = 2
DEFAULT_PADDING = 10
FONT_SIZE = 7
FONT_WIDTH = 7
M5_HIDDEN_H_PIXELS = 14
M5_HIDDEN_V_PIXELS = 14

if board.config['type'] == "bit":
    FONT_SIZE = 9
    FONT_WIDTH = 8 #todo test

MAX_BACKLIGHT = 8
MIN_BACKLIGHT = 1

DEL = ( 'Del' )
GO  = ( 'Go' )

class Display:
    """Display is a singleton interface for interacting with the device's display"""

    def __init__(self):
        self.font_size = FONT_SIZE
        self.font_width = FONT_WIDTH
        self.initialize_lcd()
        self.i2c = None

    def initialize_lcd(self):
        """Initializes the LCD"""
        if board.config['lcd']['lcd_type'] == 3:
            lcd.init(type=board.config['lcd']['lcd_type'])
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
            self.initialize_backlight()
        else:
            lcd.init()
        self.rotation(PORTRAIT)


    def initialize_backlight(self):
        """Initializes the backlight"""
        if 'I2C_SCL' not in board.config['krux.pins'] or 'I2C_SDA' not in board.config['krux.pins']:
            return
        self.i2c = I2C(
            I2C.I2C0,
            freq=400000,
            scl=board.config['krux.pins']['I2C_SCL'],
            sda=board.config['krux.pins']['I2C_SDA']
        )
        self.set_backlight(MIN_BACKLIGHT)

    def qr_offset(self):
        """Retuns y offset to subtittle QR codes"""
        if board.config['type']=='m5stickv':
            return 138
        elif board.config['type'] == "bit":
            return 223

    
    def line_height(self):
        """Returns the pixel height of a line on the display"""
        return self.font_size * 2

    def width(self):
        """Returns the width of the display, taking into account rotation"""
        if self.rot == LANDSCAPE:
            return lcd.height()
        return lcd.width()

    def screen_width(self):
        """Returns usable screen width"""
        if board.config['type']=='m5stickv':
            return self.width() - M5_HIDDEN_H_PIXELS
        else: #other boards make use of full resolution
            return self.width()

    def height(self):
        """Returns the height of the display, taking into account rotation"""
        if self.rot == LANDSCAPE:
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
        self.rotation(LANDSCAPE)

    def to_portrait(self):
        """Changes the rotation of the display to portrait"""
        self.clear()
        self.rotation(PORTRAIT)

    def to_lines(self, text, padding=DEFAULT_PADDING):
        """Takes a string of text and converts it to lines to display on
           the screen, taking into account padding
        """
        columns = math.floor(self.screen_width() / self.font_width)
        words = []
        for word in text.split(' '):
            subwords = word.split('\n')
            for i, subword in enumerate(subwords):
                if len(subword) > columns:
                    j = 0
                    while j < len(subword):
                        words.append(subword[j:j + columns])
                        j += columns
                else:
                    words.append(subword)

                if len(subwords) > 1 and i < len(subwords) - 1:
                    words.append('\n')

        num_words = len(words)

        # calculate cost of all pairs of words
        cost_between = [[0 for x in range(num_words+1)] for x in range(num_words+1)]
        for i in range(1, num_words+1):
            for j in range(i, num_words+1):
                for k in range(i, j+1):
                    cost_between[i][j] += (len(words[k-1]) + 1)
                cost_between[i][j] -= 1
                cost_between[i][j] = columns - cost_between[i][j]
                if cost_between[i][j] < 0:
                    cost_between[i][j] = float('inf')
                cost_between[i][j] = cost_between[i][j]**2

        # find optimal number of words on each line
        indexes = [0 for _ in range(num_words+1)]
        cost = [0 for _ in range(num_words+1)]
        cost[0] = 0
        for j in range(1, num_words+1):
            cost[j] = float('inf')*float('inf')
            for i in range(1, j+1):
                if cost[i-1] + cost_between[i][j] < cost[j]:
                    cost[j] = cost[i-1] + cost_between[i][j]
                    indexes[j] = i

        def build_lines(words, num_words, indexes):
            lines = []
            start = indexes[num_words]
            end = num_words
            if start != 1:
                lines.extend(build_lines(words, start - 1, indexes))
            line = ''
            for i in range(start, end+1):
                if words[i-1] == '\n':
                    lines.append(line)
                    line = ''
                else:
                    line += (' ' if len(line) > 0 else '') + words[i-1]
            if len(line) > 0:
                lines.append(line)
            return lines
        return build_lines(words, num_words, indexes)

    def clear(self):
        """Clears the display"""
        lcd.clear()

    def draw_hcentered_text(self, text, offset_y=DEFAULT_PADDING, color=lcd.WHITE,
                            padding=DEFAULT_PADDING):
        """Draws text horizontally-centered on the display, taking padding
           into account, at the given offset_y
        """
        lines = text if isinstance(text, list) else self.to_lines(text, padding)
        for i, line in enumerate(lines):
            offset_x = (self.screen_width() - self.font_width * len(line)) // 2
            offset_x = max(0, offset_x)
            lcd.draw_string(offset_x, offset_y + (i * self.line_height()), line, color, lcd.BLACK)
            #print("of_x:"+str(offset_x)+" - len_line: "+str(len(line))+" - font: " +str(self.font_width))

    def draw_centered_text(self, text, color=lcd.WHITE, padding=DEFAULT_PADDING):
        """Draws text horizontally and vertically centered on the display,
           taking padding into account
        """
        lines = text if isinstance(text, list) else self.to_lines(text, padding)
        if board.config['type']=='m5stickv':
            screen_height = self.height() - M5_HIDDEN_V_PIXELS
        else: #other boards make use of full resolution
            screen_height = self.height()
        lines_height = len(lines) * self.line_height()
        offset_y = max(0, (screen_height - lines_height) // 2)
        self.draw_hcentered_text(text, offset_y, color, padding)

    def flash_text(self, text, color=lcd.WHITE, padding=DEFAULT_PADDING,
                   duration=3000):
        """Flashes text centered on the display for duration ms"""
        self.clear()
        self.draw_centered_text(text, color, padding)
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
        if not self.i2c:
            return
        # Ranges from 0 to 8
        level = max(0, min(level, 8))
        val = (level+7) << 4
        self.i2c.writeto_mem(0x34, 0x91, int(val))
