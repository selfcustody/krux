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
from embit.descriptor.arguments import Key, KeyHash
import time
import gc
from display import DEFAULT_PADDING
from embit.networks import NETWORKS
import lcd
from multisig import MultisigWallet, PSBTSigner
from qr import FORMAT_NONE, FORMAT_UR, to_qr_codes
from page import Page
from menu import MENU_EXIT, Menu, MENU_CONTINUE
from input import BUTTON_ENTER, BUTTON_PAGE

class Home(Page):
	def __init__(self, ctx):
		Page.__init__(self, ctx)
		self.menu = Menu(ctx, [
			('Mnemonic', self.mnemonic),
			('Public Key\n(xpub)', self.public_key),
			('Multisig\nWallet', self.multisig_wallet),
			('Check\nAddress', self.check_address),
			('Sign PSBT', self.sign_psbt),
			('Shutdown', self.shutdown)
		])
	
	def mnemonic(self):  
		words = self.ctx.wallet.mnemonic.split(' ')
		self.display_mnemonic(words)
		self.ctx.input.wait_for_button()
		if self.ctx.printer.is_connected():
			lcd.clear()
			time.sleep_ms(1000)
			self.ctx.display.draw_centered_text('Print to QR?')
			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				self.ctx.display.flash_text('Printing\nmnemonic\nQR..')
				qr_code, _ = to_qr_codes(self.ctx.wallet.mnemonic, self.ctx.printer.qr_data_width(), FORMAT_NONE).__next__()
				self.ctx.printer.print_qr_code(qr_code)
		return MENU_CONTINUE

	def public_key(self):
		self.display_qr_codes(self.ctx.wallet.xpub_btc_core(), self.ctx.printer.qr_data_width(), FORMAT_NONE, title=self.ctx.wallet.xpub())
		if self.ctx.printer.is_connected():
			lcd.clear()
			time.sleep_ms(1000)
			self.ctx.display.draw_centered_text('Print to QR?')
			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				self.ctx.display.flash_text('Printing\nxpub\nQR..')
				qr_code, _ = to_qr_codes(self.ctx.wallet.xpub_btc_core(), self.ctx.printer.qr_data_width(), FORMAT_NONE).__next__()
				self.ctx.printer.print_qr_code(qr_code)
		self.display_qr_codes(self.ctx.wallet.zpub_btc_core(), self.ctx.printer.qr_data_width(), FORMAT_NONE, title=self.ctx.wallet.zpub())
		if self.ctx.printer.is_connected():
			lcd.clear()
			time.sleep_ms(1000)
			self.ctx.display.draw_centered_text('Print to QR?')
			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				self.ctx.display.flash_text('Printing\nzpub\nQR..')
				qr_code, _ = to_qr_codes(self.ctx.wallet.zpub_btc_core(), self.ctx.printer.qr_data_width(), FORMAT_NONE).__next__()
				self.ctx.printer.print_qr_code(qr_code)
		return MENU_CONTINUE
	
 	def multisig_wallet(self):
		if not self.ctx.multisig_wallet:
			self.ctx.display.draw_centered_text('Multisig wallet\nnot found.')
			self.ctx.display.draw_hcentered_text('Load one?', offset_y=200)
			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				return self.load_multisig()
		else:
			self.display_multisig(self.ctx.multisig_wallet)
			if self.ctx.printer.is_connected():
				lcd.clear()
				time.sleep_ms(1000)
				self.ctx.display.draw_centered_text('Print to QR?')
				btn = self.ctx.input.wait_for_button()
				if btn == BUTTON_ENTER:   
					self.ctx.display.flash_text('Printing\nmultisig\npolicy\nQR..')
					wallet_data, qr_format = self.ctx.multisig_wallet.wallet_qr()
					for qr_code, _ in to_qr_codes(wallet_data, self.ctx.printer.qr_data_width(), qr_format):
						self.ctx.printer.print_qr_code(qr_code)
		return MENU_CONTINUE
		
	def load_multisig(self):
		wallet_data, qr_format = self.capture_qr_code()
		if wallet_data is None:
			self.ctx.display.flash_text('Failed to load\nmultisig wallet', lcd.RED)
			return MENU_CONTINUE

		try:
			multisig_wallet = MultisigWallet(wallet_data, qr_format)
			if self.ctx.wallet.xpub() not in multisig_wallet.cosigners:
				raise ValueError('xpub not a cosigner')

			self.display_multisig(multisig_wallet, include_qr=False)
			self.ctx.display.draw_hcentered_text('Load?', offset_y=200)
			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				self.ctx.multisig_wallet = multisig_wallet
				self.ctx.log.debug('Multisig wallet descriptor: %s', self.ctx.multisig_wallet.descriptor.to_string())
				self.ctx.display.flash_text('Loaded multisig\nwallet')
				return MENU_CONTINUE
		except Exception as e:
			self.ctx.log.exception('Exception occurred loading multisig wallet')
			lcd.clear()
			self.ctx.display.draw_centered_text('Invalid multisig:\n%s' % repr(e), lcd.RED)
			self.ctx.input.wait_for_button()
			return MENU_CONTINUE
	
	def check_address(self):
		if not self.ctx.multisig_wallet:
			self.ctx.display.flash_text('Multisig wallet\nrequired', lcd.RED)
			return MENU_CONTINUE

		data, qr_format = self.capture_qr_code()
		if data is None or qr_format != FORMAT_NONE:
			self.ctx.display.flash_text('Failed to load\naddress', lcd.RED)
			return MENU_CONTINUE

		if data.lower().startswith('bitcoin:'):
			addr_end = data.find('?')
			if addr_end == -1:
				addr_end = len(data)
			data = data[8:addr_end]
   
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
			self.ctx.display.draw_centered_text('Checking\nreceive address\n' + str(i) + '\nfor match...')
			child_addr = self.ctx.multisig_wallet.descriptor.derive(i, branch_index=0).address(network=NETWORKS[self.ctx.net])
			if data == child_addr:
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
		if not self.ctx.multisig_wallet:
			self.ctx.display.draw_centered_text('Multisig wallet\nnot loaded.', lcd.WHITE)
			self.ctx.display.draw_hcentered_text('Sign anyway?', offset_y=200)
			btn = self.ctx.input.wait_for_button()
			if btn != BUTTON_ENTER:
				return MENU_CONTINUE
		
		data, qr_format = self.capture_qr_code()
		if data is None:
			self.ctx.display.flash_text('Failed to load\nPSBT', lcd.RED)
			return MENU_CONTINUE
	
		lcd.clear()
		self.ctx.display.draw_centered_text('Loading..')
  
		signer = PSBTSigner(data, qr_format)
		self.ctx.log.debug('Received PSBT: %s', signer.psbt)

	  	signer.validate(self.ctx.multisig_wallet)

		outputs = signer.outputs(self.ctx.multisig_wallet, self.ctx.net)
		lcd.clear()
  		self.ctx.display.draw_hcentered_text('\n\n'.join(outputs))
		self.ctx.display.draw_hcentered_text('Sign?', offset_y=200)
	
		btn = self.ctx.input.wait_for_button()
		if btn == BUTTON_ENTER:
			signed_psbt, qr_format = signer.sign(self.ctx.wallet.root)
			self.ctx.log.debug('Signed PSBT: %s', signer.psbt)
			signer = None
			gc.collect()
			self.display_qr_codes(signed_psbt, self.ctx.display.qr_data_width(), qr_format)
			if self.ctx.printer.is_connected():
				lcd.clear()
				time.sleep_ms(1000)
				self.ctx.display.draw_centered_text('Print to QRs?')
				btn = self.ctx.input.wait_for_button()
				if btn == BUTTON_ENTER:
					self.ctx.display.flash_text('Printing\nsigned\nPSBT\nQR..')
					for qr_code, _ in to_qr_codes(signed_psbt, self.ctx.printer.qr_data_width(), qr_format):
						self.ctx.printer.print_qr_code(qr_code)
		return MENU_CONTINUE

	def display_multisig(self, multisig_wallet, include_qr=True):
		about = multisig_wallet.label + '\n'
		xpubs = []
		for i, xpub in enumerate(multisig_wallet.cosigners):
			xpubs.append(str(i+1) + '. ' + xpub[4:8] + '...' + xpub[len(xpub)-4:len(xpub)])
		about += '\n'.join(xpubs)
		if include_qr:
			wallet_data, qr_format = self.ctx.multisig_wallet.wallet_qr()
			self.display_qr_codes(wallet_data, self.ctx.display.qr_data_width(), qr_format, title=about)
		else:
			self.ctx.display.draw_hcentered_text(about, offset_y=DEFAULT_PADDING)
