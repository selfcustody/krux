#!/usr/bin/env python3
"""
A simple Krux Font Format viewer

Pass it: font_filename.kff and height-in-pixels to view all fonts,
optionally, pass it also [ one_utf_character ] to see just that glyph
"""

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


def str_to_bytes(comma_separated_bytes_string):
    """
    receives a string like "0x00,0xff" returning bytes like b'\x00\xff'
    """
    bytestr_list = comma_separated_bytes_string.split(",")
    validation = [x[:2] == "0x" and len(x) == 4 for x in bytestr_list]
    assert set(validation) == set([True])
    return bytes([int(x[2:], 16) for x in bytestr_list])


def main(kff_filename, height, chars=[]):
    """
    receives a kff-filename, height and optionally a string of characters
    prints all kff bitmap fonts, or those requested, to stdout.
    """
    height = int(height)
    zero = chr(0x2591) * 2  # display zero bits as two light-shade chars
    one = chr(0x2588) * 2  # display one bits as two full-block chars

    with open(kff_filename, "r", encoding="ascii") as file_handle:
        contents = file_handle.read().replace("\n", "")
    contents = str_to_bytes(contents)

    num_glyphs = int.from_bytes(contents[:2], "big")
    assert (len(contents) - 2) % num_glyphs == 0
    bytes_per_glyph = (len(contents) - 2) // num_glyphs
    assert (bytes_per_glyph - 2) % height == 0

    print(f"{kff_filename} contains {num_glyphs:d} glyphs:")
    for i in range(2, len(contents), bytes_per_glyph):
        glyph = contents[i : i + bytes_per_glyph]
        codepoint = int.from_bytes(glyph[:2], "big")
        byte_map = glyph[2:]
        bit_map = "".join([f"{x:08b}" for x in byte_map])

        if chars and chr(codepoint) not in chars:
            continue

        print(f'\n"{chr(codepoint)}" is unicode: U+{codepoint:04X}, decimal: {codepoint:d}')
        if len(byte_map) == height:
            # one 8 bit column
            for i in range(0, len(bit_map), 8):
                print("".join(one if x == "1" else zero for x in bit_map[i : i + 8]))

        elif len(byte_map) == height*2:
            # two 8 bit columns
            half = int(len(bit_map) / 2)
            for i in range(0, half, 8):
                print(
                    "".join(
                        one if x == "1" else zero
                        for x in bit_map[i : i + 8] + bit_map[half + i : half + i + 8]
                    )
                )
        elif len(byte_map) == height*3:
            # three 8 bit columns
            third = int(len(bit_map) / 3)
            for i in range(0, third, 8):
                print(
                    "".join(
                        one if x == "1" else zero
                        for x in (
                            bit_map[i : i + 8] +
                            bit_map[third + i : third + i + 8] +
                            bit_map[2 * third + i : 2 * third + i + 8]
                        )
                    )
                )
        elif len(byte_map) == height*4:
            # four 8 bit columns
            qtr = int(len(bit_map) / 4)
            for i in range(0, qtr, 8):
                print(
                    "".join(
                        one if x == "1" else zero
                        for x in (
                            bit_map[i : i + 8] +
                            bit_map[qtr + i : qtr + i + 8] +
                            bit_map[2 * qtr + i : 2 * qtr + i + 8] +
                            bit_map[3 * qtr + i : 3 * qtr + i + 8]
                        )
                    )
                )


if __name__ == "__main__":
    import sys

    main(*sys.argv[1:])
