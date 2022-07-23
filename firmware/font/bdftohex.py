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
import sys

with open(sys.argv[1], "r", encoding="unicode_escape") as input_file:
    codepoint = None
    parsing_bitmap = False
    hex_chars = []
    for line in input_file.readlines():
        if line.startswith("ENCODING"):
            codepoint = int(line.split()[1])
        elif line.startswith("BITMAP"):
            parsing_bitmap = True
        elif line.startswith("ENDCHAR"):
            if parsing_bitmap and hex_chars and codepoint > 0:
                print("%04X:%s" % (codepoint, "".join(hex_chars).upper()))
            parsing_bitmap = False
            hex_chars = []
        elif parsing_bitmap:
            hex_chars.append(line.strip())
