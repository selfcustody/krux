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
from unittest import mock

fm_map = {}


def register(pin, gpio_num, force=False):
    fm_map[gpio_num] = pin


class FPIOA:
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
    UART1_RX = 40
    UART1_TX = 41
    UART2_RX = 42
    UART2_TX = 43
    UART3_RX = 44
    UART3_TX = 45


if "fpioa_manager" not in sys.modules:
    sys.modules["fpioa_manager"] = mock.MagicMock(
        fm=mock.MagicMock(fpioa=FPIOA, register=register),
    )
