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
try:
	import uio as io
except ImportError:
	import io
import qrcode

def get_size(qr_code):
	size = 0
	while qr_code[size] != '\n':
		size += 1
	return size

def to_qr_codes(data, max_width):
	num_parts = 1
	part_size = len(data) // num_parts
	while True:
		part_number = ('p1of%d ' % num_parts) if num_parts > 1 else ''
		part = part_number + data[0: part_size]
		code = qrcode.encode_to_string(part)
  		if get_size(code) <= max_width:
			break
		num_parts += 1
		part_size = len(data) // num_parts
  
	for i in range(num_parts):
		part_number = ('p%dof%d ' % (i + 1, num_parts)) if num_parts > 1 else ''
		part = None
		if i == num_parts - 1:
			part = part_number + data[i * part_size:]
		else:
			part = part_number + data[i * part_size: i * part_size + part_size]
		code = qrcode.encode_to_string(part)
		yield (code, num_parts)

def parse_pmofn_qr_part(data):
	of_index = data.index('of')
	space_index = data.index(' ')
	part_index = int(data[1:of_index])
	part_total = int(data[of_index+2:space_index])
	return data[space_index + 1:], part_index, part_total

def parse_qr_part(data):
	if data.startswith('p') and data.index('of') <= 5:
		return parse_pmofn_qr_part(data)
	return data, 1, 1

def join_pmofn_qr_parts(parts):
	code_buf = io.StringIO('')
	for part in parts:
		code_part, _, _ = parse_pmofn_qr_part(part)
		code_buf.write(code_part)
	code = code_buf.getvalue()
	code_buf.close()
	return code
	
def join_qr_parts(parts):
	if parts[0].startswith('p') and 'of' in parts[0]:
		return join_pmofn_qr_parts(parts)
	return ''.join(parts)
