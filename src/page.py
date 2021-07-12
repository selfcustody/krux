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
import time
import lcd
from embit.wordlists.ubip39 import WORDLIST
from input import BUTTON_ENTER, BUTTON_PAGE
from display import DEFAULT_PADDING, MAX_BACKLIGHT, MIN_BACKLIGHT

QR_ANIMATION_INTERVAL_MS = const(500)

class Page:
	def __init__(self, ctx):
		self.ctx = ctx
		
	# Convenience methods below used by multiple Page subclasses
	# that require both display AND input/camera
	def capture_digits_from_numpad(self, title):
		digits = ''
		selected_key = 0
		while True:
			lcd.clear()
			self.ctx.display.draw_hcentered_text(title)
			self.ctx.display.draw_numpad(selected_key, digits, mask_digits=False, offset_y=60)

			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				if selected_key == 11: # Enter
					break
				elif selected_key == 10: # Del
					digits = digits[:len(digits)-1]
				else:
					digits += str(selected_key)
			elif btn == BUTTON_PAGE:
				selected_key = (selected_key + 1) % 12
		return digits
  
	def capture_letters_from_keypad(self, title):
		letters = ''
		selected_key = 0
		while True:
			lcd.clear()
	
			self.ctx.display.draw_hcentered_text(title)
			self.ctx.display.draw_keypad(selected_key, letters, mask_letters=False, offset_y=50)

			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				changed = False
				if selected_key == 27: # Enter
					break
				elif selected_key == 26: # Del
					letters = letters[:len(letters)-1]
					changed = True
				else:
					letters += chr(ord('a') + selected_key)
					changed = True
				if changed and len(letters) > 2:
					matching_words = list(filter(lambda word: word.startswith(letters), WORDLIST))
					if len(matching_words) == 1:
						letters = matching_words[0]
						selected_key = 27
			elif btn == BUTTON_PAGE:
				selected_key = (selected_key + 1) % 28
		return letters

	def capture_qr_code(self):
		self._enter_state = -1
		self._page_state = -1
		def callback(part_total, num_parts_captured, new_part):
			# Turn on the light as long as the enter button is held down
			if self._enter_state == -1:
				self._enter_state = self.ctx.input.enter.value()
			elif self.ctx.input.enter.value() != self._enter_state:
	   			self._enter_state = self.ctx.input.enter.value()
				self.ctx.light.toggle()
			
			# Exit the capture loop if the page button is pressed
			if self._page_state == -1:
				self._page_state = self.ctx.input.page.value()
			elif self.ctx.input.page.value() != self._page_state:
				return True

			# Indicate progress to the user that a new part was captured
			if new_part:
				self.ctx.display.to_portrait()
				self.ctx.display.draw_centered_text(str(num_parts_captured) + ' / ' + str(part_total))
				time.sleep_ms(1000)
				self.ctx.display.to_landscape()
	
			return False
	
		self.ctx.display.to_landscape()
		code = None
		try:
			code = self.ctx.camera.capture_qr_code_loop(callback)
		except Exception as e:
			print(e)
			pass
		self.ctx.light.turn_off()
		self.ctx.display.to_portrait()
		return code
	
	def display_qr_codes(self, qr_codes, title=None, manual=False):
		self.ctx.display.set_backlight(MIN_BACKLIGHT)
		done = False
		i = 0
		while not done:
			lcd.clear()
			self.ctx.display.draw_qr_code(DEFAULT_PADDING, qr_codes[i])
			if title is not None:
				self.ctx.display.draw_hcentered_text(title, offset_y=140)
			else:
				self.ctx.display.draw_hcentered_text('Part ' + str(i+1) + ' / ' + str(len(qr_codes)), offset_y=175)
			i = (i + 1) % len(qr_codes)
			btn = self.ctx.input.wait_for_button(block=manual)
			done = btn == BUTTON_ENTER
			if not done:
				time.sleep_ms(QR_ANIMATION_INTERVAL_MS)
		self.ctx.display.set_backlight(MAX_BACKLIGHT)
  
	def display_recovery_phrase(self, words):
		lcd.clear()
		self.ctx.display.draw_hcentered_text('Recovery Phrase')
		word_list = [str(i+1) + '.' + ('  ' if i + 1 < 10 else ' ') + word for i, word in enumerate(words)]
		for i, word in enumerate(word_list):
			lcd.draw_string(DEFAULT_PADDING, 35 + (i * self.ctx.display.line_height()), word, lcd.WHITE, lcd.BLACK)

	def run(self):
		raise ValueError('Not implemented')