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
set -e

fonts=$1
width=$2
height=$3

# Convert from bdf to hex for all fonts
for font in $(echo $fonts | sed "s/,/ /g")
do
    poetry run python bdftohex.py $font.bdf > $font.hex
    poetry run python hexfill.py $font.hex $width $height > tmp.hex && cat tmp.hex > $font.hex && rm tmp.hex
done

# Merge all hex files into one
hexes=()
for font in $(echo $fonts | sed "s/,/ /g")
do
    hexes+=( $font.hex )
done
poetry run python hexmerge.py ${hexes[@]} > merged.hex

# Convert merged hex to krux format
poetry run python hextokff.py merged.hex $width $height

# Remove generated files
rm merged.hex
for font in $(echo $fonts | sed "s/,/ /g")
do
    rm $font.hex
done
