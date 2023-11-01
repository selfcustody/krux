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

import board
from Maix import GPIO
from fpioa_manager import fm
import time
from .krux_settings import Settings
from .buttons import Button

RIGHT = 1
LEFT = 0


def __handler__(pin_num=None):
    # pylint: disable=unused-argument
    """GPIO interrupt handler"""
    encoder.process((encoder.pin_1.value(), encoder.pin_2.value()))


class RotaryEncoder:
    """Interface with a rotary click-encoder"""

    def __init__(self):
        pins = board.config["krux"]["pins"]["ENCODER"]
        fm.register(pins[0], fm.fpioa.GPIOHS22)
        self.pin_1 = GPIO(GPIO.GPIOHS22, GPIO.IN, GPIO.PULL_UP)
        fm.register(pins[1], fm.fpioa.GPIOHS0)
        self.pin_2 = GPIO(GPIO.GPIOHS0, GPIO.IN, GPIO.PULL_UP)

        self.pin_1.irq(__handler__, GPIO.IRQ_BOTH)
        self.pin_2.irq(__handler__, GPIO.IRQ_BOTH)

        self.state = (0, 0)
        self.direction = RIGHT
        self.value = 0
        self.time_frame = 0

        self.debounce = Settings().hardware.encoder.debounce

    def process(self, new_state):
        """Sets new encoder state after position is changed"""

        def _right():
            if self.direction:
                if time.ticks_ms() > self.time_frame + self.debounce:
                    self.value += 1
                    self.time_frame = time.ticks_ms()
            self.direction = RIGHT

        def _left():
            if not self.direction:
                if time.ticks_ms() > self.time_frame + self.debounce:
                    self.value -= 1
                    self.time_frame = time.ticks_ms()
            self.direction = LEFT

        if self.state == (0, 0):
            if new_state == (0, 1):
                _right()
            elif new_state == (1, 0):
                _left()
        elif self.state == (0, 1):
            if new_state == (1, 1):
                _right()
            elif new_state == (0, 0):
                _left()
        elif self.state == (1, 0):
            if new_state == (0, 0):
                _right()
            elif new_state == (1, 1):
                _left()
        else:  # (1, 1)
            if new_state == (1, 0):
                _right()
            elif new_state == (0, 1):
                _left()

        self.state = new_state


encoder = RotaryEncoder()  # Singleton


class EncoderPage(Button):
    """Encoder class that mimics Krux Page GPIO Button behavior"""

    def event(self):
        """Returns encoder events while mimics Krux GPIO Buttons behavior"""
        if encoder.value > 0:
            encoder.value = 0
            return True
        return False


class EncoderPagePrev(Button):
    """Encoder class that mimics Krux Page_prev GPIO Button behavior"""

    def event(self):
        """Returns encoder events while mimics Krux GPIO Buttons behavior"""
        if encoder.value < 0:
            encoder.value = 0
            return True
        return False
