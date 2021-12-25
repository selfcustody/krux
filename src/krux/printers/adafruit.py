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
#*************************************************************************
# This is a Python library for the Adafruit Thermal Printer.
# Pick one up at --> http://www.adafruit.com/products/597
# These printers use TTL serial to communicate, 2 pins are required.
# IMPORTANT: On 3.3V systems (e.g. Raspberry Pi), use a 10K resistor on
# the RX pin (TX on the printer, green wire), or simply leave unconnected.
#
# Adafruit invests time and resources providing this open source code.
# Please support Adafruit and open-source hardware by purchasing products
# from Adafruit!
#
# Written by Limor Fried/Ladyada for Adafruit Industries.
# Python port by Phil Burgess for Adafruit Industries.
# MIT license, all text above must be included in any redistribution.
#*************************************************************************
import time
import board
from fpioa_manager import fm
from machine import UART
from ..settings import Settings
from .printer import Printer

class ThermalPrinter(Printer):
    """ThermalPrinter is a minimal wrapper around a serial connection to
       to the Adafruit line of thermal printers
    """

    def __init__(self):
        if 'UART2_TX' not in board.config['krux.pins'] or 'UART2_RX' not in board.config['krux.pins']:
            raise ValueError('missing required ports')
        fm.register(board.config['krux.pins']['UART2_TX'], fm.fpioa.UART2_TX, force=False)
        fm.register(board.config['krux.pins']['UART2_RX'], fm.fpioa.UART2_RX, force=False)
        # Calculate time to issue one byte to the printer.
        # 11 bits (not 8) to accommodate idle, start and
        # stop bits.  Idle time might be unnecessary, but
        # erring on side of caution here.
        self.byte_time = 11.0 / float(Settings.Printer.Adafruit.baudrate)
        self.resume_time = 0.0
        self.char_height = 24
        self.uart_conn = UART(
            Settings.Printer.Adafruit.port,
            Settings.Printer.Adafruit.baudrate
        )
        # The printer can't start receiving data immediately
        # upon power up -- it needs a moment to cold boot
        # and initialize.  Allow at least 1/2 sec of uptime
        # before printer can receive data.
        self.timeout_set(0.5)

        if not self.has_paper():
            raise ValueError('missing paper')

        self.setup()

    def setup(self):
        """Sets up the connection to the printer and sets default settings"""
        # Wake up the printer to get ready for printing
        self.timeout_set(0)
        self.write_bytes(255)
        time.sleep(0.05)            # 50 ms
        self.write_bytes(27, 118, 0) # Sleep off (important!)
        
        # Reset the printer
        self.write_bytes(27, 64) # Esc @ = init command
        # Configure tab stops on recent printers
        self.write_bytes(27, 68)         # Set tab stops
        self.write_bytes(4, 8, 12, 16) # every 4 columns,
        self.write_bytes(20, 24, 28, 0) # 0 is end-of-list.

        # Description of print settings from p. 23 of manual:
        # ESC 7 n1 n2 n3 Setting Control Parameter Command
        # Decimal: 27 55 n1 n2 n3
        # max heating dots, heating time, heating interval
        # n1 = 0-255 Max heat dots, Unit (8dots), Default: 7 (64 dots)
        # n2 = 3-255 Heating time, Unit (10us), Default: 80 (800us)
        # n3 = 0-255 Heating interval, Unit (10us), Default: 2 (20us)
        # The more max heating dots, the more peak current
        # will cost when printing, the faster printing speed.
        # The max heating dots is 8*(n1+1).  The more heating
        # time, the more density, but the slower printing
        # speed.  If heating time is too short, blank page
        # may occur.  The more heating interval, the more
        # clear, but the slower printing speed.
        self.write_bytes(
            27,             # Esc
            55,             # 7 (print settings)
            11,             # Heat dots
            Settings.Printer.Adafruit.heat_time, # Lib default
            40)             # Heat interval

        # Description of print density from p. 23 of manual:
        # DC2 # n Set printing density
        # Decimal: 18 35 n
        # D4..D0 of n is used to set the printing density.
        # Density is 50% + 5% * n(D4-D0) printing density.
        # D7..D5 of n is used to set the printing break time.
        # Break time is n(D7-D5)*250us.
        # (Unsure of default values -- not documented)
        print_density = 10 # 100%
        print_break_time = 2 # 500 uS

        self.write_bytes(
            18, # DC2
            35, # Print density
            (print_break_time << 5) | print_density)
        self.dot_print_time = 0.03
        self.dot_feed_time = 0.0021

    def write_bytes(self, *args):
        """Writes bytes to the printer at a stable speed"""
        for arg in args:
            self.timeout_wait()
            self.timeout_set(len(args) * self.byte_time)
            self.uart_conn.write(arg if isinstance(arg, bytes) else bytes([arg]))

    def timeout_set(self, x):
        """Sets estimated completion time for a just-issued task."""
        self.resume_time = time.time() + x

    def timeout_wait(self):
        """Waits (if necessary) for the prior task to complete."""
        while (time.time() - self.resume_time) < 0:
            pass

    def feed(self, x=1):
        """Feeds paper through the machine x times"""
        self.write_bytes(27, 100, x)
        self.timeout_set(self.dot_feed_time * self.char_height)

    def has_paper(self):
        """Returns a boolean indicating if the printer has paper or not"""
        self.write_bytes(27, 118, 0)
        # Bit 2 of response seems to be paper status
        stat = ord(self.uart_conn.read(1)) & 0b00000100
        # If set, we have paper; if clear, no paper
        return stat == 0

    def qr_data_width(self):
        """Returns a smaller width for the QR to be generated
           within, which will then be scaled up to fit the paper's width.
           We do this because the QR would be too dense to be readable
           by most devices otherwise.
        """
        return Settings.Printer.Adafruit.paper_width // 6

    def clear(self):
        """Clears the printer's memory, resetting it"""
        # Reset the printer
        self.write_bytes(27, 64) # Esc @ = init command
        # Configure tab stops on recent printers
        self.write_bytes(27, 68)         # Set tab stops
        self.write_bytes(4, 8, 12, 16) # every 4 columns,
        self.write_bytes(20, 24, 28, 0) # 0 is end-of-list.
        # Perform a full hardware reset which clears both printer buffer and receive buffer.
        # A full reset can only be done by setting an image in nonvolatile memory, so
        # we will send a 1x1 image with 0 as its pixel value in order to initiate the reset
        self.write_bytes(28, 113, 1, 1, 0, 1, 0, 0)

    def print_qr_code(self, qr_code):
        """Prints a QR code, scaling it up as large as possible"""
        lines = qr_code.strip().split('\n')

        width = len(lines)
        height = len(lines)

        scale = Settings.Printer.Adafruit.paper_width // width
        for y in range(height):
            # Scale the line (width) by scaling factor
            line_y = ''.join([char * scale for char in lines[y]])
            line_bytes = int(line_y, 2).to_bytes((len(line_y) + 7) // 8, 'big')
            # Print height * scale lines out to scale by
            for _ in range(scale):
                self.write_bytes(18, 42, 1, len(line_bytes))
                self.write_bytes(line_bytes)
                self.timeout_set(self.dot_print_time)
        self.feed(3)
