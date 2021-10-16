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
from board import board_info
from fpioa_manager import fm
from machine import UART
from thermal import AdafruitThermalPrinter

class Printer:
	def __init__(self, baudrate, paper_width):
		self.paper_width = paper_width

		try:
			fm.register(board_info.CONNEXT_A, fm.fpioa.UART2_TX, force=False)
			fm.register(board_info.CONNEXT_B, fm.fpioa.UART2_RX, force=False)
			self.thermal_printer = AdafruitThermalPrinter(UART.UART2, baudrate)
			if not self.thermal_printer.has_paper():
				raise ValueError('missing paper')
		except:
			self.thermal_printer = None

	def qr_data_width(self):
		""" This method returns a smaller width for the QR to be generated
	 		within, which we will then scale up to fit the display's width.
			We do this because the QR would be too dense to be readable
			by most devices otherwise.
	   	"""
		return self.paper_width // 6

	def clear(self):
		if not self.is_connected():
			return
		# A full reset zeroes all memory buffers
		self.thermal_printer.full_reset()

	def is_connected(self):
		return self.thermal_printer is not None

	def print_qr_code(self, qr_code):
		""" Prints a QR code, scaling it up as large as possible"""
		if not self.is_connected():
			raise ValueError('no printer found')

		lines = qr_code.strip().split('\n')
  
		width = len(lines)
		height = len(lines)
  
		scale = self.paper_width // width
		for y in range(height):
			# Scale the line (width) by scaling factor
			line_y = ''.join([char * scale for char in lines[y]])
			line_bytes = bitstring_to_bytes(line_y)
			# Print height * scale lines out to scale by 
			for _ in range(scale):
				self.thermal_printer.write_bytes(18, 42, 1, len(line_bytes))
				self.thermal_printer.write_bytes(line_bytes)
				self.thermal_printer.timeout_set(self.thermal_printer.dot_print_time)
		self.thermal_printer.feed(3)
   
def bitstring_to_bytes(s):
	return int(s, 2).to_bytes((len(s) + 7) // 8, 'big')