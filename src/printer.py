from board import board_info
from fpioa_manager import fm
from machine import UART
from thermal import Adafruit_Thermal

MAX_PRINT_WIDTH = const(384)

class Printer:
	def __init__(self):
		self.thermal_printer = None
		try:
			fm.register(board_info.CONNEXT_A, fm.fpioa.UART2_TX, force=False)
			fm.register(board_info.CONNEXT_B, fm.fpioa.UART2_RX, force=False)
			thermal_printer = Adafruit_Thermal(UART.UART2, 9600, heattime=255)
			if thermal_printer.hasPaper():
				self.thermal_printer = thermal_printer
		except:
			pass

	def clear(self):
		if not self.is_connected():
			return
		# A full reset zeroes all memory buffers
		self.thermal_printer.fullReset()
   
	def is_connected(self):
		return self.thermal_printer is not None

	def print_qr_code(self, qr_code, padding=0):
		""" Prints a QR code, scaling it up as large as possible"""
		if not self.is_connected():
			raise ValueError('No printer found')

		lines = qr_code.strip().split('\n')
  
		width = len(lines)
		height = len(lines)
  
		scale = (MAX_PRINT_WIDTH - padding * 2) // width
		for y in range(height):
			# Scale the line (width) by scaling factor
			line_y = ''.join([char * scale for char in lines[y]])
			line_bytes = bitstring_to_bytes(line_y)
			# Print height * scale lines out to scale by 
			for _ in range(scale):
				self.thermal_printer.writeBytes(18, 42, 1, len(line_bytes))
				self.thermal_printer.uart.write(line_bytes)
				self.thermal_printer.timeoutSet(self.thermal_printer.dotPrintTime)
		self.thermal_printer.prevByte = '\n'
		self.thermal_printer.feed(3)
   
def bitstring_to_bytes(s):
	return int(s, 2).to_bytes((len(s) + 7) // 8, 'big')