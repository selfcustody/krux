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

"""
Create Krux 16 bits colors from 8 bits RGB values
Type r g b arguments as 0-255 numbers
Ex: RED
krux_colors.py 255 0 0
Output: 0x00f8
"""

import sys


def rgb888torgb565(color):
    """convert to gggbbbbbrrrrrggg to tuple"""
    red, green, blue = color
    red *= 31
    red //= 255
    red = red << 3
    green *= 63
    green //= 255
    green_a = green & 0b111
    green_b = green & 0b111000
    green_b = green_b << 10
    green = green_a + green_b
    blue *= 31
    blue //= 255
    blue = blue << 8
    return format(red + green + blue, "04x")


if len(sys.argv) == 4:
    try:
        red_byte = min(255, int(sys.argv[1]))
        green_byte = min(255, int(sys.argv[2]))
        blue_byte = min(255, int(sys.argv[3]))
        print("0x" + rgb888torgb565((red_byte, green_byte, blue_byte)))
    except:
        print("Type r g b arguments as 0-255 numbers")
else:
    print("Type r g b arguments as 0-255 numbers")
