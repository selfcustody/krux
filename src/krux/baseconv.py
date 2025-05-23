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

B43CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ$*+-./:"
assert len(B43CHARS) == 43

B58CHARS = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
assert len(B58CHARS) == 58


def base_decode(v, base):
    """Decodes str v from base encoding and returns as bytes"""
    if not isinstance(v, str):
        raise TypeError("Invalid value, expected str")
    if base not in (43, 58, 64):
        raise ValueError("not supported base: {}".format(base))

    if v == "":
        return b""

    # Base64 is a special case: We just use binascii's implementation without
    # performing bitcoin-specific padding logic
    if base == 64:
        return a2b_base64(v)

    chars = B58CHARS if base == 58 else B43CHARS
    long_value = 0
    power_of_base = 1
    for char in reversed(v):
        digit = chars.find(char)
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
        if char == chars[0]:
            n_pad += 1
        else:
            break
    if n_pad > 0:
        result.extend(b"\x00" * n_pad)
    return bytes(reversed(result))


def base_encode(v, base):
    """Encodes the bytes data in v as base and returns as str"""
    if not isinstance(v, bytes):
        raise TypeError("Invalid value, expected bytes")
    if base not in (43, 58, 64):
        raise ValueError("not supported base: {}".format(base))

    if v == b"":
        return ""

    # Base64 is a special case: We just use binascii's implementation without
    # performing bitcoin-specific padding logic. b2a_base64 always adds a \n
    # char at the end which we strip before returning
    if base == 64:
        return b2a_base64(v).rstrip().decode()

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
    return bytes(reversed(result)).decode()


def detect_encodings(str_data):
    """Detects which encodings this data str might be, returns list"""
    from binascii import unhexlify

    if not isinstance(str_data, str):
        raise TypeError("detect_encodings() expected str")

    encodings = []

    # get min and max characters (sorted by ordinal value),
    # check most restrictive encodings first

    min_chr = min(str_data)
    max_chr = max(str_data)

    # might it be hex
    if len(str_data) % 2 == 0 and "0" <= min_chr:
        if max_chr <= "F":
            try:
                unhexlify(str_data)
                encodings.append("HEX")
            except:
                pass
        elif max_chr <= "f":
            try:
                unhexlify(str_data)
                encodings.append("hex")
            except:
                pass

    # might it be base43
    if "$" <= min_chr and max_chr <= "Z":
        try:
            base_decode(str_data, 43)
            encodings.append(43)
        except:
            pass

    # might it be base64
    if "+" <= min_chr and max_chr <= "z":
        try:
            base_decode(str_data, 64)
            encodings.append(64)
        except:
            pass

    # might it be ascii
    if ord(max_chr) <= 127:
        encodings.append("ascii")

    # might it be latin-1 or utf8
    if 128 <= ord(max_chr) <= 255:
        encodings.append("latin-1")
    else:
        encodings.append("utf8")

    return encodings
