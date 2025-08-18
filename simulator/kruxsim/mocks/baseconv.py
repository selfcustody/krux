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
import base64
from krux import baseconv

class base43:

    def encode(data, add_padding=False):
        """Encodes data to Base43."""
        return baseconv.pure_python_base_encode(data, 43)
    
    def decode(encoded_str):
        """Decodes a Base43 string."""
        return baseconv.pure_python_base_decode(encoded_str, 43)


class base32:
    """
    Mock for the base32 module.
    """
    def encode(data, add_padding=False):
        """Encodes data to Base32."""
        encoded = base64.b32encode(data).decode('utf-8')
        if not add_padding:
            encoded = encoded.rstrip('=')
        return encoded

    def decode(encoded_str):
        """Decodes a Base32 string."""
        try:
            len_pad = (8 - len(encoded_str) % 8) % 8
            decoded = base64.b32decode(encoded_str + ("=" * len_pad))
        except ValueError as e:
            raise ValueError("Invalid Base32 string: %s" % e)

        return decoded

   

if "base32" not in sys.modules:
    sys.modules["base32"] = base32

if "base43" not in sys.modules:
    sys.modules["base43"] = base43
