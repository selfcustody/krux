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
import sys
import math

BYTE_LEN = 2

width = int(sys.argv[2])
height = int(sys.argv[3])

width_bytes = math.ceil(width / 8)

with open(sys.argv[1], "r") as input_file:
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
    print(",\n".join(bitmap))
