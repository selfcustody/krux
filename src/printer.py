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
from board import board_info
from fpioa_manager import fm
from machine import UART
import settings
from thermal import AdafruitThermalPrinter

class Printer:
    """Printer is a singleton interface for interacting with the device's thermal printer"""

    def __init__(self):
        self.paper_width = int(settings.load('printer.paper_width', '384'))

        try:
            fm.register(board_info.CONNEXT_A, fm.fpioa.UART2_TX, force=False)
            fm.register(board_info.CONNEXT_B, fm.fpioa.UART2_RX, force=False)
            self.thermal_printer = AdafruitThermalPrinter(
                UART.UART2,
                int(settings.load('printer.baudrate', '9600'))
            )
            if not self.thermal_printer.has_paper():
                raise ValueError('missing paper')
        except:
            self.thermal_printer = None

    def qr_data_width(self):
        """Returns a smaller width for the QR to be generated
           within, which will then be scaled up to fit the paper's width.
           We do this because the QR would be too dense to be readable
           by most devices otherwise.
        """
        return self.paper_width // 6

    def clear(self):
        """Clears the printer's memory, resetting it"""
        if not self.is_connected():
            return
        # A full reset zeroes all memory buffers
        self.thermal_printer.full_reset()

    def is_connected(self):
        """Returns a boolean indicating if the printer is connected or not"""
        return self.thermal_printer is not None

    def print_qr_code(self, qr_code):
        """Prints a QR code, scaling it up as large as possible"""
        if not self.is_connected():
            raise ValueError('no printer found')

        lines = qr_code.strip().split('\n')

        width = len(lines)
        height = len(lines)

        scale = self.paper_width // width
        for y in range(height):
            # Scale the line (width) by scaling factor
            line_y = ''.join([char * scale for char in lines[y]])
            line_bytes = int(line_y, 2).to_bytes((len(line_y) + 7) // 8, 'big')
            # Print height * scale lines out to scale by
            for _ in range(scale):
                self.thermal_printer.write_bytes(18, 42, 1, len(line_bytes))
                self.thermal_printer.write_bytes(line_bytes)
                self.thermal_printer.timeout_set(self.thermal_printer.dot_print_time)
        self.thermal_printer.feed(3)
