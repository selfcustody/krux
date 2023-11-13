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
# *************************************************************************
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
# *************************************************************************
# pylint: disable=W0231
import time
from fpioa_manager import fm
from machine import UART

# from ..settings import CategorySetting, NumberSetting, SettingsNamespace
from ..krux_settings import Settings

# from ..krux_settings import t
from ..wdt import wdt
from . import Printer

INITIALIZE_WAIT_TIME = 500


class AdafruitPrinter(Printer):
    """AdafruitPrinter is a minimal wrapper around a serial connection to
    to the Adafruit line of thermal printers
    """

    def __init__(self):
        fm.register(
            Settings().hardware.printer.thermal.adafruit.tx_pin,
            fm.fpioa.UART2_TX,
            force=False,
        )
        fm.register(
            Settings().hardware.printer.thermal.adafruit.rx_pin,
            fm.fpioa.UART2_RX,
            force=False,
        )

        self.uart_conn = UART(
            UART.UART2, Settings().hardware.printer.thermal.adafruit.baudrate
        )

        self.character_height = 24
        self.byte_time = 1  # miliseconds
        self.dot_print_time = Settings().hardware.printer.thermal.adafruit.line_delay
        self.dot_feed_time = 2  # miliseconds

        if not self.has_paper():
            raise ValueError("missing paper")

    def write_bytes(self, *args):
        """Writes bytes to the printer at a stable speed"""
        for arg in args:
            wdt.feed()
            self.uart_conn.write(arg if isinstance(arg, bytes) else bytes([arg]))
            # Calculate time to issue one byte to the printer.
            # 11 bits (not 8) to accommodate idle, start and
            # stop bits.  Idle time might be unnecessary, but
            # erring on side of caution here.
            time.sleep_ms(self.byte_time)

    def feed(self, x=1):
        """Feeds paper through the machine x times"""
        while x > 0:
            x -= 1
            self.write_bytes(10)
            # Wait for the paper to feed
            time.sleep_ms(self.dot_feed_time * self.character_height)

    def has_paper(self):
        """Returns a boolean indicating if the printer has paper or not"""
        self.write_bytes(27, 118, 0)
        # Bit 2 of response seems to be paper status
        res = self.uart_conn.read(1)
        if res is None:
            return True  # If not set, won't raise value error
        stat = ord(res) & 0b00000100
        # If set, we have paper; if clear, no paper
        return stat == 0

    def qr_data_width(self):
        """Returns a smaller width for the QR to be generated
        within, which will then be scaled up to fit the paper's width.
        We do this because the QR would be too dense to be readable
        by most devices otherwise.
        """
        return 33

    def clear(self):
        """Clears the printer's memory, resetting it"""
        # Perform a full hardware reset which clears both printer buffer and receive buffer.
        # A full reset can only be done by setting an image in nonvolatile memory, so
        # we will send a 1x1 image with 0 as its pixel value in order to initiate the reset
        self.write_bytes(28, 113, 1, 1, 0, 1, 0, 0)
        # Reset the printer
        self.write_bytes(27, 64)  # Esc @ = init command
        # Configure tab stops on recent printers
        self.write_bytes(27, 68)  # Set tab stops
        self.write_bytes(4, 8, 12, 16)  # every 4 columns,
        self.write_bytes(20, 24, 28, 0)  # 0 is end-of-list.

    def print_qr_code(self, qr_code):
        """Prints a QR code, scaling it up as large as possible"""
        from ..qr import get_size

        size = get_size(qr_code)

        scale = Settings().hardware.printer.thermal.adafruit.paper_width // size
        scale *= Settings().hardware.printer.thermal.adafruit.scale  # Scale in %
        scale //= 200  # 100% * 2 because printer will scale 2X later to save data
        # Being at full size sometimes makes prints more faded (can't apply too much heat?)

        line_bytes_size = (size * scale + 7) // 8  # amount of bytes per line
        self.set_bitmap_mode(line_bytes_size, size * scale, 3)
        for row in range(size):
            byte = 0
            line_bytes = bytearray()
            for col in range(size):
                bit_index = row * size + col
                bit = qr_code[bit_index >> 3] & (1 << (bit_index % 8))
                for i in range(scale):
                    byte <<= 1
                    if bit:
                        byte |= 1
                    end_line = col == size - 1 and i == scale - 1
                    shift_index = (col * scale + i) % 8
                    # If we filled a byte or reached the end of the row, append it
                    if shift_index == 7 or end_line:
                        if end_line:
                            # Shift pending bits if on last byte of row
                            byte <<= 7 - shift_index
                        line_bytes.append(byte)
                        byte = 0
            for _ in range(scale):
                self.uart_conn.write(line_bytes)
                time.sleep_ms(self.dot_print_time)
        self.feed(4)

    def set_bitmap_mode(self, width, height, scale_mode=1):
        """Set image format to be printed"""
        # width in bytes, height in pixels
        # scale_mode=1-> unchanged scale. scale_mode=3-> 2x scale
        command = b"\x1D\x76\x30"
        command += bytes([scale_mode])
        command += bytes([width])
        command += b"\x00"
        command += bytes([height])
        command += b"\x00"
        self.uart_conn.write(command)

    def print_bitmap_line(self, data):
        """Print a bitmap line"""
        self.uart_conn.write(data)
        time.sleep_ms(self.dot_print_time)

    def print_string(self, text):
        """Print a text string"""
        self.uart_conn.write(text)
        time.sleep_ms(self.dot_print_time)
