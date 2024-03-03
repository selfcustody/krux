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

"""Merge multiple hex files into one."""

import sys

def hexmerge(filenames=None):
    if filenames is None:
        raise Exception("ERROR: Provide the filename.bdf as argument")
    
    if type(filenames) is str:
        filenames = [filenames]
    
    characters = {}

    codepoint_list = []
    for filename in filenames:
        with open(filename, "r", encoding="utf-8") as font_file:
            lines = font_file.readlines()
            for line in lines:
                if not line.strip():
                    continue
                codepoint, glyph = line.replace("\n", "").split(":")
                if codepoint not in characters:
                    characters[codepoint] = glyph
                else:
                    if int(characters[codepoint], 16) == 0:
                        characters[codepoint] = glyph
    for codepoint, glyph in sorted(characters.items(), key=lambda s: s[0]):
        codepoint_list.append(f"{codepoint}:{glyph}")

    return codepoint_list


if __name__ == '__main__':
    if len(sys.argv) > 1:
        print('\n'.join(hexmerge(sys.argv[1:])))
    else:
        raise Exception("ERROR: Provide the filename.hex as argument")