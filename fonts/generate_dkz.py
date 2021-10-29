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

height=int(sys.argv[2])

with open(sys.argv[1], 'r') as input_file:
    # Read in a hex formatted bitmap font file
    lines = input_file.readlines()
    # Zero out > height pixel width characters since they cannot be displayed on the
    # tiny screen
    lines = list(map(
        lambda line: line.split(':')[0] + ':' + ('0' * 2*height)
        if len(line) > height*2+6 else line,
        lines
    ))
    i = 0
    while i < len(lines):
        codepoint = int(lines[i].split(':')[0], 16)
        while i < codepoint:
            lines.insert(i, hex(i).lstrip('0x') + ':' + ('0' * 2*height))
            i += 1
        i += 1
    # Strip out the unicode code point prefix at the beginning of each line
    lines = map(lambda line: line.split(':')[1].rstrip('\n'), lines)
    # Break up each line's hex into comma-separated bytes
    lines = map(
        lambda line: ','.join(['0x' + line[i] + line[i+1] for i in range(0, len(line), 2)]),
        lines
    )
    # Use only the first 33 bitmaps so that the ₿ char is included
    print(',\n'.join(list(lines)[0:33*256]))
