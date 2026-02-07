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
import sys
from unittest import mock
import qrcode as qrc


def encode(data):
    # Changed from pyqrcode to qrcode
    qr = qrc.QRCode(error_correction=qrc.constants.ERROR_CORRECT_L)
    qr.add_data(data)
    qr.make(fit=True)

    matrix = qr.get_matrix()
    size = len(matrix)

    # Same logic as old pyqrcode
    byte_length = (size * size + 7) // 8
    binary_qr = bytearray(b"\x00" * byte_length)

    for y in range(size):
        for x in range(size):
            bit_index = y * size + x
            if matrix[y][x]:
                byte_idx = bit_index >> 3
                bit_in_byte = bit_index & 7   # % 8
                binary_qr[byte_idx] |= (1 << bit_in_byte)

    return binary_qr

# delete imported qrcode lib
del sys.modules["qrcode"]

# mock the qrcode lib from Krux
if "qrcode" not in sys.modules:
    sys.modules["qrcode"] = mock.MagicMock(
        encode=encode,
    )
