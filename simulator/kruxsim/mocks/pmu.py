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
import sys
import time
from unittest import mock
import pygame as pg

PRESSED = 0
RELEASED = 1

sequence_executor = None


def register_sequence_executor(s):
    global sequence_executor
    sequence_executor = s


class PMU_Button:
    def __init__(self):
        self.key = pg.K_UP
        self.state = RELEASED

    def value(self):
        return PRESSED if pg.key.get_pressed()[self.key] else RELEASED

    def event(self):
        if self.state == RELEASED:
            if (
                sequence_executor
                and sequence_executor.key is not None
                and sequence_executor.key == pg.K_UP
                ):
                sequence_executor.key = None
                return True
            if self.value() == PRESSED:
                self.state = PRESSED
                return True
        self.state = self.value()
        return False


class PMUController:
    def __init__(self, i2c_bus):
        pass

    def get_battery_voltage(self):
        return 3400

    def get_usb_voltage(self):
        return 0

    def enable_pek_button_monitor(self):
        pass

    def enter_sleep_mode(self):
        pass

    def enable_adcs(self, on_off):
        pass

    def set_screen_brightness(self, level):
        pass

    def charging(self):
        return True
    
    def usb_connected(self):
        return True

if "pmu" not in sys.modules:
    sys.modules["pmu"] = mock.MagicMock(
        PMU_Button=PMU_Button,
        PMUController=PMUController,
    )
