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

__b43chars = b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ$*+-./:'
assert len(__b43chars) == 43

__b58chars = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
assert len(__b58chars) == 58
	
def try_decode(v):
	for base in [43, 58, 64]:
		try:
			return (base_decode(v, base), base)
		except: pass
	raise ValueError('failed to decode')

def base_decode(v, base):
	v = bytearray(v, 'ascii') if isinstance(v, str) else bytearray(v)
	if base not in (43, 58, 64):
		raise ValueError('not supported base: {}'.format(base))
	chars = __b58chars
	if base == 43:
		chars = __b43chars
	elif base == 64:
		return a2b_base64(bytes(v))
	long_value = 0
	power_of_base = 1
	for c in reversed(v):
		digit = chars.find(bytes([c]))
		if digit == -1:
			raise ValueError('forbidden character {} for base {}'.format(c, base))
		long_value += digit * power_of_base
		power_of_base *= base
	result = bytearray()
	while long_value >= 256:
		div, mod = divmod(long_value, 256)
		result.append(mod)
		long_value = div
	result.append(long_value)
	nPad = 0
	for c in v:
		if c == chars[0]:
			nPad += 1
		else:
			break
	result.extend(b'\x00' * nPad)
	return bytes(reversed(result))

def base_encode(v, base):
	v = bytearray(v, 'ascii') if isinstance(v, str) else bytearray(v)
	if base not in (43, 58, 64):
		raise ValueError('not supported base: {}'.format(base))
	chars = __b58chars
	if base == 43:
		chars = __b43chars
	elif base == 64:
		return b2a_base64(bytes(v))
	long_value = 0
	power_of_base = 1
	for c in reversed(v):
		long_value += power_of_base * c
		power_of_base <<= 8
	result = bytearray()
	while long_value >= base:
		div, mod = divmod(long_value, base)
		result.append(chars[mod])
		long_value = div
	result.append(chars[long_value])
	# Bitcoin does a little leading-zero-compression:
	# leading 0-bytes in the input become leading-1s
	nPad = 0
	for c in v:
		if c == 0x00:
			nPad += 1
		else:
			break
	result.extend(bytearray(chars[0] * nPad))
	return bytes(reversed(result))