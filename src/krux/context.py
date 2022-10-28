# The MIT License (MIT)

# Copyright (c) 2021-2022 Krux contributors

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
import gc
import board
import os
from .logging import logger
from .display import Display
from .input import Input
from .camera import Camera
from .light import Light


class Context:
    """Context is a singleton containing all 'global' state that lives throughout the
    duration of the program, including references to all device interfaces.
    """

    def __init__(self):
        self.display = Display()
        self.input = Input()
        self.camera = Camera()
        self.light = Light() if "LED_W" in board.config["krux"]["pins"] else None
        self.power_manager = None
        self.printer = None
        self.wallet = None

    @property
    def log(self):
        """Returns the default logger"""
        return logger

    def clear(self):
        """Clears all sensitive data from the context, resetting it"""
        self.wallet = None
        if self.printer is not None:
            self.printer.clear()
        gc.collect()

    @property
    def sd_card(self):
        """Returns whether or not an SD card is present. This property should eventually
        be replaced by an SD interface class for reading and writing to disk"""
        try:
            tmpfile = "/sd/.chkmnt"
            with open(tmpfile, "w") as tmp:
                tmp.write("")
            os.remove(tmpfile)
            return object()
        except:
            return None
