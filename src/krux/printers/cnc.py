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
# pylint: disable=W0231
import math
from ..krux_settings import Settings
from ..wdt import wdt
from . import Printer
from ..sd_card import SDHandler

G0_XY = "G0 X%.4f Y%.4f"
G0_Z = "G0 Z%.4f"
G1_XY = "G1 X%.4f Y%.4f F%.1f"
G1_Z = "G1 Z%.4f F%.1f"


class GCodeGenerator(Printer):
    """GCodeGenerator takes QR codes and emits gcode via the on_gcode method which
    must be implemented by subclasses
    """

    def __init__(self):
        self.unit = Settings().hardware.printer.cnc.unit
        self.flute_diameter = Settings().hardware.printer.cnc.flute_diameter
        self.plunge_rate = Settings().hardware.printer.cnc.plunge_rate
        self.feed_rate = Settings().hardware.printer.cnc.feed_rate
        self.cut_depth = Settings().hardware.printer.cnc.cut_depth
        self.pass_depth = Settings().hardware.printer.cnc.depth_per_pass
        self.part_size = Settings().hardware.printer.cnc.part_size
        self.border_padding = Settings().hardware.printer.cnc.border_padding
        self.invert = Settings().hardware.printer.cnc.invert

        if self.plunge_rate > self.feed_rate / 2:
            raise ValueError("plunge rate must be less than half of feed rate")

        if self.pass_depth > self.cut_depth:
            raise ValueError("depth per pass must be less than or equal to cut depth")

    def on_gcode(self, gcode):
        """Receives gcode"""
        raise NotImplementedError()

    def qr_data_width(self):
        """Returns a smaller width for the QR to be generated
        within, which will then be scaled up to fit the part's width.
        We do this because the QR would be too dense to be readable
        by most devices otherwise.
        """
        return 33

    def print_qr_code(self, qr_code):
        """Prints a QR code, scaling it up as large as possible"""
        size = 0
        while qr_code[size] != "\n":
            size += 1

        cell_size = (self.part_size - (self.border_padding * 2)) / size

        # Modal settings
        self.on_gcode("G17")  # x/y plane
        self.on_gcode("G20" if self.unit == "in" else "G21")  # units
        self.on_gcode("G40")  # cancel diameter compensation
        self.on_gcode("G49")  # cancel length offset
        self.on_gcode("G54")  # coord system 1
        self.on_gcode("G90")  # non-incremental motion
        self.on_gcode("G94")  # feed/minute mode

        num_passes = math.ceil(self.cut_depth / self.pass_depth)
        for i in range(num_passes):
            plunge_depth = min((i + 1) * self.pass_depth, self.cut_depth)
            for y in range(size):
                for x in range(size):
                    # To reduce travel and avoid zig-zagging, continue cutting on the next row from
                    # the same y
                    x_index = x
                    if y % 2 == 0:
                        x_index = size - 1 - x
                    cell = qr_code[y * (size + 1) + x_index]
                    cut = (cell == "1" and not self.invert) or (
                        cell == "0" and self.invert
                    )
                    if cut:
                        # Flip the y coord
                        self.cut_cell(x_index, size - 1 - y, cell_size, plunge_depth)

    def cut_cell(self, x, y, cell_size, plunge_depth):
        """Hollows out the specified cell using a cutting method defined in settings"""
        if Settings().hardware.printer.cnc.cut_method == "spiral":
            self.spiral_cut_cell(x, y, cell_size, plunge_depth)
        else:
            self.row_cut_cell(x, y, cell_size, plunge_depth)

    def row_cut_cell(self, x, y, cell_size, plunge_depth):
        """Hollows out the specified cell by cutting in lines from one end to the
        other, in rows, similar to a printer
        """
        flute_radius = self.flute_diameter / 2

        corner_x = self.border_padding + (x * cell_size) + flute_radius
        corner_y = self.border_padding + (y * cell_size) + flute_radius

        # Lift the bit
        self.on_gcode(G0_Z % self.pass_depth)

        # Rapid position to top-left cell corner
        self.on_gcode(G0_XY % (corner_x, corner_y))

        # Smoothly descend to zero
        self.on_gcode(G1_Z % (0, self.plunge_rate))

        # Go to starting position and smoothly plunge
        self.on_gcode(G1_XY % (corner_x, corner_y, self.feed_rate))
        self.on_gcode(G1_Z % (-plunge_depth, self.plunge_rate))

        # Cut row by row
        num_rows = math.floor(cell_size / flute_radius)
        for j in range(num_rows):
            cut_start = (corner_x, corner_y + j * flute_radius, self.feed_rate)
            cut_end = (
                corner_x + cell_size - self.flute_diameter,
                corner_y + j * flute_radius,
                self.feed_rate,
            )
            if j % 2 != 0:
                cut_start, cut_end = cut_end, cut_start
            self.on_gcode(G1_XY % cut_start)
            self.on_gcode(G1_XY % cut_end)

        # Smoothly lift the bit
        self.on_gcode(G1_Z % (self.pass_depth, self.plunge_rate))

    def spiral_cut_cell(self, x, y, cell_size, plunge_depth):
        """Hollows out the specified cell by starting at the edge of the cell and
        following a spiral cutting path until reaching the center
        """
        x_idx = 0
        y_idx = 1

        flute_radius = self.flute_diameter / 2

        origin_top_left = (
            (x * cell_size) + self.border_padding + flute_radius,
            (y * cell_size) + cell_size + self.border_padding - flute_radius,
        )
        origin_top_right = (
            origin_top_left[x_idx] + cell_size - self.flute_diameter,
            origin_top_left[y_idx],
        )
        origin_bottom_right = (
            origin_top_right[x_idx],
            origin_top_right[y_idx] - cell_size + self.flute_diameter,
        )
        origin_bottom_left = (origin_top_left[x_idx], origin_bottom_right[y_idx])

        # Lift the bit
        self.on_gcode(G0_Z % self.pass_depth)

        # Rapid position to top-left cell corner
        self.on_gcode(G0_XY % (origin_top_left[x_idx], origin_top_left[y_idx]))

        # Smoothly descend to zero
        self.on_gcode(G1_Z % (0, self.plunge_rate))

        # Go to starting position and smoothly plunge
        self.on_gcode(
            G1_XY % (origin_top_left[x_idx], origin_top_left[y_idx], self.feed_rate)
        )
        self.on_gcode(G1_Z % (-plunge_depth, self.plunge_rate))

        # Cut in a spiral moving inwards
        j = 0
        while True:
            incr = flute_radius

            top_left = (
                origin_top_left[x_idx] + j * incr,
                origin_top_left[y_idx] - j * incr,
            )
            top_right = (
                origin_top_right[x_idx] - j * incr,
                origin_top_right[y_idx] - j * incr,
            )
            bottom_right = (
                origin_bottom_right[x_idx] - j * incr,
                origin_bottom_right[y_idx] + j * incr,
            )
            bottom_left = (
                origin_bottom_left[x_idx] + j * incr,
                origin_bottom_left[y_idx] + j * incr,
            )
            done = (
                top_left[x_idx] >= top_right[x_idx]
                or top_left[y_idx] <= bottom_left[y_idx]
                or top_right[y_idx] <= bottom_right[y_idx]
                or bottom_left[x_idx] >= bottom_right[x_idx]
            )
            if done:
                break

            self.on_gcode(G1_XY % (top_left[x_idx], top_left[y_idx], self.feed_rate))
            self.on_gcode(G1_XY % (top_right[x_idx], top_right[y_idx], self.feed_rate))
            self.on_gcode(
                G1_XY % (bottom_right[x_idx], bottom_right[y_idx], self.feed_rate)
            )
            self.on_gcode(
                G1_XY % (bottom_left[x_idx], bottom_left[y_idx], self.feed_rate)
            )
            self.on_gcode(
                G1_XY % (top_left[x_idx], top_left[y_idx] - j * incr, self.feed_rate)
            )

            j += 1

        # Smoothly lift the bit
        self.on_gcode(G1_Z % (self.pass_depth, self.plunge_rate))


class FilePrinter(GCodeGenerator):
    """FilePrinter is an implementation of the GCodeGenerator that writes generated
    gcode to a file on an attached SD card.
    """

    def __init__(self):
        super().__init__()
        self.file = None

    def on_gcode(self, gcode):
        """Writes each gcode command on a new line in the file"""
        wdt.feed()
        self.file.write(gcode + "\n")

    def print_qr_code(self, qr_code):
        """Creates an nc file on the SD card with commands to cut out the specified QR code"""
        try:
            with SDHandler():
                self.file = open("/sd/qr.nc", "w")
                super().print_qr_code(qr_code)
        except OSError:
            pass
        finally:
            if self.file:
                self.file.flush()
                self.file.close()

    def print_string(self, text):
        """Print a text string. Avoided on CNC"""

    def clear(self):
        """Clears the printer's memory, resetting it"""
        self.file = None


# TODO: Didn't have the time or resources to test this, so it's commented out for now.
#       If anyone is brave enough, you should be able to uncomment this block and uncomment the line
#       in ./__init__.py to display 'cnc/grbl' as a selectable option to test.
# import time
# from fpioa_manager import fm
# from machine import UART
# class GRBLPrinter(GCodeGenerator):
#     """GRBLPrinter is an implementation of the GCodeGenerator that sends generated
#     gcode as commands to a GRBL controller over a serial connection.
#     """

#     def __init__(self):
#         super().__init__()
#         fm.register(Settings().hardware.printer.cnc.grbl.tx_pin, fm.fpioa.UART2_TX, force=False)
#         fm.register(Settings().hardware.printer.cnc.grbl.rx_pin, fm.fpioa.UART2_RX, force=False)
#         self.uart_conn = UART(UART.UART2, Settings().hardware.printer.cnc.grbl.baudrate)
#         self.byte_time = 11.0 / float(Settings().hardware.printer.cnc.grbl.baudrate)
#         res = self.uart_conn.readline()
#         if res is None or not res.decode().lower().startswith("grbl"):
#             raise ValueError("not connected")

#     def write_bytes(self, *args):
#         """Writes bytes to the controller at a stable speed"""
#         for arg in args:
#             wdt.feed()
#             self.uart_conn.write(arg if isinstance(arg, bytes) else bytes([arg]))
#             # Calculate time to issue one byte to the controller.
#             # 11 bits (not 8) to accommodate idle, start and
#             # stop bits.  Idle time might be unnecessary, but
#             # erring on side of caution here.
#             time.sleep_ms(math.floor(self.byte_time * 1000))

#     def on_gcode(self, gcode):
#         """Sends the gcode command to GRBL"""
#         wdt.feed()

#         # Send the gcode command to GRBL as bytes
#         self.write_bytes(*((gcode + "\n").encode()))

#         # Wait for an 'ok' response
#         res = self.uart_conn.readline()
#         if res is None:
#             raise ValueError("gcode send failed: timed out")

#         status = res.decode().split("\n")[0]
#         if status != "ok":
#             err_msg = status if status.startswith("error") else "unknown error"
#             raise ValueError("gcode send failed: %s" % err_msg)

#     def clear(self):
#         """Clears the printer's memory, resetting it"""
