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
from binascii import a2b_base64, b2a_base64

B32CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
assert len(B32CHARS) == 32

B43CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ$*+-./:"
assert len(B43CHARS) == 43

B58CHARS = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
assert len(B58CHARS) == 58


def base_decode(v, base):
    """Decodes v from base encoding and returns the decoded bytes"""
    if base not in (43, 58, 64):
        raise ValueError("not supported base: {}".format(base))

    if v == b"":
        return v

    # Base64 is a special case: We just use binascii's implementation without
    # performing bitcoin-specific padding logic
    if base == 64:
        return a2b_base64(v)

    chars = B58CHARS if base == 58 else B43CHARS
    long_value = 0
    power_of_base = 1
    for char in reversed(v):
        digit = chars.find(bytes([char]).decode())
        if digit == -1:
            raise ValueError("forbidden character {} for base {}".format(char, base))
        long_value += digit * power_of_base
        power_of_base *= base
    result = bytearray()
    while long_value >= 256:
        div, mod = divmod(long_value, 256)
        result.append(mod)
        long_value = div
    if long_value > 0:
        result.append(long_value)
    n_pad = 0
    for char in v:
        if bytes([char]).decode() == chars[0]:
            n_pad += 1
        else:
            break
    if n_pad > 0:
        result.extend(b"\x00" * n_pad)
    return bytes(reversed(result))


def base_encode(v, base):
    """Encodes the data in v as base and returns as bytes"""
    if base not in (43, 58, 64):
        raise ValueError("not supported base: {}".format(base))

    if v == b"":
        return v

    # Base64 is a special case: We just use binascii's implementation without
    # performing bitcoin-specific padding logic. b2a_base64 always adds a \n
    # char at the end which we strip before returning
    if base == 64:
        return b2a_base64(v).rstrip()

    chars = B58CHARS if base == 58 else B43CHARS
    long_value = 0
    power_of_base = 1
    for char in reversed(v):
        long_value += power_of_base * char
        power_of_base <<= 8
    result = bytearray()
    while long_value >= base:
        div, mod = divmod(long_value, base)
        result.extend(chars[mod].encode())
        long_value = div
    if long_value > 0:
        result.extend(chars[long_value].encode())
    # Bitcoin does a little leading-zero-compression:
    # leading 0-bytes in the input become leading-1s
    n_pad = 0
    for char in v:
        if char == 0x00:
            n_pad += 1
        else:
            break
    if n_pad > 0:
        result.extend((chars[0] * n_pad).encode())
    return bytes(reversed(result))


def base32_decode(encoded_str):
    """Decodes a Base32 string according to RFC 4648."""

    # Reverse lookup table
    base32_index = {ch: index for index, ch in enumerate(B32CHARS)}

    # Strip padding
    encoded_str = encoded_str.rstrip("=")

    # Convert Base32 characters to binary string
    bits = ""
    for char in encoded_str:
        if char not in base32_index:
            raise ValueError("Invalid Base32 character: %s" % char)
        index = base32_index[char]
        binary_str = ""
        for i in range(5):
            binary_str = str(index & 1) + binary_str
            index >>= 1
        bits += binary_str

    # Convert binary string to bytes
    n = len(bits) // 8 * 8  # Only take complete groups of 8 bits
    bytes_list = []
    for i in range(0, n, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | int(bits[i + j])
        bytes_list.append(byte)

    return bytes(bytes_list)


def base32_encode(data):
    """Encodes bytes into a Base32 string according to RFC 4648."""

    def byte_to_bin(byte):
        """Convert a single byte to a binary string."""
        return "".join(str((byte >> i) & 1) for i in range(7, -1, -1))

    # Collect bits as a string of '1's and '0's
    bits = "".join(byte_to_bin(byte) for byte in data)

    # Prepare to segment bits into groups of 5
    padding_length = (5 - len(bits) % 5) % 5
    bits += "0" * padding_length  # Pad bits to make length a multiple of 5

    # Encode bits to Base32
    encoded = ""
    for i in range(0, len(bits), 5):
        index = int(bits[i : i + 5], 2)
        encoded += B32CHARS[index]

    # Calculate required padding for the encoded string
    padding = "=" * ((8 - len(encoded) % 8) % 8)
    return encoded + padding
