# The MIT License (MIT)

# Copyright (c) 2021 Tom J. Sun

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
# pylint: disable=C0103
# pylint: disable=E1307

# Joined conversion files in one, except merge
# No need to specify output file

import sys
import math
import os

width = int(sys.argv[2])
height = int(sys.argv[3])

# bdf to hex
hex_name = sys.argv[1][:-4]
hex_name += ".hex"
with open(sys.argv[1], "r", encoding="unicode_escape") as input_file:
    with open(hex_name, "w") as hex_file:
        codepoint = None
        parsing_bitmap = False
        hex_chars = []
        for line in input_file.readlines():
            if line.startswith("ENCODING"):
                codepoint = int(line.split()[1])
            elif line.startswith("BITMAP"):
                parsing_bitmap = True
            elif line.startswith("ENDCHAR"):
                if parsing_bitmap and hex_chars:
                    hex_file.write(
                        "%04X:%s" % (codepoint, "".join(hex_chars).upper()) + "\n"
                    )
                parsing_bitmap = False
                hex_chars = []
            elif parsing_bitmap:
                hex_chars.append(line.strip())
    hex_file.close()

# Fill
font_byte_length = math.ceil(width / 8) * height
line_char_length = (font_byte_length * 2) + 6  # 6 is codepoint prefix len
fill_name = sys.argv[1][:-4]
fill_name += "_fill.hex"
with open(hex_name, "r") as input_file:
    # Read in a hex formatted bitmap font file
    lines = input_file.readlines()
    # Zero out > height pixel width characters since they can't be scaled down
    lines = list(
        map(
            lambda line: line.split(":")[0] + ":" + ("00" * font_byte_length) + "\n"
            if len(line) > line_char_length
            else line,
            lines,
        )
    )
    # Pad < height pixel width chars with leading 0s
    lines = list(
        map(
            lambda line: line[:5]
            + ("0" * (line_char_length - len(line)))
            + line[5 : len(line)]
            if len(line) < line_char_length
            else line,
            lines,
        )
    )
    # Add missing characters (zero'd out) so the codepoint sequence is contiguous
    i = 0
    while i < len(lines):
        codepoint = int(lines[i].split(":")[0], 16)
        while i < codepoint:
            lines.insert(i, ("%04X" % i) + ":" + ("00" * font_byte_length) + "\n")
            i += 1
        i += 1
    with open(fill_name, "w") as fill_file:
        fill_file.write("".join(lines).strip())
    fill_file.close()

# replace symbols
r_name = sys.argv[1][:-4]
r_name += "_r.hex"

with open(fill_name, "r") as fill_file:
    original = fill_file.readlines()

# replace ¡ for █
original[0xA1] = original[0x2588]
# replace ¤ for ₿
# original[0xA4] = original[0x20BF]
# Terminus does not have ₿, using B instead
original[0xA4] = original[0x42]

with open(r_name, "w") as file:
    file.writelines(original)

# to dkz
BYTE_LEN = 2
width_bytes = math.ceil(width / 8)

dkz_name = sys.argv[1][:-4]
dkz_name += ".dkz"

with open(r_name, "r") as input_file:
    # Read in a hex formatted bitmap font file
    lines = input_file.readlines()

    # Strip out the unicode code point prefix at the beginning of each line
    glyphs = list(map(lambda line: line.split(":")[1].rstrip("\n"), lines))

    # Use only the first $limit glyphs
    limit = len(glyphs)
    if len(sys.argv) == 5:
        limit = int(sys.argv[4])

    bitmap = []
    for i in range(len(glyphs)):
        if i >= limit:
            break
        glyph = glyphs[i]

        rows = []
        for x in range(width_bytes):
            row = []
            for y in range(height):
                glyph_index = y * BYTE_LEN * width_bytes + (x * BYTE_LEN)
                row.append("0x" + glyph[glyph_index : glyph_index + BYTE_LEN])
            rows.append(",".join(row))
        bitmap.append(",\n".join(rows))
    with open(dkz_name, "w") as dkz_file:
        dkz_file.write(",\n".join(bitmap))
    dkz_file.close()

# Comment below to debug intermediary steps files
os.remove(hex_name)
os.remove(fill_name)
os.remove(r_name)
