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

# This is pretty much a 1:1 direct Python port of the Adafruit_Thermal
# library for Arduino.  All methods use the same naming conventions as the
# Arduino library, with only slight changes in parameter behavior where
# needed.  This should simplify porting existing Adafruit_Thermal-based
# printer projects to Raspberry Pi, BeagleBone, etc.  See printertest.py
# for an example.
#
# One significant change is the addition of the printImage() function,
# which ties this to the Python Imaging Library and opens the door to a
# lot of cool graphical stuff!
#
# TO DO:
# - Might use standard ConfigParser library to put thermal calibration
#   settings in a global configuration file (rather than in the library).
# - Make this use proper Python library installation procedure.
# - Trap errors properly.  Some stuff just falls through right now.
# - Add docstrings throughout!

import time
import sys
import math
from machine import UART

class Adafruit_Thermal:

	resumeTime      =   0.0
	byteTime        =   0.0
	dotPrintTime    =   0.0
	dotFeedTime     =   0.0
	prevByte        =  '\n'
	column          =     0
	maxColumn       =    32
	charHeight      =    24
	lineSpacing     =     8
	barcodeHeight   =    50
	printMode       =     0
	defaultHeatTime =   120
	heatTime        = defaultHeatTime
	firmwareVersion =   268
	writeToStdout   = False

	def __init__(self, *args, **kwargs):
		# NEW BEHAVIOR: if no parameters given, output is written
		# to stdout, to be piped through 'lp -o raw' (old behavior
		# was to use default port & baud rate).
		baudrate = 9600
		if len(args) == 0:
			self.writeToStdout = True
		if len(args) == 1:
			# If only port is passed, use default baud rate.
			args = [ args[0], baudrate ]
		elif len(args) == 2:
			# If both passed, use those values.
			baudrate = args[1]

		# Firmware is assumed version 2.68.  Can override this
		# with the 'firmware=X' argument, where X is the major
		# version number * 100 + the minor version number (e.g.
		# pass "firmware=264" for version 2.64.
		self.firmwareVersion = kwargs.get('firmware', 268)

		if self.writeToStdout is False:
			# Calculate time to issue one byte to the printer.
			# 11 bits (not 8) to accommodate idle, start and
			# stop bits.  Idle time might be unnecessary, but
			# erring on side of caution here.
			self.byteTime = 11.0 / float(baudrate)
			self.uart = UART(*args)
			self.heatTime = kwargs.get('heattime', self.defaultHeatTime)
			self.initialize()
		else:
			self.reset() # Inits some vars

	def initialize(self):
		# The printer can't start receiving data immediately
		# upon power up -- it needs a moment to cold boot
		# and initialize.  Allow at least 1/2 sec of uptime
		# before printer can receive data.
		self.timeoutSet(0.5)

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

		self.writeBytes(
			27,       # Esc
			55,       # 7 (print settings)
			11,       # Heat dots
			self.heatTime, # Lib default
			40)       # Heat interval

		# Description of print density from p. 23 of manual:
		# DC2 # n Set printing density
		# Decimal: 18 35 n
		# D4..D0 of n is used to set the printing density.
		# Density is 50% + 5% * n(D4-D0) printing density.
		# D7..D5 of n is used to set the printing break time.
		# Break time is n(D7-D5)*250us.
		# (Unsure of default values -- not documented)

		printDensity   = 10 # 100%
		printBreakTime =  2 # 500 uS

		self.writeBytes(
			18, # DC2
			35, # Print density
			(printBreakTime << 5) | printDensity)
		self.dotPrintTime = 0.03
		self.dotFeedTime  = 0.0021
   
	# Because there's no flow control between the printer and computer,
	# special care must be taken to avoid overrunning the printer's
	# buffer.  Serial output is throttled based on serial speed as well
	# as an estimate of the device's print and feed rates (relatively
	# slow, being bound to moving parts and physical reality).  After
	# an operation is issued to the printer (e.g. bitmap print), a
	# timeout is set before which any other printer operations will be
	# suspended.  This is generally more efficient than using a delay
	# in that it allows the calling code to continue with other duties
	# (e.g. receiving or decoding an image) while the printer
	# physically completes the task.

	# Sets estimated completion time for a just-issued task.
	def timeoutSet(self, x):
		self.resumeTime = time.time() + x

	# Waits (if necessary) for the prior task to complete.
	def timeoutWait(self):
		if self.writeToStdout is False:
			while (time.time() - self.resumeTime) < 0: pass

	# Printer performance may vary based on the power supply voltage,
	# thickness of paper, phase of the moon and other seemingly random
	# variables.  This method sets the times (in microseconds) for the
	# paper to advance one vertical 'dot' when printing and feeding.
	# For example, in the default initialized state, normal-sized text
	# is 24 dots tall and the line spacing is 32 dots, so the time for
	# one line to be issued is approximately 24 * print time + 8 * feed
	# time.  The default print and feed times are based on a random
	# test unit, but as stated above your reality may be influenced by
	# many factors.  This lets you tweak the timing to avoid excessive
	# delays and/or overrunning the printer buffer.
	def setTimes(self, p, f):
		# Units are in microseconds for
		# compatibility with Arduino library
		self.dotPrintTime = p / 1000000.0
		self.dotFeedTime  = f / 1000000.0

	# 'Raw' byte-writing method
	def writeBytes(self, *args):
		if self.writeToStdout:
			for arg in args:
				sys.stdout.write(bytes([arg]))
		else:
			for arg in args:
				self.timeoutWait()
				self.timeoutSet(len(args) * self.byteTime)
				self.uart.write(bytes([arg]))

	# Override write() method to keep track of paper feed.
	def write(self, *data):
		for i in range(len(data)):
			c = data[i]
			if self.writeToStdout:
				sys.stdout.write(c)
				continue
			if c != 0x13:
				self.timeoutWait()
				self.uart.write(c)
				d = self.byteTime
				if ((c == '\n') or
					(self.column == self.maxColumn)):
					# Newline or wrap
					if self.prevByte == '\n':
						# Feed line (blank)
						d += ((self.charHeight +
							   self.lineSpacing) *
							  self.dotFeedTime)
					else:
						# Text line
						d += ((self.charHeight *
							   self.dotPrintTime) +
							  (self.lineSpacing *
							   self.dotFeedTime))
						self.column = 0
						# Treat wrap as newline
						# on next pass
						c = '\n'
				else:
					self.column += 1
				self.timeoutSet(d)
				self.prevByte = c

	# The bulk of this method was moved into __init__,
	# but this is left here for compatibility with older
	# code that might get ported directly from Arduino.
	def begin(self, heatTime=defaultHeatTime):
		self.writeBytes(
		  27,       # Esc
		  55,       # 7 (print settings)
		  11,       # Heat dots
		  heatTime,
		  40)       # Heat interval

	def fullReset(self):
		# Performs a full hardware reset which clears both printer buffer and receive buffer
		# A full reset can only be done by setting an image in nonvolatile memory, so
		# we will send a 1x1 image with 0 as its pixel value in order to initiate the reset
		self.writeBytes(28, 113, 1, 1, 0, 1, 0, 0)
		self.initialize()
  
	def reset(self):
		self.writeBytes(27, 64) # Esc @ = init command
		self.prevByte      = '\n' # Treat as if prior line is blank
		self.column        =  0
		self.maxColumn     = 32
		self.charHeight    = 24
		self.lineSpacing   =  6
		self.barcodeHeight = 50
		if self.firmwareVersion >= 264:
			# Configure tab stops on recent printers
			self.writeBytes(27, 68)         # Set tab stops
			self.writeBytes( 4,  8, 12, 16) # every 4 columns,
			self.writeBytes(20, 24, 28,  0) # 0 is end-of-list.

	# Reset text formatting parameters.
	def setDefault(self):
		self.online()
		self.justify('L')
		self.inverseOff()
		self.doubleHeightOff()
		self.setLineHeight(30)
		self.boldOff()
		self.underlineOff()
		self.setBarcodeHeight(50)
		self.setSize('s')
		self.setCharset()
		self.setCodePage()

	def test(self):
		self.write("Hello world!".encode('cp437', 'ignore'))
		self.feed(2)

	def testPage(self):
		self.writeBytes(18, 84)
		self.timeoutSet(
		  self.dotPrintTime * 24 * 26 +
		  self.dotFeedTime * (6 * 26 + 30))

	def setBarcodeHeight(self, val=50):
		if val < 1: val = 1
		self.barcodeHeight = val
		self.writeBytes(29, 104, val)

	UPC_A   =  0
	UPC_E   =  1
	EAN13   =  2
	EAN8    =  3
	CODE39  =  4
	I25     =  5
	CODEBAR =  6
	CODE93  =  7
	CODE128 =  8
	CODE11  =  9
	MSI     = 10
	ITF     = 11
	CODABAR = 12

	def printBarcode(self, text, type):

		newDict = { # UPC codes & values for firmwareVersion >= 264
			self.UPC_A   : 65,
			self.UPC_E   : 66,
			self.EAN13   : 67,
			self.EAN8    : 68,
			self.CODE39  : 69,
			self.ITF     : 70,
			self.CODABAR : 71,
			self.CODE93  : 72,
			self.CODE128 : 73,
			self.I25     : -1, # NOT IN NEW FIRMWARE
			self.CODEBAR : -1,
			self.CODE11  : -1,
			self.MSI     : -1
		}
		oldDict = { # UPC codes & values for firmwareVersion < 264
			self.UPC_A   :  0,
			self.UPC_E   :  1,
			self.EAN13   :  2,
			self.EAN8    :  3,
			self.CODE39  :  4,
			self.I25     :  5,
			self.CODEBAR :  6,
			self.CODE93  :  7,
			self.CODE128 :  8,
			self.CODE11  :  9,
			self.MSI     : 10,
			self.ITF     : -1, # NOT IN OLD FIRMWARE
			self.CODABAR : -1
		}

		if self.firmwareVersion >= 264:
			n = newDict[type]
		else:
			n = oldDict[type]
		if n == -1: return
		self.feed(1) # Recent firmware requires this?
		self.writeBytes(
		  29,  72, 2, # Print label below barcode
		  29, 119, 3, # Barcode width
		  29, 107, n) # Barcode type
		self.timeoutWait()
		self.timeoutSet((self.barcodeHeight + 40) * self.dotPrintTime)
		# Print string
		if self.firmwareVersion >= 264:
			# Recent firmware: write length byte + string sans NUL
			n = len(text)
			if n > 255: n = 255
			if self.writeToStdout:
				sys.stdout.write((chr(n)).encode('cp437', 'ignore'))
				for i in range(n):
					sys.stdout.write(text[i].encode('utf-8', 'ignore'))
			else:
				self.uart.write((chr(n)).encode('utf-8', 'ignore'))
				for i in range(n):
					self.uart.write(text[i].encode('utf-8', 'ignore'))
		else:
			# Older firmware: write string + NUL
			if self.writeToStdout:
				sys.stdout.write(text.encode('utf-8', 'ignore'))
			else:
				self.uart.write(text.encode('utf-8', 'ignore'))
		self.prevByte = '\n'

	# === Character commands ===

	INVERSE_MASK       = (1 << 1) # Not in 2.6.8 firmware (see inverseOn())
	UPDOWN_MASK        = (1 << 2)
	BOLD_MASK          = (1 << 3)
	DOUBLE_HEIGHT_MASK = (1 << 4)
	DOUBLE_WIDTH_MASK  = (1 << 5)
	STRIKE_MASK        = (1 << 6)

	def setPrintMode(self, mask):
		self.printMode |= mask
		self.writePrintMode()
		if self.printMode & self.DOUBLE_HEIGHT_MASK:
			self.charHeight = 48
		else:
			self.charHeight = 24
		if self.printMode & self.DOUBLE_WIDTH_MASK:
			self.maxColumn  = 16
		else:
			self.maxColumn  = 32

	def unsetPrintMode(self, mask):
		self.printMode &= ~mask
		self.writePrintMode()
		if self.printMode & self.DOUBLE_HEIGHT_MASK:
			self.charHeight = 48
		else:
			self.charHeight = 24
		if self.printMode & self.DOUBLE_WIDTH_MASK:
			self.maxColumn  = 16
		else:
			self.maxColumn  = 32

	def writePrintMode(self):
		self.writeBytes(27, 33, self.printMode)

	def normal(self):
		self.printMode = 0
		self.writePrintMode()

	def inverseOn(self):
		if self.firmwareVersion >= 268:
			self.writeBytes(29, 66, 1)
		else:
			self.setPrintMode(self.INVERSE_MASK)

	def inverseOff(self):
		if self.firmwareVersion >= 268:
			self.writeBytes(29, 66, 0)
		else:
			self.unsetPrintMode(self.INVERSE_MASK)

	def upsideDownOn(self):
		self.setPrintMode(self.UPDOWN_MASK)

	def upsideDownOff(self):
		self.unsetPrintMode(self.UPDOWN_MASK)

	def doubleHeightOn(self):
		self.setPrintMode(self.DOUBLE_HEIGHT_MASK)

	def doubleHeightOff(self):
		self.unsetPrintMode(self.DOUBLE_HEIGHT_MASK)

	def doubleWidthOn(self):
		self.setPrintMode(self.DOUBLE_WIDTH_MASK)

	def doubleWidthOff(self):
		self.unsetPrintMode(self.DOUBLE_WIDTH_MASK)

	def strikeOn(self):
		self.setPrintMode(self.STRIKE_MASK)

	def strikeOff(self):
		self.unsetPrintMode(self.STRIKE_MASK)

	def boldOn(self):
		self.setPrintMode(self.BOLD_MASK)

	def boldOff(self):
		self.unsetPrintMode(self.BOLD_MASK)

	def justify(self, value):
		c = value.upper()
		if   c == 'C':
			pos = 1
		elif c == 'R':
			pos = 2
		else:
			pos = 0
		self.writeBytes(0x1B, 0x61, pos)

	# Feeds by the specified number of lines
	def feed(self, x=1):
		if self.firmwareVersion >= 264:
			self.writeBytes(27, 100, x)
			self.timeoutSet(self.dotFeedTime * self.charHeight)
			self.prevByte = '\n'
			self.column   =    0

		else:
			# datasheet claims sending bytes 27, 100, <x> works,
			# but it feeds much more than that.  So, manually:
			while x > 0:
				self.write('\n'.encode('cp437', 'ignore'))
				x -= 1

	# Feeds by the specified number of individual pixel rows
	def feedRows(self, rows):
		self.writeBytes(27, 74, rows)
		self.timeoutSet(rows * dotFeedTime)
		self.prevByte = '\n'
		self.column = 0

	def flush(self):
		self.writeBytes(12) # ASCII FF

	def setSize(self, value):
		c = value.upper()
		if c == 'L':   # Large: double width and height
			size            = 0x11
			self.charHeight = 48
			self.maxColumn  = 16
		elif c == 'M': # Medium: double height
			size            = 0x01
			self.charHeight = 48
			self.maxColumn  = 32
		else:          # Small: standard width and height
			size            = 0x00
			self.charHeight = 24
			self.maxColumn  = 32

		self.writeBytes(29, 33, size)
		prevByte = '\n' # Setting the size adds a linefeed

	# Underlines of different weights can be produced:
	# 0 - no underline
	# 1 - normal underline
	# 2 - thick underline
	def underlineOn(self, weight=1):
		if weight > 2: weight = 2
		self.writeBytes(27, 45, weight)

	def underlineOff(self):
		self.writeBytes(27, 45, 0)

	def printBitmap(self, w, h, bitmap, LaaT=False):
		rowBytes = math.floor((w + 7) / 8)  # Round up to next byte boundary
		if rowBytes >= 48:
			rowBytesClipped = 48  # 384 pixels max width
		else:
			rowBytesClipped = rowBytes

		# if LaaT (line-at-a-time) is True, print bitmaps
		# scanline-at-a-time (rather than in chunks).
		# This tends to make for much cleaner printing
		# (no feed gaps) on large images...but has the
		# opposite effect on small images that would fit
		# in a single 'chunk', so use carefully!
		if LaaT: maxChunkHeight = 1
		else:    maxChunkHeight = 255

		i = 0
		for rowStart in range(0, h, maxChunkHeight):
			chunkHeight = h - rowStart
			if chunkHeight > maxChunkHeight:
				chunkHeight = maxChunkHeight

			# Timeout wait happens here
			self.writeBytes(18, 42, chunkHeight, rowBytesClipped)

			for y in range(chunkHeight):
				for x in range(rowBytesClipped):
					if self.writeToStdout:
						sys.stdout.write(bytes([bitmap[i]]))
					else:
						self.uart.write(bytes([bitmap[i]]))
					i += 1
				i += rowBytes - rowBytesClipped
			self.timeoutSet(chunkHeight * self.dotPrintTime)

		self.prevByte = '\n'

	# Print Image.  Requires Python Imaging Library.  This is
	# specific to the Python port and not present in the Arduino
	# library.  Image will be cropped to 384 pixels width if
	# necessary, and converted to 1-bit w/diffusion dithering.
	# For any other behavior (scale, B&W threshold, etc.), use
	# the Imaging Library to perform such operations before
	# passing the result to this function.
	def printImage(self, image_file, LaaT=False):
		from PIL import Image
		image = Image.open(image_file)
		if image.mode != '1':
			image = image.convert('1')

		width  = image.size[0]
		height = image.size[1]
		if width > 384:
			width = 384
		rowBytes = math.floor((width + 7) / 8)
		bitmap   = bytearray(rowBytes * height)
		pixels   = image.load()

		for y in range(height):
			n = y * rowBytes
			x = 0
			for b in range(rowBytes):
				sum = 0
				bit = 128
				while bit > 0:
					if x >= width: break
					if pixels[x, y] == 0:
						sum |= bit
					x    += 1
					bit >>= 1
				bitmap[n + b] = sum

		self.printBitmap(width, height, bitmap, LaaT)

	# Take the printer offline. Print commands sent after this
	# will be ignored until 'online' is called.
	def offline(self):
		self.writeBytes(27, 61, 0)

	# Take the printer online. Subsequent print commands will be obeyed.
	def online(self):
		self.writeBytes(27, 61, 1)

	# Put the printer into a low-energy state immediately.
	def sleep(self):
		self.sleepAfter(1) # Can't be 0, that means "don't sleep"

	# Put the printer into a low-energy state after
	# the given number of seconds.
	def sleepAfter(self, seconds):
		if self.firmwareVersion >= 264:
			self.writeBytes(27, 56, seconds & 0xFF, seconds >> 8)
		else:
			self.writeBytes(27, 56, seconds)

	def wake(self):
		self.timeoutSet(0)
		self.writeBytes(255)
		if self.firmwareVersion >= 264:
			time.sleep(0.05)            # 50 ms
			self.writeBytes(27, 118, 0) # Sleep off (important!)
		else:
			for i in range(10):
				self.writeBytes(27)
				self.timeoutSet(0.1)

	# Empty method, included for compatibility
	# with existing code ported from Arduino.
	def listen(self):
		pass

	# Check the status of the paper using the printers self reporting
	# ability. Doesn't match the datasheet...
	# Returns True for paper, False for no paper.
	def hasPaper(self):
		if self.firmwareVersion >= 264:
			self.writeBytes(27, 118, 0)
		else:
			self.writeBytes(29, 114, 0)
		# Bit 2 of response seems to be paper status
		stat = ord(self.uart.read(1)) & 0b00000100
		# If set, we have paper; if clear, no paper
		return stat == 0

	def setLineHeight(self, val=32):
		if val < 24: val = 24
		self.lineSpacing = val - 24

		# The printer doesn't take into account the current text
		# height when setting line height, making this more akin
		# to inter-line spacing.  Default line spacing is 32
		# (char height of 24, line spacing of 8).
		self.writeBytes(27, 51, val)

	CHARSET_USA          =  0
	CHARSET_FRANCE       =  1
	CHARSET_GERMANY      =  2
	CHARSET_UK           =  3
	CHARSET_DENMARK1     =  4
	CHARSET_SWEDEN       =  5
	CHARSET_ITALY        =  6
	CHARSET_SPAIN1       =  7
	CHARSET_JAPAN        =  8
	CHARSET_NORWAY       =  9
	CHARSET_DENMARK2     = 10
	CHARSET_SPAIN2       = 11
	CHARSET_LATINAMERICA = 12
	CHARSET_KOREA        = 13
	CHARSET_SLOVENIA     = 14
	CHARSET_CROATIA      = 14
	CHARSET_CHINA        = 15

	# Alters some chars in ASCII 0x23-0x7E range; see datasheet
	def setCharset(self, val=0):
		if val > 15: val = 15
		self.writeBytes(27, 82, val)

	CODEPAGE_CP437       =  0 # USA, Standard Europe
	CODEPAGE_KATAKANA    =  1
	CODEPAGE_CP850       =  2 # Multilingual
	CODEPAGE_CP860       =  3 # Portuguese
	CODEPAGE_CP863       =  4 # Canadian-French
	CODEPAGE_CP865       =  5 # Nordic
	CODEPAGE_WCP1251     =  6 # Cyrillic
	CODEPAGE_CP866       =  7 # Cyrillic #2
	CODEPAGE_MIK         =  8 # Cyrillic/Bulgarian
	CODEPAGE_CP755       =  9 # East Europe, Latvian 2
	CODEPAGE_IRAN        = 10
	CODEPAGE_CP862       = 15 # Hebrew
	CODEPAGE_WCP1252     = 16 # Latin 1
	CODEPAGE_WCP1253     = 17 # Greek
	CODEPAGE_CP852       = 18 # Latin 2
	CODEPAGE_CP858       = 19 # Multilingual Latin 1 + Euro
	CODEPAGE_IRAN2       = 20
	CODEPAGE_LATVIAN     = 21
	CODEPAGE_CP864       = 22 # Arabic
	CODEPAGE_ISO_8859_1  = 23 # West Europe
	CODEPAGE_CP737       = 24 # Greek
	CODEPAGE_WCP1257     = 25 # Baltic
	CODEPAGE_THAI        = 26
	CODEPAGE_CP720       = 27 # Arabic
	CODEPAGE_CP855       = 28
	CODEPAGE_CP857       = 29 # Turkish
	CODEPAGE_WCP1250     = 30 # Central Europe
	CODEPAGE_CP775       = 31
	CODEPAGE_WCP1254     = 32 # Turkish
	CODEPAGE_WCP1255     = 33 # Hebrew
	CODEPAGE_WCP1256     = 34 # Arabic
	CODEPAGE_WCP1258     = 35 # Vietnam
	CODEPAGE_ISO_8859_2  = 36 # Latin 2
	CODEPAGE_ISO_8859_3  = 37 # Latin 3
	CODEPAGE_ISO_8859_4  = 38 # Baltic
	CODEPAGE_ISO_8859_5  = 39 # Cyrillic
	CODEPAGE_ISO_8859_6  = 40 # Arabic
	CODEPAGE_ISO_8859_7  = 41 # Greek
	CODEPAGE_ISO_8859_8  = 42 # Hebrew
	CODEPAGE_ISO_8859_9  = 43 # Turkish
	CODEPAGE_ISO_8859_15 = 44 # Latin 3
	CODEPAGE_THAI2       = 45
	CODEPAGE_CP856       = 46
	CODEPAGE_CP874       = 47

	# Selects alt symbols for 'upper' ASCII values 0x80-0xFF
	def setCodePage(self, val=0):
		if val > 47: val = 47
		self.writeBytes(27, 116, val)

	# Copied from Arduino lib for parity; may not work on all printers
	def tab(self):
		self.writeBytes(9)
		self.column = (self.column + 4) & 0xFC

	# Copied from Arduino lib for parity; may not work on all printers
	def setCharSpacing(self, spacing):
		self.writeBytes(27, 32, spacing)

	# Overloading print() in Python pre-3.0 is dirty pool,
	# but these are here to provide more direct compatibility
	# with existing code written for the Arduino library.
	def print(self, *args, **kwargs):
		for arg in args:
			self.uart.write((str(arg)).encode('cp437', 'ignore'))

	# For Arduino code compatibility again
	def println(self, *args, **kwargs):
		for arg in args:
			self.uart.write((str(arg)).encode('cp437', 'ignore'))
		self.uart.write('\n'.encode('cp437', 'ignore'))
