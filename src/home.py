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
	import ujson as json
except ImportError:
	import json
import time
import gc
from embit.networks import NETWORKS
import lcd
from embit.psbt import PSBT
from multisig import MultisigPolicy
from printer import MAX_PRINT_WIDTH
from qr import QR_FORMAT_NONE, to_pmofn_qr_codes, to_qr_codes
from wallet import get_tx_output_amount_messages, get_tx_policy, is_multisig
from page import Page
from menu import Menu, MENU_CONTINUE, MENU_EXIT
from input import BUTTON_ENTER

MAX_ADDRESS_DEPTH = const(200)

class Home(Page):
	def __init__(self, ctx):
		Page.__init__(self, ctx)
		self.menu = Menu(ctx, [
			('Recovery\nPhrase', self.recovery_phrase),
			('Public Key\n(xpub)', self.public_key),
			('Multisig\nPolicy', self.multisig_policy),
			('Check\nAddress', self.check_address),
			('Sign PSBT', self.sign_psbt),
			('Close Wallet', self.close_wallet)
		])
	 
	def run(self):
		self.menu.run_loop()
		return False
	
	def recovery_phrase(self):  
		words = self.ctx.wallet.mnemonic.split(' ')
		self.display_recovery_phrase(words)
		self.ctx.input.wait_for_button()
		if self.ctx.printer.is_connected():
			lcd.clear()
			time.sleep_ms(1000)
			self.ctx.display.draw_centered_text('Print to QR?')
			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				self.ctx.display.flash_text('Printing recovery phrase QR..')
				qr_code = to_qr_codes(self.ctx.wallet.mnemonic, format=QR_FORMAT_NONE)[0]
				self.ctx.printer.print_qr_code(qr_code, padding=32)
		return MENU_CONTINUE

	def public_key(self):  
		self.display_qr_codes(to_qr_codes(self.ctx.wallet.xpub_btc_core()), title=self.ctx.wallet.xpub())
		if self.ctx.printer.is_connected():
			lcd.clear()
			time.sleep_ms(1000)
			self.ctx.display.draw_centered_text('Print to QR?')
			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				self.ctx.display.flash_text('Printing xpub QR..')
				qr_code = to_qr_codes(self.ctx.wallet.xpub_btc_core(), format=QR_FORMAT_NONE)[0]
				self.ctx.printer.print_qr_code(qr_code, padding=32)
		return MENU_CONTINUE
	
 	def multisig_policy(self):
		if not self.ctx.multisig_policy:
			self.ctx.display.draw_centered_text('There is no multisig policy to display.')
			self.ctx.display.draw_hcentered_text('Load one?', offset_y=200)
			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				return self.load_multisig()
		else:
			self.display_multisig(self.ctx.multisig_policy)
			if self.ctx.printer.is_connected():
				lcd.clear()
				time.sleep_ms(1000)
				self.ctx.display.draw_centered_text('Print to QR?')
				btn = self.ctx.input.wait_for_button()
				if btn == BUTTON_ENTER:   
					self.ctx.display.flash_text('Printing multisig policy QR..')
					for qr_code in to_pmofn_qr_codes(json.dumps(self.ctx.multisig_policy.policy), min_part_size=MAX_PRINT_WIDTH // 2 - 10):
						self.ctx.printer.print_qr_code(qr_code, padding=32)
		return MENU_CONTINUE

	def load_multisig(self):		
		multisig_policy_json = self.capture_qr_code()
		if not multisig_policy_json:
			self.ctx.display.flash_text('Failed to load multisig policy', lcd.RED)
			return MENU_CONTINUE

		try:
			multisig_policy = MultisigPolicy(json.loads(multisig_policy_json))
			if self.ctx.wallet.xpub() not in multisig_policy.cosigners:
				raise ValueError('xpub not a cosigner')

			self.display_multisig(multisig_policy, include_label=False)
			self.ctx.display.draw_hcentered_text('Load?', offset_y=220)
			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				self.ctx.multisig_policy = multisig_policy
				self.ctx.display.flash_text('Loaded multisig')
				return MENU_CONTINUE
		except Exception as e:
			print(e)
			self.ctx.display.flash_text('Invalid multisig policy - ' + str(e), lcd.RED)
			return MENU_CONTINUE
	
	def check_address(self, max_depth=MAX_ADDRESS_DEPTH):
		if not self.ctx.multisig_policy:
			self.ctx.display.flash_text('Multisig policy not found', lcd.RED)
			return MENU_CONTINUE

		data = self.capture_qr_code()
		if not data:
			return MENU_CONTINUE

		if data.startswith('bitcoin:'):
			data = data[8:]
   
		gc.collect()
  
		found = False
		for i in range(max_depth):
			lcd.clear()
			self.ctx.display.draw_centered_text('Checking\nreceive address\n' + str(i + 1) + '\nfor match...')
			if data == self.ctx.multisig_policy.descriptor.derive(i, branch_index=0).address(network=NETWORKS[self.ctx.net]):
				found = True
				break

		gc.collect()
  
		lcd.clear()
		if found:
			self.ctx.display.draw_centered_text(data + '\n\nis a valid\nreceive address', lcd.GREEN)
		else:
			self.ctx.display.draw_centered_text(data + '\n\nWAS NOT found\nin the first\n' + str(max_depth) + '\nreceive addresses', lcd.RED)
									   
		self.ctx.input.wait_for_button()

		return MENU_CONTINUE

	def sign_psbt(self):
		if not self.ctx.multisig_policy:
			self.ctx.display.flash_text('Multisig policy not found', lcd.RED)
			return MENU_CONTINUE
		
		data = self.capture_qr_code()
		if not data:
			return MENU_CONTINUE
	
		tx = PSBT.from_base64(data)
		policy = get_tx_policy(tx)

		if not is_multisig(policy):
			self.ctx.display.flash_text('Invalid PSBT - not a multisig transaction', lcd.RED)
			return MENU_CONTINUE

		if not self.ctx.multisig_policy.matches_tx_policy(policy):
			self.ctx.display.flash_text('Invalid PSBT - policy mismatch', lcd.RED)
			return MENU_CONTINUE
	
		outputs = get_tx_output_amount_messages(tx, network=self.ctx.net)
		self.ctx.display.draw_hcentered_text('\n\n'.join(outputs))
		self.ctx.display.draw_hcentered_text('Sign?', offset_y=200)
	
		btn = self.ctx.input.wait_for_button()
		if btn == BUTTON_ENTER:
			tx.sign_with(self.ctx.wallet.root)
			signed_psbt = tx.to_base64()
			self.display_qr_codes(to_qr_codes(signed_psbt), None, manual=True)
			if self.ctx.printer.is_connected():
				lcd.clear()
				time.sleep_ms(1000)
				self.ctx.display.draw_centered_text('Print to QRs?')
				btn = self.ctx.input.wait_for_button()
				if btn == BUTTON_ENTER:
					self.ctx.display.flash_text('Printing signed PSBT QRs..')
					for qr_code in to_pmofn_qr_codes(signed_psbt, min_part_size=MAX_PRINT_WIDTH // 2 - 10):
						self.ctx.printer.print_qr_code(qr_code, padding=32)
		return MENU_CONTINUE

	def close_wallet(self):
		self.ctx.wallet = None
		self.ctx.multisig_policy = None
		self.ctx.printer.clear()
		gc.collect()
		return MENU_EXIT

	def display_multisig(self, multisig_policy, include_label=True):
		about = (multisig_policy.label + '\n') if include_label else ''
		xpubs = []
		for i, xpub in enumerate(multisig_policy.cosigners):
			xpubs.append(str(i+1) + '. ' + xpub[4:8] + '...' + xpub[len(xpub)-4:len(xpub)])
		about += '\n'.join(xpubs)
		self.display_qr_codes(to_qr_codes(json.dumps(multisig_policy.policy)), about)
