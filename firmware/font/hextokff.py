# The MIT License (MIT)

# Copyright (c) 2022 Tom J. Sun

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
# pylint: disable=C0301
# pylint: disable=C0103
import sys
import math
import os
import json

BYTE_LEN = 2
DEFAULT_CODEPOINTS = [
    ord(char)
    for char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 !#$%&'()*+,-./:;<=>?@[\\]^_\"{|}~█₿"
]
TRANSLATIONS_DIR = "../../i18n/translations"

width = int(sys.argv[2])
height = int(sys.argv[3])

width_bytes = math.ceil(width / 8)

# Scan the translations folder and build a set of unique codepoints used
# across all translations
used_codepoints = set(DEFAULT_CODEPOINTS)
for translation_file in os.listdir(TRANSLATIONS_DIR):
    translations = json.load(
        open(os.path.join(TRANSLATIONS_DIR, translation_file), "r")
    )
    for translation in translations.values():
        for char in translation:
            used_codepoints.add(ord(char))

with open(sys.argv[1], "r") as input_file:
    # Read in a hex formatted bitmap font file
    lines = input_file.readlines()

    # Output in modified dkz format ("krux font format") where first two bytes
    # of each row are the codepoint
    bitmap = []
    total_codepoints = 0
    for line in lines:
        line = line.rstrip("\n")
        codepoint, glyph = line.split(":")
        if int(codepoint, 16) not in used_codepoints:
            continue

        total_codepoints += 1

        # Prefix with codepoint bytes
        rows = ["0x%s,0x%s" % (codepoint[:2], codepoint[2:])]

        for x in range(width_bytes):
            row = []
            for y in range(height):
                glyph_index = y * BYTE_LEN * width_bytes + (x * BYTE_LEN)
                row.append("0x" + glyph[glyph_index : glyph_index + BYTE_LEN])
            rows.append(",".join(row))
        bitmap.append(",\n".join(rows))

    # Prefix with number of codepoints as two hex bytes
    total_codepoints = "%04X" % total_codepoints
    print(
        ",\n".join(
            ["0x%s,0x%s" % (total_codepoints[:2], total_codepoints[2:])] + bitmap
        )
    )
