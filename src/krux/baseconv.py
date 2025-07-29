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


def base_decode(v, base):
    """Abstraction to decode the str data in v as base; returns bytes"""
    if not isinstance(v, str):
        raise TypeError("Invalid value, expected str")

    if v == "":
        return b""

    # Base32 and Base43 are implemented custom in MaixPy on k210, else in python for simulator
    # Base58 is implemented in pure_python_base_decode() below
    # Base64 is a special case: We just use binascii's implementation without
    # performing bitcoin-specific padding logic
    if base == 32:
        import base32

        return base32.decode(v)
    if base == 43:
        import base43

        return base43.decode(v)
    if base == 58:
        return pure_python_base_decode(v, 58)
    if base == 64:
        return a2b_base64(v)

    raise ValueError("not supported base: {}".format(base))


def base_encode(v, base):
    """Abstraction to encode the bytes data in v as base; returns str"""
    if not isinstance(v, bytes):
        raise TypeError("Invalid value, expected bytes")

    if v == b"":
        return ""

    # Base32 and Base43 are implemented custom in MaixPy on k210, else in python for simulator
    # Base58 is implemented in pure_python_base_encode() below
    # Base64 is a special case: We just use binascii's implementation without
    # performing bitcoin-specific padding logic. b2a_base64 always adds a \n
    # char at the end which we strip before returning
    if base == 32:
        import base32

        return base32.encode(v, False)
    if base == 43:
        import base43

        return base43.encode(v, False)
    if base == 58:
        return pure_python_base_encode(v, 58)
    if base == 64:
        return b2a_base64(v).rstrip().decode()

    raise ValueError("not supported base: {}".format(base))


def hint_encodings(str_data):
    """NON-VERIFIED encoding hints of what input string might be, returns list"""

    if not isinstance(str_data, str):
        raise TypeError("hint_encodings() expected str")

    encodings = []

    # get min and max characters (sorted by ordinal value),
    # check most restrictive encodings first
    # is not strict -- does not try to decode -- assumptions are made

    min_chr = min(str_data)
    max_chr = max(str_data)

    # might it be hex
    if len(str_data) % 2 == 0 and "0" <= min_chr:
        if max_chr <= "F":
            encodings.append("HEX")
        elif max_chr <= "f":
            encodings.append("hex")

    # might it be base32
    if "2" <= min_chr and max_chr <= "Z":
        encodings.append(32)

    # might it be base43
    if "$" <= min_chr and max_chr <= "Z":
        encodings.append(43)

    # might it be base58? currently unused
    # if "1" <= min_chr and max_chr <= "z":
    #     encodings.append(58)

    # might it be base64
    if "+" <= min_chr and max_chr <= "z":
        encodings.append(64)

    # might it be ascii
    if ord(max_chr) <= 127:
        encodings.append("ascii")

    # might it be latin-1 or utf8
    if 128 <= ord(max_chr) <= 255:
        encodings.append("latin-1")
    else:
        encodings.append("utf8")

    return encodings


# pure-python encoder/decoder for base43 and base58 below
B43CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ$*+-./:"
B58CHARS = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def pure_python_base_decode(v, base):
    """decode str v from base encoding; returns bytes"""
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


def pure_python_base_encode(v, base):
    """decode bytes v from base encoding; returns str"""
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
