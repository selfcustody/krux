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

    def value(self):
        if (
            sequence_executor
            and sequence_executor.key is not None
            and sequence_executor.key == self.key
        ):
            sequence_executor.key_checks += 1
            # wait for release
            if sequence_executor.key_checks == 1:
                return RELEASED
            # wait for press
            # if pressed
            elif sequence_executor.key_checks == 2 or sequence_executor.key_checks == 3:
                return PRESSED
            # released
            elif sequence_executor.key_checks == 4:
                sequence_executor.key = None
                sequence_executor.key_checks = 0
                return RELEASED
        return 0 if pg.key.get_pressed()[self.key] else 1


class Battery:
    def getVbatVoltage(self):
        return 3400

    def getUSBVoltage(self):
        return 0

    def enablePMICSleepMode(self, val):
        pass

    def setEnterSleepMode(self):
        pass


if "pmu" not in sys.modules:
    sys.modules["pmu"] = mock.MagicMock(
        PMU_Button=PMU_Button,
        axp192=Battery,
        axp173=Battery,
    )
