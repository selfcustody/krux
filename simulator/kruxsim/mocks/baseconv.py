# The MIT License (MIT)

# Copyright (c) 2021-2025 Krux contributors

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
from krux.baseconv import base_encode, base_decode

B32CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

class base43:

    def encode(data):
        """Encodes data to Base43."""
        return base_encode(data, 43)
    
    def decode(encoded_str):
        """Decodes a Base43 string."""
        return base_decode(encoded_str, 43)


class base32:
    """
    Mock for the base32 module.
    """

    @staticmethod
    def b32encode(data):
        """Mock implementation of b32encode."""
        return data.encode('utf-8').hex().upper()

    @staticmethod
    def b32decode(data):
        """Mock implementation of b32decode."""
        return bytes.fromhex(data.lower()).decode('utf-8')


    def decode(encoded_str):
        """Decodes a Base32 string"""
        base32_index = {ch: index for index, ch in enumerate(B32CHARS)}

        # Strip padding
        encoded_str = encoded_str.rstrip("=")

        buffer = 0
        bits_left = 0
        decoded_bytes = bytearray()

        for char in encoded_str:
            if char not in base32_index:
                raise ValueError("Invalid Base32 character: %s" % char)
            index = base32_index[char]
            buffer = (buffer << 5) | index
            bits_left += 5

            while bits_left >= 8:
                bits_left -= 8
                decoded_bytes.append((buffer >> bits_left) & 0xFF)
                buffer &= (1 << bits_left) - 1  # Keep only the remaining bits

        return bytes(decoded_bytes)


    def encode_stream(data, add_padding):
        """A streaming base32 encoder"""
        buffer = 0
        bits_left = 0
        chars_yielded = 0

        for byte in data:
            buffer = (buffer << 8) | byte
            bits_left += 8

            while bits_left >= 5:
                bits_left -= 5
                yield B32CHARS[(buffer >> bits_left) & 0x1F]
                chars_yielded += 1
                buffer &= (1 << bits_left) - 1  # Keep only the remaining bits

        if bits_left > 0:
            buffer <<= 5 - bits_left
            yield B32CHARS[buffer & 0x1F]
            chars_yielded += 1

        # Padding
        if add_padding:
            padding_length = (8 - (chars_yielded % 8)) % 8
            for _ in range(padding_length):
                yield "="

    def encode(data, add_padding=True):
        return ''.join(base32.encode_stream(data, add_padding))

if "base32" not in sys.modules:
    sys.modules["base32"] = base32

if "base43" not in sys.modules:
    sys.modules["base43"] = base43