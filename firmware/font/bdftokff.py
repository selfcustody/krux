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
import re
import bdftohex, hexfill, hexmerge, hextokff

FONT14 = "ter-u14n"
FONT16 = "ter-u16n"
FONT24 = "ter-u24b"

def open_bdf_save_kff(filename, width, height):
    filename_kff = 'm5stickv'
    if filename == FONT16:
        filename_kff = 'bit_dock_yahboom'
    elif filename == FONT24:
        filename_kff = 'amigo'

    # Create hexfile based on bdf
    font_hex = '\n'.join(bdftohex.bdftohex(filename + '.bdf')) + '\n'
    with open(filename + '.hex', "w", encoding="utf-8") as save_file:
        save_file.write(font_hex)

    # Fill the hexfile with missing empty glyphs
    font_hex_filled = ''.join(hexfill.hexfill(filename + '.hex', width, height)).strip()
    with open(filename + '.hex', "w", encoding="utf-8") as save_file:
        save_file.write(font_hex_filled)

    # Merges the hexfile empty glyphs with the its corresponding contents (can be used with multiple files)
    font_hex_merged = '\n'.join(hexmerge.hexmerge(filename + '.hex')) + '\n'
    with open(filename + '.hex', "w", encoding="utf-8") as save_file:
        save_file.write(font_hex_merged)

    # Creates the Krux font file, to be used on
    # ../MaixPy/projects/<device_name>/compile/overrides/components/micropython/port/src/omv/img/font.c
    # replacing the contents of the unicode[] variable
    font_kff = hextokff.hextokff(filename + '.hex', width, height)
    with open(filename_kff + '.kff', "w", encoding="utf-8") as save_file:
        save_file.write(font_kff)

    # Deletes the temporary hexfile
    os.remove(filename + '.hex')

def save_new_fontc(font_name):
    device_name = filename_kff = 'm5stickv'
    if font_name == FONT16:
        filename_kff = 'bit_dock_yahboom'
        device_name = 'dock'
    elif font_name == FONT24:
        device_name = filename_kff = 'amigo'

    with open(filename_kff + '.kff', "r", encoding="utf-8") as read_file:
        content_kff = read_file.read()

    content_kff = 'static uint8_t unicode[] = {\n' + content_kff + '\n};'

    filename = '../MaixPy/projects/maixpy_'+ device_name +'/compile/overrides/components/micropython/port/src/omv/img/font.c'
    with open(filename, "r", encoding="utf-8") as font_file:
        lines = font_file.read()
        unicode_str = re.sub(re.escape('static uint8_t unicode[] = {\n') +
                      r'((\dx[0-9A-F]{2},)\n?)*\dx[0-9A-F]{2}\n};',
                      content_kff
                      ,lines)
        
    with open(filename_kff + '_font.c', 'w', encoding='utf-8') as save_file:
        save_file.write(unicode_str)

    # Deletes the temporary kff file
        os.remove(filename_kff + '.kff')


if __name__ == '__main__':
    # generate kff files
    open_bdf_save_kff(FONT14, 8, 14)
    open_bdf_save_kff(FONT16, 8, 16)
    open_bdf_save_kff(FONT24, 12, 24)

    # generate new font.c files (delete kff files)
    save_new_fontc(FONT14)
    save_new_fontc(FONT16)
    save_new_fontc(FONT24)
