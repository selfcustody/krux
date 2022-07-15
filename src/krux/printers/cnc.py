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
# pylint: disable=W0231
import binascii
import hashlib
import time
import math
import board
from fpioa_manager import fm
from machine import UART
from ..settings import settings
from ..wdt import wdt
from . import Printer

G0_XY = "G0 X%.4f Y%.4f"
G0_Z = "G0 Z%.4f"
G1_XY = "G1 X%.4f Y%.4f F%.1f"
G1_Z = "G1 Z%.4f F%.1f"


class GCodeGenerator(Printer):
    """GCodeGenerator takes QR codes and emits gcode via the on_gcode method which
    must be implemented by subclasses
    """

    def __init__(self):
        self.unit = settings.printer.cnc.unit
        self.flute_diameter = settings.printer.cnc.flute_diameter
        self.plunge_rate = settings.printer.cnc.plunge_rate
        self.feed_rate = settings.printer.cnc.feed_rate
        self.cut_depth = settings.printer.cnc.cut_depth
        self.pass_depth = settings.printer.cnc.depth_per_pass
        self.border_size = settings.printer.cnc.border_size
        self.cell_margin = settings.printer.cnc.cell_margin
        self.part_width = settings.printer.cnc.part_width
        self.border_size = settings.printer.cnc.border_size
        self.invert = settings.printer.cnc.invert

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

        cell_size = (self.part_width - (self.border_size * 2)) / size

        # Modal settings
        self.on_gcode("G17")  # x/y plane
        self.on_gcode("G20" if self.unit == "in" else "G21")  # units
        self.on_gcode("G40")  # cancel diameter compensation
        self.on_gcode("G49")  # cancel length offset
        self.on_gcode("G54")  # coord system 1
        self.on_gcode("G80")  # cancel motion
        self.on_gcode("G90")  # non-incremental motion
        self.on_gcode("G94")  # feed/minute mode

        for y in range(size):
            for x in range(size):
                # To reduce travel and avoid zig-zagging, continue cutting on the next row from
                # the same y
                x_index = x
                if y % 2 == 0:
                    x_index = size - 1 - x
                cell = qr_code[y * (size + 1) + x_index]
                cut = (cell == "1" and not self.invert) or (cell == "0" and self.invert)
                if cut:
                    # Flip the y coord
                    self.cut_cell(x_index, size - 1 - y, cell_size)

    def cut_cell(self, x, y, cell_size):
        """Hollows out the specified cell using a cutting method defined in settings"""
        if settings.printer.cnc.cut_method == "spiral":
            self.spiral_cut_cell(x, y, cell_size)
        else:
            self.row_cut_cell(x, y, cell_size)

    def row_cut_cell(self, x, y, cell_size):
        """Hollows out the specified cell by cutting in lines from one end to the
        other, in rows, similar to a printer
        """
        flute_radius = self.flute_diameter / 2

        corner_x = self.border_size + (x * cell_size) + flute_radius + self.cell_margin
        corner_y = self.border_size + (y * cell_size) + flute_radius + self.cell_margin

        # Lift the bit
        self.on_gcode(G0_Z % (2 * self.pass_depth))

        # Rapid position to top-left cell corner
        self.on_gcode(G0_XY % (corner_x, corner_y))

        # Smoothly descend to zero
        self.on_gcode(G1_Z % (0, self.plunge_rate))

        num_passes = math.ceil(self.cut_depth / self.pass_depth)
        num_rows = math.floor((cell_size - (2 * self.cell_margin)) / flute_radius)
        for i in range(num_passes):
            self.on_gcode(G1_XY % (corner_x, corner_y, self.feed_rate))
            self.on_gcode(G1_Z % (-(i + 1) * self.pass_depth, self.plunge_rate))
            for j in range(num_rows):
                cut_start = (corner_x, corner_y + j * flute_radius, self.feed_rate)
                cut_end = (
                    corner_x + cell_size - self.cell_margin - self.flute_diameter,
                    corner_y + j * flute_radius,
                    self.feed_rate,
                )
                if j % 2 != 0:
                    cut_start, cut_end = cut_end, cut_start
                self.on_gcode(G1_XY % cut_start)
                self.on_gcode(G1_XY % cut_end)

        # Lift the bit
        self.on_gcode(G0_Z % (2 * self.pass_depth))

    def spiral_cut_cell(self, x, y, cell_size):
        """Hollows out the specified cell by starting at the edge of the cell and
        following a spiral cutting path until reaching the center
        """
        x_idx = 0
        y_idx = 1

        flute_radius = self.flute_diameter / 2

        origin_top_left = (
            (x * cell_size) + self.border_size + self.cell_margin + flute_radius,
            (y * cell_size)
            + cell_size
            + self.border_size
            - self.cell_margin
            - flute_radius,
        )
        origin_top_right = (
            origin_top_left[x_idx] + cell_size - self.cell_margin - self.flute_diameter,
            origin_top_left[y_idx],
        )
        origin_bottom_right = (
            origin_top_right[x_idx],
            origin_top_right[y_idx]
            - cell_size
            + self.cell_margin
            + self.flute_diameter,
        )
        origin_bottom_left = (origin_top_left[x_idx], origin_bottom_right[y_idx])

        # Lift the bit
        self.on_gcode(G0_Z % (2 * self.pass_depth))

        # Rapid position to top-left cell corner
        self.on_gcode(G0_XY % (origin_top_left[x_idx], origin_top_left[y_idx]))

        # Smoothly descend to zero
        self.on_gcode(G1_Z % (0, self.plunge_rate))

        num_passes = math.ceil(self.cut_depth / self.pass_depth)
        for i in range(num_passes):
            self.on_gcode(
                G1_XY % (origin_top_left[x_idx], origin_top_left[y_idx], self.feed_rate)
            )
            self.on_gcode(G1_Z % (-(i + 1) * self.pass_depth, self.plunge_rate))
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

                self.on_gcode(
                    G1_XY % (top_left[x_idx], top_left[y_idx], self.feed_rate)
                )
                self.on_gcode(
                    G1_XY % (top_right[x_idx], top_right[y_idx], self.feed_rate)
                )
                self.on_gcode(
                    G1_XY % (bottom_right[x_idx], bottom_right[y_idx], self.feed_rate)
                )
                self.on_gcode(
                    G1_XY % (bottom_left[x_idx], bottom_left[y_idx], self.feed_rate)
                )
                self.on_gcode(
                    G1_XY
                    % (top_left[x_idx], top_left[y_idx] - j * incr, self.feed_rate)
                )

                j += 1

        # Lift the bit
        self.on_gcode(G0_Z % (2 * self.pass_depth))


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
        filename = (
            "qr-%s.gcode"
            % binascii.hexlify(hashlib.sha256(qr_code.encode()).digest()).decode()
        )
        self.file = open("/sd/%s" % filename, "w")
        super().print_qr_code(qr_code)
        self.file.flush()
        self.file.close()

    def clear(self):
        """Clears the printer's memory, resetting it"""


class GRBLPrinter(GCodeGenerator):
    """GRBLPrinter is an implementation of the GCodeGenerator that sends generated
    gcode as commands to a GRBL controller over a serial connection.
    """

    def __init__(self):
        super().__init__()
        if (
            "UART2_TX" not in board.config["krux.pins"]
            or "UART2_RX" not in board.config["krux.pins"]
        ):
            raise ValueError("missing required ports")
        fm.register(
            board.config["krux.pins"]["UART2_TX"], fm.fpioa.UART2_TX, force=False
        )
        fm.register(
            board.config["krux.pins"]["UART2_RX"], fm.fpioa.UART2_RX, force=False
        )
        self.uart_conn = UART(UART.UART2, settings.printer.cnc.baudrate)
        self.byte_time = 11.0 / float(settings.printer.cnc.baudrate)

    def write_bytes(self, *args):
        """Writes bytes to the controller at a stable speed"""
        for arg in args:
            wdt.feed()
            self.uart_conn.write(arg if isinstance(arg, bytes) else bytes([arg]))
            # Calculate time to issue one byte to the controller.
            # 11 bits (not 8) to accommodate idle, start and
            # stop bits.  Idle time might be unnecessary, but
            # erring on side of caution here.
            time.sleep_ms(math.floor(self.byte_time * 1000))

    def on_gcode(self, gcode):
        """Sends the gcode command to GRBL"""
        wdt.feed()

        # Send the gcode command to GRBL as bytes
        self.write_bytes(*((gcode + "\n").encode()))

        # Wait for an 'ok' response
        res = self.uart_conn.readline()
        if res is None:
            raise ValueError("gcode send failed: timed out")

        status = res.decode().split("\n")[0]
        if status != "ok":
            err_msg = status if status.startswith("error") else "unknown error"
            raise ValueError("gcode send failed: %s" % err_msg)

    def clear(self):
        """Clears the printer's memory, resetting it"""
        self.uart_conn.deinit()
