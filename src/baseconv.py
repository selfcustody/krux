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
from binascii import a2b_base64, b2a_base64

B43CHARS = b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ$*+-./:'
assert len(B43CHARS) == 43

B58CHARS = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
assert len(B58CHARS) == 58

def try_decode(v):
    """Exhaustively tries to decode v from whichever base encoding it is in"""
    for base in [43, 58, 64]:
        try:
            return (base_decode(v, base), base)
        except:
            pass
    raise ValueError('failed to decode')

def base_decode(v, base):
    """Decodes v from base encoding and returns the decoded bytes"""
    v = bytearray(v, 'ascii') if isinstance(v, str) else bytearray(v)
    if base not in (43, 58, 64):
        raise ValueError('not supported base: {}'.format(base))
    chars = B58CHARS
    if base == 43:
        chars = B43CHARS
    elif base == 64:
        return a2b_base64(bytes(v))
    long_value = 0
    power_of_base = 1
    for char in reversed(v):
        digit = chars.find(bytes([char]))
        if digit == -1:
            raise ValueError('forbidden character {} for base {}'.format(char, base))
        long_value += digit * power_of_base
        power_of_base *= base
    result = bytearray()
    while long_value >= 256:
        div, mod = divmod(long_value, 256)
        result.append(mod)
        long_value = div
    result.append(long_value)
    n_pad = 0
    for char in v:
        if char == chars[0]:
            n_pad += 1
        else:
            break
    result.extend(b'\x00' * n_pad)
    return bytes(reversed(result))

def base_encode(v, base):
    """Encodes the data in v as base and returns as bytes"""
    v = bytearray(v, 'ascii') if isinstance(v, str) else bytearray(v)
    if base not in (43, 58, 64):
        raise ValueError('not supported base: {}'.format(base))
    chars = B58CHARS
    if base == 43:
        chars = B43CHARS
    elif base == 64:
        return b2a_base64(bytes(v))
    long_value = 0
    power_of_base = 1
    for char in reversed(v):
        long_value += power_of_base * char
        power_of_base <<= 8
    result = bytearray()
    while long_value >= base:
        div, mod = divmod(long_value, base)
        result.append(chars[mod])
        long_value = div
    result.append(chars[long_value])
    # Bitcoin does a little leading-zero-compression:
    # leading 0-bytes in the input become leading-1s
    n_pad = 0
    for char in v:
        if char == 0x00:
            n_pad += 1
        else:
            break
    result.extend(bytearray(chars[0] * n_pad))
    return bytes(reversed(result))
