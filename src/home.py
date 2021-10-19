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
import gc
from display import DEFAULT_PADDING
from embit.networks import NETWORKS
import lcd
from psbt import PSBTSigner
from qr import FORMAT_NONE, FORMAT_PMOFN, to_qr_codes
from page import Page
from menu import Menu, MENU_CONTINUE
from input import BUTTON_ENTER
from wallet import Wallet

class Home(Page):
	def __init__(self, ctx):
		Page.__init__(self, ctx)
		self.menu = Menu(ctx, [
			(( 'Mnemonic' ), self.mnemonic),
			(( 'Public Key\n(xpub)' ), self.public_key),
			(( 'Wallet' ), self.wallet),
			(( 'Check\nAddress' ), self.check_address),
			(( 'Sign PSBT' ), self.sign_psbt),
			(( 'Shutdown' ), self.shutdown)
		])

	def mnemonic(self):
		self.display_mnemonic(self.ctx.wallet.key.mnemonic_words())
		self.ctx.input.wait_for_button()
		if self.ctx.printer.is_connected():
			lcd.clear()
			time.sleep_ms(1000)
			self.ctx.display.draw_centered_text(( 'Print to QR?' ))
			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				self.ctx.display.flash_text(( 'Printing..' ))
				qr_code, _ = to_qr_codes(self.ctx.wallet.key.mnemonic, self.ctx.printer.qr_data_width(), FORMAT_NONE).__next__()
				self.ctx.printer.print_qr_code(qr_code)
		return MENU_CONTINUE

	def public_key(self):
		self.display_qr_codes(self.ctx.wallet.key.xpub_btc_core(), self.ctx.printer.qr_data_width(), FORMAT_NONE, title=self.ctx.wallet.key.xpub())
		if self.ctx.printer.is_connected():
			lcd.clear()
			time.sleep_ms(1000)
			self.ctx.display.draw_centered_text(( 'Print to QR?' ))
			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				self.ctx.display.flash_text(( 'Printing..' ))
				qr_code, _ = to_qr_codes(self.ctx.wallet.key.xpub_btc_core(), self.ctx.printer.qr_data_width(), FORMAT_NONE).__next__()
				self.ctx.printer.print_qr_code(qr_code)
	
		if self.ctx.wallet.is_multisig():
			self.display_qr_codes(self.ctx.wallet.key.p2wsh_zpub_btc_core(), self.ctx.printer.qr_data_width(), FORMAT_NONE, title=self.ctx.wallet.key.p2wsh_zpub())
			if self.ctx.printer.is_connected():
				lcd.clear()
				time.sleep_ms(1000)
				self.ctx.display.draw_centered_text(( 'Print to QR?' ))
				btn = self.ctx.input.wait_for_button()
				if btn == BUTTON_ENTER:
					self.ctx.display.flash_text(( 'Printing..' ))
					qr_code, _ = to_qr_codes(self.ctx.wallet.key.p2wsh_zpub_btc_core(), self.ctx.printer.qr_data_width(), FORMAT_NONE).__next__()
					self.ctx.printer.print_qr_code(qr_code)
		else:
			self.display_qr_codes(self.ctx.wallet.key.p2wpkh_zpub_btc_core(), self.ctx.printer.qr_data_width(), FORMAT_NONE, title=self.ctx.wallet.key.p2wpkh_zpub())
			if self.ctx.printer.is_connected():
				lcd.clear()
				time.sleep_ms(1000)
				self.ctx.display.draw_centered_text(( 'Print to QR?' ))
				btn = self.ctx.input.wait_for_button()
				if btn == BUTTON_ENTER:
					self.ctx.display.flash_text(( 'Printing..' ))
					qr_code, _ = to_qr_codes(self.ctx.wallet.key.p2wpkh_zpub_btc_core(), self.ctx.printer.qr_data_width(), FORMAT_NONE).__next__()
					self.ctx.printer.print_qr_code(qr_code)
		return MENU_CONTINUE
	
 	def wallet(self):
		if not self.ctx.wallet.is_loaded():
			self.ctx.display.draw_centered_text(( 'Wallet\nnot found.' ))
			self.ctx.display.draw_hcentered_text(( 'Load one?' ), offset_y=200)
			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				return self.load_wallet()
		else:
			self.display_wallet(self.ctx.wallet)
			if self.ctx.printer.is_connected():
				lcd.clear()
				time.sleep_ms(1000)
				self.ctx.display.draw_centered_text(( 'Print to QR?' ))
				btn = self.ctx.input.wait_for_button()
				if btn == BUTTON_ENTER:   
					self.ctx.display.flash_text(( 'Printing..' ))
					wallet_data, qr_format = self.ctx.wallet.wallet_qr()
					for qr_code, _ in to_qr_codes(wallet_data, self.ctx.printer.qr_data_width(), qr_format):
						self.ctx.printer.print_qr_code(qr_code)
		return MENU_CONTINUE
		
	def load_wallet(self):
		wallet_data, qr_format = self.capture_qr_code()
		if wallet_data is None:
			self.ctx.display.flash_text(( 'Failed to\nload wallet' ), lcd.RED)
			return MENU_CONTINUE

		try:
			wallet = Wallet(self.ctx.wallet.key)
   			wallet.load(wallet_data, qr_format)
			self.display_wallet(wallet, include_qr=False)
			self.ctx.display.draw_hcentered_text(( 'Load?' ), offset_y=200)
			btn = self.ctx.input.wait_for_button()
			if btn == BUTTON_ENTER:
				self.ctx.wallet = wallet
				self.ctx.log.debug('Wallet descriptor: %s', self.ctx.wallet.descriptor.to_string())
				self.ctx.display.flash_text(( 'Loaded wallet' ))
				return MENU_CONTINUE
		except Exception as e:
			self.ctx.log.exception('Exception occurred loading wallet')
			lcd.clear()
			self.ctx.display.draw_centered_text(( 'Invalid wallet:\n%s' ) % repr(e), lcd.RED)
			self.ctx.input.wait_for_button()
			return MENU_CONTINUE
	
	def check_address(self):
		if not self.ctx.wallet.is_loaded() and self.ctx.wallet.is_multisig():
			self.ctx.display.flash_text(( 'Wallet required' ), lcd.RED)
			return MENU_CONTINUE

		data, qr_format = self.capture_qr_code()
		if data is None or qr_format != FORMAT_NONE:
			self.ctx.display.flash_text(( 'Failed to load\naddress' ), lcd.RED)
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
				self.ctx.display.draw_centered_text(( 'Checked\n%d receive\naddresses with\nno matches.' ) % (i + 1))
				self.ctx.display.draw_hcentered_text(( 'Try more?' ), offset_y=200)
				btn = self.ctx.input.wait_for_button()
				if btn != BUTTON_ENTER:
					break
 
			lcd.clear()
			self.ctx.display.draw_centered_text(( 'Checking\nreceive address\n%d\nfor match..' ) % i)
			child_addr = self.ctx.wallet.descriptor.derive(i, branch_index=0).address(network=NETWORKS[self.ctx.net])
			if data == child_addr:
				found = True
				break
			i += 1

		gc.collect()
  
		lcd.clear()
		if found:
			self.ctx.display.draw_centered_text(( '%s\n\nis a valid\nreceive address' ) % data, lcd.GREEN)
		else:
			self.ctx.display.draw_centered_text(( '%s\n\nwas\nNOT FOUND\nin the first\n%d receive\naddresses' ) % (data, i + 1), lcd.RED)
									   
		self.ctx.input.wait_for_button()

		return MENU_CONTINUE

	def sign_psbt(self):
		if not self.ctx.wallet.is_loaded():
			self.ctx.display.draw_centered_text(( 'WARNING:\nWallet\nnot loaded.\n\nSome checks\ncannot be\nperformed.' ), lcd.WHITE)
			self.ctx.display.draw_hcentered_text(( 'Proceed?' ), offset_y=200)
			btn = self.ctx.input.wait_for_button()
			if btn != BUTTON_ENTER:
				return MENU_CONTINUE
		
		data, qr_format = self.capture_qr_code()
		if data is None:
			self.ctx.display.flash_text(( 'Failed to load\nPSBT' ), lcd.RED)
			return MENU_CONTINUE
	
		lcd.clear()
		self.ctx.display.draw_centered_text(( 'Loading..' ))
  
		signer = PSBTSigner(self.ctx.wallet, data, FORMAT_PMOFN if qr_format == FORMAT_NONE else qr_format)
		self.ctx.log.debug('Received PSBT: %s', signer.psbt)

	  	signer.validate()

		outputs = signer.outputs(self.ctx.net)
		lcd.clear()
  		self.ctx.display.draw_hcentered_text('\n\n'.join(outputs))
		self.ctx.display.draw_hcentered_text(( 'Sign?' ), offset_y=200)
	
		btn = self.ctx.input.wait_for_button()
		if btn == BUTTON_ENTER:
			signed_psbt, qr_format = signer.sign()
			self.ctx.log.debug('Signed PSBT: %s', signer.psbt)
			signer = None
			gc.collect()
			self.display_qr_codes(signed_psbt, self.ctx.display.qr_data_width(), qr_format)
			if self.ctx.printer.is_connected():
				lcd.clear()
				time.sleep_ms(1000)
				self.ctx.display.draw_centered_text(( 'Print to QR?' ))
				btn = self.ctx.input.wait_for_button()
				if btn == BUTTON_ENTER:
					self.ctx.display.flash_text(( 'Printing..' ))
					for qr_code, _ in to_qr_codes(signed_psbt, self.ctx.printer.qr_data_width(), qr_format):
						self.ctx.printer.print_qr_code(qr_code)
		return MENU_CONTINUE

	def display_wallet(self, wallet, include_qr=True):
		about = wallet.label + '\n'
		if wallet.is_multisig():
			xpubs = []
			for i, xpub in enumerate(wallet.policy['cosigners']):
				xpubs.append(str(i+1) + '. ' + xpub[4:8] + '...' + xpub[len(xpub)-4:len(xpub)])
			about += '\n'.join(xpubs)
		else:
			xpub = wallet.key.xpub()
			about += xpub[4:8] + '...' + xpub[len(xpub)-4:len(xpub)]
		if include_qr:
			wallet_data, qr_format = wallet.wallet_qr()
			self.display_qr_codes(wallet_data, self.ctx.display.qr_data_width(), qr_format, title=about)
		else:
			self.ctx.display.draw_hcentered_text(about, offset_y=DEFAULT_PADDING)
