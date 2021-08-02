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
from display import DEFAULT_PADDING
from embit import psbt
from embit.networks import NETWORKS
import lcd
from embit.psbt import PSBT
from multisig import MultisigPolicy
from qr import to_qr_codes
from wallet import get_tx_output_amount_messages, get_tx_policy, is_multisig
from page import Page
from menu import Menu, MENU_CONTINUE
from input import BUTTON_ENTER, BUTTON_PAGE

class Home(Page):
	def __init__(self, ctx):
		Page.__init__(self, ctx)
		self.menu = Menu(ctx, [
			('Recovery\nPhrase', self.recovery_phrase),
			('Public Key\n(xpub)', self.public_key),
			('Multisig\nPolicy', self.multisig_policy),
			('Check\nAddress', self.check_address),
			('Sign PSBT', self.sign_psbt),
			('Shutdown', self.shutdown)
		])
	
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
				qr_code, _ = to_qr_codes(self.ctx.wallet.mnemonic, max_width=self.ctx.printer.qr_data_width()).__next__()
				self.ctx.printer.print_qr_code(qr_code)
		return MENU_CONTINUE

	def public_key(self):  
		self.display_qr_codes(self.ctx.wallet.xpub_btc_core(), self.ctx.display.qr_data_width(), title=self.ctx.wallet.xpub())
		if self.ctx.printer.is_connected():
			lcd.clear()
			time.sleep_ms(1000)
			self.ctx.display.draw_centered_text('Print to QR?')
			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				self.ctx.display.flash_text('Printing xpub QR..')
				qr_code, _ = to_qr_codes(self.ctx.wallet.xpub_btc_core(), max_width=self.ctx.printer.qr_data_width()).__next__()
				self.ctx.printer.print_qr_code(qr_code)
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
					payload = json.dumps(self.ctx.multisig_policy.policy)
					for qr_code, _ in to_qr_codes(payload, max_width=self.ctx.printer.qr_data_width()):
						self.ctx.printer.print_qr_code(qr_code)
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

			self.display_multisig(multisig_policy, include_qr=False)
			self.ctx.display.draw_hcentered_text('Load?', offset_y=200)
			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				self.ctx.multisig_policy = multisig_policy
				self.ctx.display.flash_text('Loaded multisig')
				return MENU_CONTINUE
		except Exception as e:
			print(e)
			self.ctx.display.flash_text('Invalid multisig policy - ' + str(e), lcd.RED)
			return MENU_CONTINUE
	
	def check_address(self):
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
		i = 0
		while True:
			if (i + 1) % 100 == 0:
				lcd.clear()
				self.ctx.display.draw_centered_text('Checked\n%d receive\naddresses with\nno matches.' % (i + 1))
				self.ctx.display.draw_hcentered_text('Try more?', offset_y=200)
				btn = self.ctx.input.wait_for_button()
				if btn != BUTTON_ENTER:
					break
 
			lcd.clear()
			self.ctx.display.draw_centered_text('Checking\nreceive address\n' + str(i + 1) + '\nfor match...')
   
			if data == self.ctx.multisig_policy.descriptor.derive(i, branch_index=0).address(network=NETWORKS[self.ctx.net]):
				found = True
				break
			i += 1

		gc.collect()
  
		lcd.clear()
		if found:
			self.ctx.display.draw_centered_text(data + '\n\nis a valid\nreceive address', lcd.GREEN)
		else:
			self.ctx.display.draw_centered_text(data + '\n\nwas\nNOT FOUND\nin the first\n' + str(i + 1) + ' receive\naddresses', lcd.RED)
									   
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
			trimmed_psbt = psbt.PSBT(tx.tx)
			for i, inp in enumerate(tx.inputs):
				trimmed_psbt.inputs[i].partial_sigs = inp.partial_sigs
			signed_psbt = trimmed_psbt.to_base64()
			trimmed_psbt = None
			tx = None
			gc.collect()
			self.display_qr_codes(signed_psbt, self.ctx.display.qr_data_width(), title=None, manual=True)
			if self.ctx.printer.is_connected():
				lcd.clear()
				time.sleep_ms(1000)
				self.ctx.display.draw_centered_text('Print to QRs?')
				btn = self.ctx.input.wait_for_button()
				if btn == BUTTON_ENTER:
					self.ctx.display.flash_text('Printing signed PSBT QRs..')
					for qr_code, _ in to_qr_codes(signed_psbt, max_width=self.ctx.printer.qr_data_width()):
						self.ctx.printer.print_qr_code(qr_code)
		return MENU_CONTINUE

	def display_multisig(self, multisig_policy, include_qr=True):
		about = multisig_policy.label + '\n'
		xpubs = []
		for i, xpub in enumerate(multisig_policy.cosigners):
			xpubs.append(str(i+1) + '. ' + xpub[4:8] + '...' + xpub[len(xpub)-4:len(xpub)])
		about += '\n'.join(xpubs)
		if include_qr:
			self.display_qr_codes(json.dumps(multisig_policy.policy), self.ctx.display.qr_data_width(), title=about)
		else:
	  		self.ctx.display.draw_hcentered_text(about, offset_y=DEFAULT_PADDING)
