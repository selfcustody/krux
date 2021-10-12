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
import lcd
from embit.networks import NETWORKS
from embit.wordlists.bip39 import WORDLIST
from page import Page
from menu import Menu, MENU_CONTINUE, MENU_EXIT
from input import BUTTON_ENTER, BUTTON_PAGE
from qr import FORMAT_UR
from wallet import Wallet, pick_final_word
import urtypes

class Login(Page):
	def __init__(self, ctx):
		Page.__init__(self, ctx)
		self.menu = Menu(ctx, [
			('Load Mnemonic', self.open_wallet),
			('About', self.about),
			('Shutdown', self.shutdown),
		])

	def open_wallet(self):
		submenu = Menu(self.ctx, [
			('Via QR Code', self.open_wallet_with_qr_code),
			('Via Text', self.open_wallet_with_text),
			('Via Numbers', self.open_wallet_with_digits),
			('Via Bits', self.open_wallet_with_bits),
			('Cancel', lambda: MENU_EXIT)
		])
		index, status = submenu.run_loop()
		if index == len(submenu.menu)-1:
			return MENU_CONTINUE
		return status
  
	def open_wallet_with_words(self, words):
		self.display_mnemonic(words)
		self.ctx.display.draw_hcentered_text('Continue?', offset_y=220)
		btn = self.ctx.input.wait_for_button()
		if btn == BUTTON_ENTER:
			self.ctx.display.flash_text('Loading..')
			self.ctx.wallet = Wallet(' '.join(words), network=NETWORKS[self.ctx.net])
			return MENU_EXIT
		return MENU_CONTINUE

	def open_wallet_with_qr_code(self):
		data, qr_format = self.capture_qr_code()
		if data is None:
			self.ctx.display.flash_text('Failed to load mnemonic', lcd.RED)
			return MENU_CONTINUE

		words = []
		if qr_format == FORMAT_UR:
			try:
				words = urtypes.crypto.BIP39.from_cbor(data.cbor).words
			except:
				words = urtypes.Bytes.from_cbor(data.cbor).data.decode().split(' ')
		else:
			if ' ' in data:
				words = data.split(' ')
			elif len(data) == 48 or len(data) == 96:
				for i in range(0, len(data), 4):
					words.append(WORDLIST[int(data[i:i+4])])

		if not words or (len(words) != 12 and len(words) != 24):
			self.ctx.display.flash_text('Invalid mnemonic\nlength', lcd.RED)
			return MENU_CONTINUE
		return self.open_wallet_with_words(words)

	def open_wallet_with_text(self):
		words = []
		self.ctx.display.draw_hcentered_text('Enter each\nword of your\nBIP-39 mnemonic.')
		self.ctx.display.draw_hcentered_text('Proceed?', offset_y=200)
		btn = self.ctx.input.wait_for_button()
		if btn == BUTTON_ENTER:
			for i in range(24):
				if i == 12:
					lcd.clear()
					self.ctx.display.draw_centered_text('Done?')
					btn = self.ctx.input.wait_for_button()
					if btn == BUTTON_ENTER:
						break
  
				word = ''
				while True:
					word = self.capture_letters_from_keypad('Word ' + str(i+1))
					if word in WORDLIST:
						break
					# If the first 'word' is 11 a's in a row, we're testing and just want the test words
					if i == 0 and word == 'a' * 11:
						break
					# If the last 'word' is xyz, pick a random final word that is a valid checksum
					if (i == 11 or i == 23) and word == 'xyz':
						break
  
				if word == 'a' * 11:
					words = [WORDLIST[0] if n + 1 < 12 else WORDLIST[1879] for n in range(12)]
					break
 
				if word == 'xyz':
					word = pick_final_word(words)
	 	
				lcd.clear()
				self.ctx.display.draw_centered_text(word)
				self.ctx.input.wait_for_button()
				
				words.append(word)

			return self.open_wallet_with_words(words)
		
		return MENU_CONTINUE
	
	def open_wallet_with_digits(self):
		words = []
		self.ctx.display.draw_hcentered_text('Enter each\nword of your\nBIP-39 mnemonic\nas a number from\n1 to 2048.')
		self.ctx.display.draw_hcentered_text('Proceed?', offset_y=200)
		btn = self.ctx.input.wait_for_button()
		if btn == BUTTON_ENTER:
			for i in range(24):
				if i == 12:
					lcd.clear()
					self.ctx.display.draw_centered_text('Done?')
					btn = self.ctx.input.wait_for_button()
					if btn == BUTTON_ENTER:
						break
  
				digits = ''
				while True:
					digits = self.capture_digits_from_numpad('Word ' + str(i+1))
					if int(digits) >= 1 and int(digits) <= 2048:
						break
					# If the first 'word' is 11 1's in a row, we're testing and just want the test words
					if i == 0 and digits == '1' * 11:
						break
					# If the last 'word' is 11 9's in a row, pick a random final word that is a valid checksum
					if (i == 11 or i == 23) and digits == '9' * 11:
						break
  
				if digits == '1' * 11:
					words = [WORDLIST[0] if n + 1 < 12 else WORDLIST[1879] for n in range(12)]
					break
 
				word = ''
				if digits == '9' * 11:
					word = pick_final_word(words)
				else:
					word = WORDLIST[int(digits)-1]
	
				lcd.clear()
				self.ctx.display.draw_centered_text(word)
				self.ctx.input.wait_for_button()
	
				words.append(word)
	
			return self.open_wallet_with_words(words)
		
		return MENU_CONTINUE

	def open_wallet_with_bits(self):
		words = []
		self.ctx.display.draw_hcentered_text('Enter each\nword of your\nBIP-39 mnemonic\nas a series of\nbinary digits.')
		self.ctx.display.draw_hcentered_text('Proceed?', offset_y=200)
		btn = self.ctx.input.wait_for_button()
		if btn == BUTTON_ENTER:
			for i in range(24):
				if i == 12:
					lcd.clear()
					self.ctx.display.draw_centered_text('Done?')
					btn = self.ctx.input.wait_for_button()
					if btn == BUTTON_ENTER:
						break
  
				bits = ''
				while True:
					bits = self.capture_bits_from_numpad('Word ' + str(i+1))
					if len(bits) == 11:
						break
 
				word = WORDLIST[int('0b' + bits, 0)]
	
				lcd.clear()
				self.ctx.display.draw_centered_text(word)
				self.ctx.input.wait_for_button()
	
				words.append(word)
	
			return self.open_wallet_with_words(words)
		
		return MENU_CONTINUE

	def about(self):
		networks = list(NETWORKS.keys())

		while True:
			lcd.clear()
			self.ctx.display.draw_centered_text('Krux\n\n\nVersion\n%s\n\nNetwork\n%snet' % (self.ctx.version, self.ctx.net))

			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_PAGE:
				for i, network in enumerate(networks):
					if self.ctx.net == network:
						self.ctx.net = networks[(i + 1) % len(networks)]
						break
			elif btn == BUTTON_ENTER:
				break
		return MENU_CONTINUE
