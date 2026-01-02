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
# pylint: disable=W0231
import math
import time

from ..krux_settings import Settings, CNC_HEAD_LASER, CNC_HEAD_ROUTER
from ..sd_card import SDHandler
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
            raise ValueError("Plunge rate must be less than half of feed rate")

        if self.pass_depth > self.cut_depth:
            raise ValueError("Depth per pass must be less than or equal to cut depth")

    def on_gcode(self, gcode):
        """Receives gcode"""
        raise NotImplementedError(
            "Must implement 'on_gcode' method for {}".format(self.__class__.__name__)
        )

    def print_string(self, text):
        """Print a text string. Avoided on CNC"""
        raise NotImplementedError(
            "Must implement 'print_string' method for {}".format(
                self.__class__.__name__
            )
        )

    def on_xy_gcode(self, gcode):
        """Handle xy gcode preprocessing"""
        if Settings().hardware.printer.cnc.head_type == CNC_HEAD_LASER:
            self.on_gcode(
                (gcode + " S{}").format(Settings().hardware.printer.cnc.head_power)
            )
        else:
            self.on_gcode(gcode)

    def clear(self):
        """Clears the printer's memory, resetting it"""
        raise NotImplementedError(
            "Must implement 'clear' method for {}".format(self.__class__.__name__)
        )

    def on_z_gcode(self, gcode):
        """Handle z gcode preprocessing"""
        if Settings().hardware.printer.cnc.head_type == CNC_HEAD_ROUTER:
            self.on_gcode(gcode)

    def qr_data_width(self):
        """Returns a smaller width for the QR to be generated
        within, which will then be scaled up to fit the part's width.
        We do this because the QR would be too dense to be readable
        by most devices otherwise.
        """
        return 33

    def print_qr_code(self, qr_code):
        """Prints a QR code, scaling it up as large as possible"""
        from ..qr import get_size

        size = 0

        size = get_size(qr_code)

        # If inverted we add two columns and two rows to cut a border.
        if self.invert:
            size += 2

        cell_size = (self.part_size - (self.border_padding * 2)) / size

        # Modal settings
        self.on_gcode("G17")  # x/y plane
        self.on_gcode("G20" if self.unit == "in" else "G21")  # units
        self.on_gcode("G40")  # cancel diameter compensation
        self.on_gcode("G49")  # cancel length offset
        self.on_gcode("G54")  # coord system 1
        self.on_gcode("G90")  # non-incremental motion
        self.on_gcode("G94")  # feed/minute mode
        if Settings().hardware.printer.cnc.head_type == CNC_HEAD_LASER:
            self.on_gcode("$32=1")  # enable laser mode
            self.on_gcode("M4")  # enable Dynamic Laser Power Mode

        num_passes = math.ceil(self.cut_depth / self.pass_depth)
        for p in range(num_passes):
            for row in range(size):
                for col in range(size):
                    plunge_depth = min((p + 1) * self.pass_depth, self.cut_depth)
                    # Reversing row so milling goes from top to bottom
                    reversed_row = size - 1 - row
                    if self.invert and row == 0:
                        self.cut_cell(col, reversed_row, cell_size, plunge_depth)
                    elif self.invert and row == (size - 1):
                        self.cut_cell(col, 0, cell_size, plunge_depth)
                    elif self.invert and col == 0:
                        self.cut_cell(0, reversed_row, cell_size, plunge_depth)
                    elif self.invert and col == (size - 1):
                        self.cut_cell(size - 1, reversed_row, cell_size, plunge_depth)
                    else:
                        # If inverted we need to calculate based on original qr code array size.
                        if self.invert:
                            bit_index = (row - 1) * (size - 2) + (col - 1)
                        else:
                            bit_index = row * size + col
                        bit = qr_code[bit_index >> 3] & (1 << (bit_index % 8))
                        cut = (bit > 0 and not self.invert) or (
                            bit == 0 and self.invert
                        )
                        if cut:
                            self.cut_cell(col, reversed_row, cell_size, plunge_depth)

    # We could optimize by milling rows instead of cell by cell,
    # but this would not allow the use of drill bits
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
        self.on_z_gcode(G0_Z % self.pass_depth)

        # Rapid position to top-left cell corner
        self.on_gcode(G0_XY % (corner_x, corner_y))

        # Smoothly descend to zero
        self.on_z_gcode(G1_Z % (0, self.plunge_rate))

        # Go to starting position and smoothly plunge
        self.on_xy_gcode(G1_XY % (corner_x, corner_y, self.feed_rate))
        self.on_z_gcode(G1_Z % (-plunge_depth, self.plunge_rate))

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
            self.on_xy_gcode(G1_XY % cut_start)
            self.on_xy_gcode(G1_XY % cut_end)

        # Smoothly lift the bit
        self.on_z_gcode(G1_Z % (self.pass_depth, self.plunge_rate))

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
        self.on_z_gcode(G0_Z % self.pass_depth)

        # Rapid position to top-left cell corner
        self.on_gcode(G0_XY % (origin_top_left[x_idx], origin_top_left[y_idx]))

        # Smoothly descend to zero
        self.on_z_gcode(G1_Z % (0, self.plunge_rate))

        # Go to starting position and smoothly plunge
        self.on_xy_gcode(
            G1_XY % (origin_top_left[x_idx], origin_top_left[y_idx], self.feed_rate)
        )
        self.on_z_gcode(G1_Z % (-plunge_depth, self.plunge_rate))

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

            self.on_xy_gcode(G1_XY % (top_left[x_idx], top_left[y_idx], self.feed_rate))
            self.on_xy_gcode(
                G1_XY % (top_right[x_idx], top_right[y_idx], self.feed_rate)
            )
            self.on_xy_gcode(
                G1_XY % (bottom_right[x_idx], bottom_right[y_idx], self.feed_rate)
            )
            self.on_xy_gcode(
                G1_XY % (bottom_left[x_idx], bottom_left[y_idx], self.feed_rate)
            )
            self.on_xy_gcode(
                G1_XY % (top_left[x_idx], top_left[y_idx] - j * incr, self.feed_rate)
            )

            j += 1

        # Smoothly lift the bit
        self.on_z_gcode(G1_Z % (self.pass_depth, self.plunge_rate))


class FilePrinter(GCodeGenerator):
    """FilePrinter is an implementation of the GCodeGenerator that writes generated
    gcode to a file on an attached SD card.
    """

    CNC_FILENAME = "qr.nc"

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
                self.file = open(SDHandler.PATH_STR % FilePrinter.CNC_FILENAME, "w")
                super().print_qr_code(qr_code)
        except:
            raise ValueError("SD card not detected.")
        finally:
            if self.file:
                self.file.flush()
                self.file.close()

    def print_string(self, text):
        """Print a text string. Avoided on CNC"""

    def clear(self):
        """Clears the printer's memory, resetting it"""
        self.file = None


# Tested on openbuilds 1515 with openbuilds blackbox x4 grbl
# controller,openbuilds interface serial remote controller,
# and wondermv. An adapter was made to use the same cable
# that connect to interface, with rx and tx reversed.
# The machine need be homed first before the krux software
# send the commands. On krux device, the grbl/cnc printer
# driver need to be selected, here is the settings
# tested on :
#
# {
#   "settings": {
#     "persist": {"location": "sd"},
#     "printer": {
#       "driver": "cnc/file",
#       "cnc": {
#         "unit": "mm",
#         "part_size": 70.675,
#         "flute_diameter": 3.175,
#         "depth_per_pass": 1.0,
#         "cut_depth": 2.0,
#         "border_padding": 2.0,
#         "plunge_rate":300,
#         "feed_rate":650,
#         "cut_method": "spiral"
#       }
#   }
# }
#
# It seems the wondermv device can be powered by the blackbox
# controller only but sometimes it doesn't start. With it's usb
# powered it always start. Testing scenario : power the cnc,
# use the interface to home everything and start the router,
# unplug the interface and plug the krux device instead, start print.
class GRBLPrinter(GCodeGenerator):
    """
    GRBLPrinter is an implementation of GCodeGenerator that writes generated
    G-code commands to a file intended for use with GRBL-based CNC controllers.
    """

    def __init__(self):
        super().__init__()

        from fpioa_manager import fm
        from machine import UART

        fm.register(
            Settings().hardware.printer.cnc.grbl.tx_pin,
            fm.fpioa.UART2_TX,
            force=True,
        )
        fm.register(
            Settings().hardware.printer.cnc.grbl.rx_pin,
            fm.fpioa.UART2_RX,
            force=True,
        )

        self.uart_conn = UART(UART.UART2, Settings().hardware.printer.cnc.grbl.baudrate)

        self.byte_time = 11.0 / float(Settings().hardware.printer.cnc.grbl.baudrate)

    def print_qr_code(self, qr_code):

        res = self.uart_conn.read()

        gcode = "$I"
        self.write_bytes(*((gcode + "\n").encode()))

        res = self.uart_conn.read()
        if res is None:
            raise ConnectionError("Cannot read from UART connection")

        statuses = res.decode().split("\n")
        if len(statuses) < 2:
            raise IOError("Cannot read, expected at least 2 lines of data")

        handshaked = statuses[0].startswith("[VER:1.1")
        if not handshaked:
            raise ValueError(
                "Cannot handshake, version mismatch. Expected [VER:1.1, got {}".format(
                    statuses[0]
                )
            )

        super().print_qr_code(qr_code)

    def transmit(self, gcode):
        """Sometimes a command is send but seems ignored, we wait 1s and retry in that case"""
        timeout = 10
        for _ in range(timeout):
            self.write_bytes(*((gcode + "\n").encode()))
            res = self.uart_conn.read()
            if res is not None:
                return res
            time.sleep_ms(1000)

        raise TimeoutError("Timeout while waiting for response from GRBL")

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

        res = self.transmit(gcode)

        return res.decode().split("\n")[0]

    def print_string(self, text):
        """Print a text string. Avoided on CNC"""
        raise NotImplementedError(
            "Must implement 'print_string' method for GRBLPrinter"
        )

    def clear(self):
        """Clears the printer's memory, resetting it"""
        raise NotImplementedError("Must implement 'clear' method for GRBLPrinter")
