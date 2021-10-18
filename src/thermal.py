#*************************************************************************
# This is a Python library for the Adafruit Thermal Printer.
# Pick one up at --> http://www.adafruit.com/products/597
# These printers use TTL serial to communicate, 2 pins are required.
# IMPORTANT: On 3.3V systems (e.g. Raspberry Pi), use a 10K resistor on
# the RX pin (TX on the printer, green wire), or simply leave unconnected.
#
# Adafruit invests time and resources providing this open source code.
# Please support Adafruit and open-source hardware by purchasing products
# from Adafruit!
#
# Written by Limor Fried/Ladyada for Adafruit Industries.
# Python port by Phil Burgess for Adafruit Industries.
# MIT license, all text above must be included in any redistribution.
#*************************************************************************
import time
from machine import UART

class AdafruitThermalPrinter:
	def __init__(self, port, baudrate, heat_time=255):
		# Calculate time to issue one byte to the printer.
		# 11 bits (not 8) to accommodate idle, start and
		# stop bits.  Idle time might be unnecessary, but
		# erring on side of caution here.
		self.byte_time = 11.0 / float(baudrate)
		self.heat_time = heat_time
		self.resume_time = 0.0
		self.uart_conn = UART(port, baudrate)
		self.initialize()

	def initialize(self):
		# The printer can't start receiving data immediately
		# upon power up -- it needs a moment to cold boot
		# and initialize.  Allow at least 1/2 sec of uptime
		# before printer can receive data.
		self.timeout_set(0.5)

		self.wake()
		self.reset()

		# Description of print settings from p. 23 of manual:
		# ESC 7 n1 n2 n3 Setting Control Parameter Command
		# Decimal: 27 55 n1 n2 n3
		# max heating dots, heating time, heating interval
		# n1 = 0-255 Max heat dots, Unit (8dots), Default: 7 (64 dots)
		# n2 = 3-255 Heating time, Unit (10us), Default: 80 (800us)
		# n3 = 0-255 Heating interval, Unit (10us), Default: 2 (20us)
		# The more max heating dots, the more peak current
		# will cost when printing, the faster printing speed.
		# The max heating dots is 8*(n1+1).  The more heating
		# time, the more density, but the slower printing
		# speed.  If heating time is too short, blank page
		# may occur.  The more heating interval, the more
		# clear, but the slower printing speed.

		self.write_bytes(
			27,             # Esc
			55,             # 7 (print settings)
			11,             # Heat dots
			self.heat_time, # Lib default
			40)             # Heat interval

		# Description of print density from p. 23 of manual:
		# DC2 # n Set printing density
		# Decimal: 18 35 n
		# D4..D0 of n is used to set the printing density.
		# Density is 50% + 5% * n(D4-D0) printing density.
		# D7..D5 of n is used to set the printing break time.
		# Break time is n(D7-D5)*250us.
		# (Unsure of default values -- not documented)
		print_density = 10 # 100%
		print_break_time = 2 # 500 uS

		self.write_bytes(
			18, # DC2
			35, # Print density
			(print_break_time << 5) | print_density)
		self.dot_print_time = 0.03
		self.dot_feed_time = 0.0021

	def wake(self):
		self.timeout_set(0)
		self.write_bytes(255)
		time.sleep(0.05)            # 50 ms
		self.write_bytes(27, 118, 0) # Sleep off (important!)

	def reset(self):
		self.write_bytes(27, 64) # Esc @ = init command
		self.char_height = 24
		# Configure tab stops on recent printers
		self.write_bytes(27, 68)         # Set tab stops
		self.write_bytes(4, 8, 12, 16) # every 4 columns,
		self.write_bytes(20, 24, 28, 0) # 0 is end-of-list.

	def full_reset(self):
		# Performs a full hardware reset which clears both printer buffer and receive buffer
		# A full reset can only be done by setting an image in nonvolatile memory, so
		# we will send a 1x1 image with 0 as its pixel value in order to initiate the reset
		self.write_bytes(28, 113, 1, 1, 0, 1, 0, 0)
		self.initialize()

	def write_bytes(self, *args):
		for arg in args:
			self.timeout_wait()
			self.timeout_set(len(args) * self.byte_time)
			self.uart_conn.write(arg if isinstance(arg, bytes) else bytes([arg]))

	# Sets estimated completion time for a just-issued task.
	def timeout_set(self, x):
		self.resume_time = time.time() + x

	# Waits (if necessary) for the prior task to complete.
	def timeout_wait(self):
		while (time.time() - self.resume_time) < 0: pass

	def feed(self, x=1):
		self.write_bytes(27, 100, x)
		self.timeout_set(self.dot_feed_time * self.char_height)

	def has_paper(self):
		self.write_bytes(27, 118, 0)
		# Bit 2 of response seems to be paper status
		stat = ord(self.uart_conn.read(1)) & 0b00000100
		# If set, we have paper; if clear, no paper
		return stat == 0
