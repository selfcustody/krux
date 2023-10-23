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
from ..krux_settings import t

# from ..settings import CategorySetting, SettingsNamespace
from ..krux_settings import Settings, PrinterSettings


class Printer:
    """Printer is a singleton interface for interacting with the device's printer

    Must be subclassed.
    """

    def __init__(self):
        raise NotImplementedError()

    def qr_data_width(self):
        """Returns a smaller width for the QR to be generated
        within, which will then be scaled up to fit the paper's width.
        We do this because the QR would be too dense to be readable
        by most devices otherwise.
        """
        raise NotImplementedError()

    def clear(self):
        """Clears the printer's memory, resetting it"""
        raise NotImplementedError()

    def print_qr_code(self, qr_code):
        """Prints a QR code, scaling it up as large as possible"""
        raise NotImplementedError()

    def print_string(self, text):
        """Print a text string"""
        raise NotImplementedError()


def create_printer():
    """Instantiates a new printer dynamically based on the default in Settings"""

    module, cls = PrinterSettings.PRINTERS[Settings().hardware.printer.driver]
    if not cls:
        return None
    return getattr(
        __import__(module, globals(), None, [None], 1),
        cls,
    )()
