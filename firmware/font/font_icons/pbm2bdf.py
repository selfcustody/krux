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

# Convert pbm files to bdf format
# Draw pbm files in gimp and use them as glyphs
# Usage: python pbm2bdf.py Derivation_Amigo.pbm 21B3
# Where 21B3 is the target codepoint, ex U+21B3
# Copy the output to the bdf file

import sys

code_point_hex = None
try:
    pbm_file = sys.argv[1]
    code_point_hex = sys.argv[2]
except Exception as e:
    print("Not enough arguments")
    exit()
try:
    with open(pbm_file, "rb") as f:
        lines = f.read().split(b"\n")
        popped = 0
        for i in range(len(lines)):
            if lines[i - popped].startswith(b"#"):
                lines.pop(i - popped)
                popped += 1
        dimensions = lines[1].split(b" ")
        width = int(dimensions[0].decode())
        bytes_width = (width + 7) // 8
        height = int(dimensions[1].decode())

except Exception as e:
    print(e, "Failed to read file")
    exit()
print("STARTCHAR U+" + code_point_hex.upper())
print("ENCODING " + str(int(code_point_hex, 16)))
print("SWIDTH 1000 0")
print("DWIDTH " + str(width) + " 0")
print("BBX " + str(width) + " " + str(height) + " 0 0")
print("BITMAP")

for i in range(len(lines[2]) // bytes_width):
    line_bytes = ""
    for j in range(bytes_width):
        line_bytes += "%0.2X" % lines[2][i * bytes_width + j]
    print(line_bytes)
print("ENDCHAR")
