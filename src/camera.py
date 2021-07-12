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
import gc
import sensor
import lcd
from qr import join_qr_parts, parse_qr_part

class Camera:
	def __init__(self):
		self.initialize_sensor()
		
	def initialize_sensor(self):
		sensor.reset()
		sensor.set_pixformat(sensor.GRAYSCALE)
		sensor.set_framesize(sensor.QVGA)
		sensor.skip_frames()

	def capture_qr_code_loop(self, callback):
		""" QR codes can become too large to display and must be animated as
			several codes in sequence.
			This function parses the code contents and looks for part numbers,
			adding them to a dict by their part number until all parts are loaded.
			The part data are then assembled into one and returned.
   		"""
		self.initialize_sensor()
		sensor.run(1)
		
		qr_parts_dict = {}
		qr_part_total = -1
		qr_part_index_sum = -1
		
		new_part = False
		while True:
			stop = callback(qr_part_total, len(qr_parts_dict), new_part)
			if stop:
				sensor.run(0)
				return None
			
			new_part = False

			img = sensor.snapshot()
			gc.collect()
			hist = img.get_histogram()
			if str(type(hist)) != "<class 'histogram'>":
				continue
			# Convert the image to black and white by using Otsu's thresholding.
			# This is done to account for spots, blotches, and streaks in the code
			# that may cause issues for the decoder.
			img.binary([(0, hist.get_threshold().value())], invert=True)
			lcd.display(img)
 
 			res = img.find_qrcodes()
			if len(res) > 0:
				data = res[0].payload()
				_, part_index, part_total = parse_qr_part(data)
				if qr_part_total == -1:
					qr_part_total = part_total
					qr_part_index_sum = sum(range(1, part_total+1))
					
				prev_qr_parts_len = len(qr_parts_dict)
				qr_parts_dict[part_index] = data
				if prev_qr_parts_len < len(qr_parts_dict):
					new_part = True
					
			if len(qr_parts_dict) == qr_part_total and sum(qr_parts_dict.keys()) == qr_part_index_sum:
				break
			
		sensor.run(0)
		return join_qr_parts([part for _, part in sorted(qr_parts_dict.items())])
	