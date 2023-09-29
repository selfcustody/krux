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
from kruxsim.mocks.board import BUTTON_A, BUTTON_B, BUTTON_C
from kruxsim.mocks.fpioa_manager import fm_map

PRESSED = 0
RELEASED = 1


class GPIO:
    IN = 0
    OUT = 3
    PULL_NONE = 0
    PULL_UP = 2
    PULL_DOWN = 1
    GPIOHS0 = 0
    GPIOHS1 = 1
    GPIOHS2 = 2
    GPIOHS3 = 3
    GPIOHS4 = 4
    GPIOHS5 = 5
    GPIOHS6 = 6
    GPIOHS7 = 7
    GPIOHS8 = 8
    GPIOHS9 = 9
    GPIOHS10 = 10
    GPIOHS11 = 11
    GPIOHS12 = 12
    GPIOHS13 = 13
    GPIOHS14 = 14
    GPIOHS15 = 15
    GPIOHS16 = 16
    GPIOHS17 = 17
    GPIOHS18 = 18
    GPIOHS19 = 19
    GPIOHS20 = 20
    GPIOHS21 = 21
    GPIOHS22 = 22
    GPIOHS23 = 23
    GPIOHS24 = 24
    GPIOHS25 = 25
    GPIOHS26 = 26
    GPIOHS27 = 27
    GPIOHS28 = 28
    GPIOHS29 = 29
    GPIOHS30 = 30
    GPIOHS31 = 31
    GPIO0 = 32
    GPIO1 = 33
    GPIO2 = 34
    GPIO3 = 35
    GPIO4 = 36
    GPIO5 = 37
    GPIO6 = 38
    GPIO7 = 39
    IRQ_FALLING = 0

    def __init__(self, gpio_num, dir=None, val=None):
        self.key = None
        pin = fm_map[gpio_num]
        if pin == BUTTON_A:
            self.key = pg.K_RETURN
        if pin == BUTTON_B:
            self.key = pg.K_DOWN
        if pin == BUTTON_C:
            self.key = pg.K_UP

    def value(self, val=1):
        if not self.key:
            return RELEASED
        return PRESSED if pg.key.get_pressed()[self.key] else RELEASED

    def irq(self, pin, mode):
        pass


if "Maix" not in sys.modules:
    sys.modules["Maix"] = mock.MagicMock(
        GPIO=GPIO,
    )

from Crypto.Cipher import AES

if "ucryptolib" not in sys.modules:
    sys.modules["ucryptolib"] = mock.MagicMock(
        aes=AES.new, MODE_ECB=AES.MODE_ECB, MODE_CBC=AES.MODE_CBC
    )
