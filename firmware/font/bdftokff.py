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

import os
import sys
import re
import bdftohex
import hexfill
import hexmerge
import hextokff

FONT14 = "ter-u14n"
FONT16 = "ter-u16n"
FONT24 = "ter-u24b"


def open_bdf_save_kff(filename, width, height):
    """Open a bdf font filename and save the corresponding kff file based on the filename"""

    filename_kff = "m5stickv"
    if filename == FONT16:
        filename_kff = "bit_dock_yahboom"
    elif filename == FONT24:
        filename_kff = "amigo"

    # Create hexfile based on bdf
    font_hex = "\n".join(bdftohex.bdftohex(filename + ".bdf")) + "\n"
    with open(filename + ".hex", "w", encoding="utf-8") as save_file:
        save_file.write(font_hex)

    # Fill the hexfile with missing empty glyphs
    font_hex_filled = "".join(hexfill.hexfill(filename + ".hex", width, height)).strip()
    with open(filename + ".hex", "w", encoding="utf-8") as save_file:
        save_file.write(font_hex_filled)

    # Merges the hexfile empty glyphs with the its corresponding contents
    # (can be used with multiple files)
    font_hex_merged = "\n".join(hexmerge.hexmerge(filename + ".hex")) + "\n"
    with open(filename + ".hex", "w", encoding="utf-8") as save_file:
        save_file.write(font_hex_merged)

    # Creates the Krux font file, to be used on each project
    # font.c file: ../MaixPy/projects/<device_name>/compile/
    # overrides/components/micropython/port/src/omv/img/font.c
    # in order to replace the contents of the unicode[] variable
    #  in the font.c
    font_kff = hextokff.hextokff(filename + ".hex", width, height)
    with open(filename_kff + ".kff", "w", encoding="utf-8") as save_file:
        save_file.write(font_kff)

    # Deletes the temporary hexfile
    os.remove(filename + ".hex")


def save_new_fontc(font_name, overwrite=False):
    """If overwrite=True them overwrite the content of the font.c file
    on each project, based on the font_name passed otherwise save
    a new font.c file"""

    device_name = filename_kff = "m5stickv"
    if font_name == FONT16:
        filename_kff = "bit_dock_yahboom"
        device_name = "dock"
    elif font_name == FONT24:
        device_name = filename_kff = "amigo"

    maixpy_path_start = "../MaixPy/projects/maixpy_"
    maixpy_path_end = (
        "/compile/overrides/components/micropython/port/src/omv/img/font.c"
    )

    with open(filename_kff + ".kff", "r", encoding="utf-8") as read_file:
        content_kff = read_file.read()

    content_kff = "static uint8_t unicode[] = {\n" + content_kff + "\n};"

    filename = maixpy_path_start + device_name + maixpy_path_end
    with open(filename, "r", encoding="utf-8") as font_file:
        lines = font_file.read()
        unicode_str = re.sub(
            re.escape("static uint8_t unicode[] = {\n")
            + r"((0[xX][\da-fA-F]{2},)\n?)*0[xX][\da-fA-F]{2}\n};",
            content_kff,
            lines,
        )

    if overwrite:
        with open(filename, "w", encoding="utf-8") as save_file:
            save_file.write(unicode_str)

        # Also replace for bit and yahboom
        if font_name == FONT16:
            filename = maixpy_path_start + "bit" + maixpy_path_end
            with open(filename, "w", encoding="utf-8") as save_file:
                save_file.write(unicode_str)

            filename = maixpy_path_start + "yahboom" + maixpy_path_end
            with open(filename, "w", encoding="utf-8") as save_file:
                save_file.write(unicode_str)
    else:
        with open(filename_kff + "_font.c", "w", encoding="utf-8") as save_file:
            save_file.write(unicode_str)

    # Deletes the temporary kff file
    os.remove(filename_kff + ".kff")


if __name__ == "__main__":
    REPLACE = False
    if len(sys.argv) > 1:
        REPLACE = True

    # generate kff files
    open_bdf_save_kff(FONT14, 8, 14)
    open_bdf_save_kff(FONT16, 8, 16)
    open_bdf_save_kff(FONT24, 12, 24)

    # generate new font.c files (delete kff files)
    save_new_fontc(FONT14, REPLACE)
    save_new_fontc(FONT16, REPLACE)
    save_new_fontc(FONT24, REPLACE)
