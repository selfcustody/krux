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
import math
import qrcode

QR_FORMAT_NONE  = const(0)
QR_FORMAT_PMOFN = const(1)

PMOFN_MIN_PART_SIZE = const(80)

def to_pmofn_qr_codes(data, min_part_size=PMOFN_MIN_PART_SIZE):
	""" Breaks data up into many 'pMofN part' chunks """
	codes = []
	if len(data) > min_part_size:
		num_parts = round(len(data) / min_part_size)
		mod_part_size = len(data) % min_part_size
		add_part_size = math.ceil(mod_part_size / num_parts) if mod_part_size < (min_part_size / 2) else math.floor((mod_part_size - min_part_size) / num_parts)
		part_size = min_part_size + add_part_size
		last_index = 0
		for index in range(1, num_parts):
			part = 'p' + str(index) + 'of' + str(num_parts) + ' ' + data[(index - 1) * part_size:index * part_size]
			codes.append(qrcode.encode_to_string(part))
			last_index = index * part_size
		part = 'p' + str(num_parts) + 'of' + str(num_parts) + ' ' + data[last_index:]
		codes.append(qrcode.encode_to_string(part))
	else:
		codes.append(qrcode.encode_to_string(data))
	return codes

def to_qr_codes(data, format=QR_FORMAT_PMOFN):
	if format == QR_FORMAT_PMOFN:
		return to_pmofn_qr_codes(data)
	return [qrcode.encode_to_string(data)]

def parse_pmofn_qr_part(data):
	of_split = data.split('of', 1)
	part_index = int(of_split[0][1:])
	part_total = int(of_split[1][:of_split[1].index(' ')])
	part = data[data.index(' ') + 1:]
	return part, part_index, part_total

def parse_qr_part(data):
	if data.startswith('p') and data.index('of') <= 5:
		return parse_pmofn_qr_part(data)
	return data, 1, 1

def join_pmofn_qr_parts(parts):
	code = ''
	for part in parts:
		code_part, _, _ = parse_pmofn_qr_part(part)
		code += code_part
	return code
	
def join_qr_parts(parts):
	if parts[0].startswith('p') and 'of' in parts[0]:
		return join_pmofn_qr_parts(parts)
	return ''.join(parts)
