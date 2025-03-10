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
import board
from Maix import GPIO
from fpioa_manager import fm
from .kboard import kboard


class IOCircuit:
    """Implements the protocol for Multifunctional IO"""

    def __init__(self, board_io_pin, kendryte_gpio, maixpy_gpio):
        fm.register(board_io_pin, kendryte_gpio)
        self.circuit = GPIO(maixpy_gpio, GPIO.OUT)
        self.turn_off()

    def is_on(self):
        """Returns a boolean indicating if the circuit is currently on"""
        if kboard.is_wonder_mv:
            return self.circuit.value() == 1
        return self.circuit.value() == 0

    def turn_on(self):
        """Turns on the circuit"""
        if kboard.is_wonder_mv:
            self.circuit.value(1)
        else:
            self.circuit.value(0)

    def turn_off(self):
        """Turns off the circuit"""
        if kboard.is_wonder_mv:
            self.circuit.value(0)
        else:
            self.circuit.value(1)

    def toggle(self):
        """Toggles the circuit on or off"""
        if self.is_on():
            self.turn_off()
        else:
            self.turn_on()


class Light(IOCircuit):
    """Light is a singleton interface for interacting with the device's LED light"""

    def __init__(self):
        super().__init__(
            board.config["krux"]["pins"]["LED_W"], fm.fpioa.GPIO3, GPIO.GPIO3
        )
