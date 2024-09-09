# The MIT License (MIT)

# Copyright (c) 2021-2024 Krux contributors

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


from collections import namedtuple
import math
import sys


def bdftohex(filename=None):
    """Converts a BDF font filename to a hex file for use with the Krux firmware."""
    if filename is None:
        raise ValueError("ERROR: Provide the filename.bdf as argument")

    codepoint_list = []
    BBox = namedtuple("BoundingBox", ["width", "height", "x", "y"])

    with open(filename, "r", encoding="unicode_escape") as input_file:
        font_bbox = None
        glyph_bbox = None
        codepoint = -1
        parsing_bitmap = False
        hex_chars = []
        for line in input_file.readlines():
            if line.startswith("FONTBOUNDINGBOX"):
                font_bbox = BBox(*[int(c) for c in line.split()[1:]])
                line_size = math.ceil(font_bbox.width / 8) * 2
            elif line.startswith("BBX"):
                glyph_bbox = BBox(*[int(c) for c in line.split()[1:]])
            elif line.startswith("ENCODING"):
                codepoint = int(line.split()[1])
            elif line.startswith("BITMAP"):
                parsing_bitmap = True
            elif line.startswith("ENDCHAR"):
                if parsing_bitmap and hex_chars and codepoint >= 0:
                    bitmap = "".join(hex_chars).upper()
                    if font_bbox and glyph_bbox:
                        row = "00" * math.ceil(font_bbox.width / 8)
                        glyph_height = len(hex_chars)
                        padding = font_bbox.height - glyph_height
                        if padding > 0:
                            bottom_padding = glyph_bbox.y - font_bbox.y
                            top_padding = padding - bottom_padding
                            if top_padding > 0:
                                bitmap = row * top_padding + bitmap
                            if bottom_padding > 0:
                                bitmap = bitmap + row * bottom_padding
                    glyph_trimmer = (
                        math.ceil(font_bbox.width / 8) * font_bbox.height * 2
                    )
                    bitmap = bitmap[:glyph_trimmer]
                    codepoint_list.append(f"{codepoint:04X}:{bitmap}")
                parsing_bitmap = False
                hex_chars = []
                codepoint = -1
                glyph_bbox = None
            elif parsing_bitmap:
                # Ensures each line has proper length
                line = line.strip()
                if len(line) < line_size:
                    line += "0" * (line_size - len(line))
                hex_chars.append(line)
    return codepoint_list


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("\n".join(bdftohex(sys.argv[1])))
    else:
        raise ValueError("ERROR: Provide the filename.bdf as argument")
