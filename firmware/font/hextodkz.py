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

with open(sys.argv[1], "r") as input_file:
    # Read in a hex formatted bitmap font file
    lines = input_file.readlines()

    # Strip out the unicode code point prefix at the beginning of each line
    lines = map(lambda line: line.split(":")[1].rstrip("\n"), lines)
    # Break up each line's hex into comma-separated bytes
    lines = list(
        map(
            lambda line: ",".join(
                ["0x" + line[i] + line[i + 1] for i in range(0, len(line), 2)]
            ),
            lines,
        )
    )

    # Use only the first $limit bitmaps
    limit = len(lines)
    if len(sys.argv) == 4:
        limit = sys.argv[3]

    print(",\n".join(list(lines)[:limit]))
