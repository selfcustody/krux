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
from embit.wordlists.ubip39 import WORDLIST
from page import Page
from menu import Menu, MENU_CONTINUE, MENU_EXIT
from input import BUTTON_ENTER, BUTTON_PAGE
from wallet import Wallet, pick_final_word

class Login(Page):
	def __init__(self, ctx):
		Page.__init__(self, ctx)
		self.menu = Menu(ctx, [
			('Open Wallet\n(QR)', self.open_wallet_with_qr_code),
			('Open Wallet\n(Text)', self.open_wallet_with_text),
			('Open Wallet\n(Numeric)', self.open_wallet_with_digits),
			('About', self.about),
			('Shutdown', self.shutdown),
		])

	def open_wallet_with_words(self, words):
		self.display_recovery_phrase(words)
		self.ctx.display.draw_hcentered_text('Open?', offset_y=220)
		btn = self.ctx.input.wait_for_button()
		if btn == BUTTON_ENTER:
			self.ctx.display.flash_text('Opening wallet..')
			self.ctx.wallet = Wallet(' '.join(words), network=NETWORKS[self.ctx.net])
			return MENU_EXIT
		return MENU_CONTINUE

	def open_wallet_with_qr_code(self):
		mnemonic = self.capture_qr_code()
		if not mnemonic:
			self.ctx.display.flash_text('Invalid wallet', lcd.RED)
			return MENU_CONTINUE

		words = mnemonic.split(' ')
		if not words or len(words) != 12:
			self.ctx.display.flash_text('Invalid wallet', lcd.RED)
			return MENU_CONTINUE
		return self.open_wallet_with_words(words)

	def open_wallet_with_text(self):
		words = []
		self.ctx.display.draw_hcentered_text('Enter each word of your 12-word BIP-39 recovery phrase.')
		self.ctx.display.draw_hcentered_text('Proceed?', offset_y=200)
		btn = self.ctx.input.wait_for_button()
		if btn == BUTTON_ENTER:
			for i in range(12):
				word = ''
				while True:
					word = self.capture_letters_from_keypad('Word ' + str(i+1))
					if word in WORDLIST:
						break
					# If the first 'word' is 11 a's in a row, we're testing and just want the test words
					if i == 0 and word == 'a' * 11:
						break
					# If the last 'word' is xyz, pick a random final word that is a valid checksum
					if i == 11 and word == 'xyz':
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
		self.ctx.display.draw_hcentered_text('Enter each word of your 12-word BIP-39 recovery phrase as a number from 1 to 2048.')
		self.ctx.display.draw_hcentered_text('Proceed?', offset_y=200)
		btn = self.ctx.input.wait_for_button()
		if btn == BUTTON_ENTER:
			for i in range(12):
				digits = ''
				while True:
					digits = self.capture_digits_from_numpad('Word ' + str(i+1))
					if int(digits) >= 1 and int(digits) <= 2048:
						break
					# If the first 'word' is 11 1's in a row, we're testing and just want the test words
					if i == 0 and digits == '1' * 11:
						break
					# If the last 'word' is 11 9's in a row, pick a random final word that is a valid checksum
					if i == 11 and digits == '9' * 11:
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
