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
from baseconv import base_encode, try_decode
from embit import psbt
from embit.descriptor.descriptor import Descriptor
from embit.descriptor.arguments import Key, KeyHash, AllowedDerivation
from qr import FORMAT_PMOFN, FORMAT_UR
from ur.ur import UR
import urtypes
from urtypes import BYTES
from urtypes.crypto import CRYPTO_PSBT
from wallet import get_tx_output_amount_messages, get_tx_policy, is_multisig
try:
	import ujson as json
except ImportError:
	import json
 
class MultisigWallet:
	def __init__(self, wallet_data, qr_format):
		self.wallet_data = wallet_data
		self.wallet_qr_format = qr_format
		self.descriptor = None
		self.label = None

		self.load(wallet_data)

		if not self.descriptor or not self.descriptor.is_basic_multisig:
			raise ValueError('Not multisig')

		# If child derivation info is missing to generate receive addresses, 
  		# use the default scheme
		for i in range(len(self.descriptor.miniscript.args)):
			key = self.descriptor.miniscript.args[i]
			if isinstance(key, Key) or isinstance(key, KeyHash):
				if key.allowed_derivation is None:
					key.allowed_derivation = AllowedDerivation.default()
     
		self.m = int(str(self.descriptor.miniscript.args[0]))
		self.n = len(self.descriptor.keys)
		self.cosigners = [key.key.to_base58() for key in self.descriptor.keys]
		if self.descriptor.is_sorted:
			self.cosigners = sorted(self.cosigners)

		if not self.label:
			self.label = '%d of %d multisig' % (self.m, self.n)

	def load(self, wallet_data):
		if isinstance(wallet_data, UR):
			# Try to parse as a Crypto-Output type
			try:
				output = urtypes.crypto.Output.from_cbor(wallet_data.cbor)
				self.descriptor = Descriptor.from_string(output.descriptor())
				return
			except: pass
	
			# If a generic UR bytes object was sent, extract the data for further processing
			try:
				wallet_data = urtypes.Bytes.from_cbor(wallet_data.cbor).data
			except: pass
  
		# Process as a string
		wallet_data = wallet_data.decode() if not isinstance(wallet_data, str) else wallet_data
  
		# Try to parse as JSON and look for a 'descriptor' key
		try:
			wallet_json = json.loads(wallet_data)
			if 'descriptor' in wallet_json:
				self.descriptor = Descriptor.from_string(wallet_json['descriptor'])
				if 'label' in wallet_json:
					self.label = wallet_json['label']
				return
		except: pass
	
		# Try to parse as a key-value file
		try:
			key_vals = []
			for word in wallet_data.split(':'):
				for w in word.split('\n'):
					w = w.strip()
					if w != '':
						key_vals.append(w)

			if len(key_vals) > 0:
				script = key_vals[key_vals.index('Format') + 1].lower()
				if script != 'p2wsh':
					raise ValueError('Invalid script type: ' + script)
					
				policy = key_vals[key_vals.index('Policy') + 1]
				m = int(policy[:policy.index('of')].strip())
				n = int(policy[policy.index('of')+2:].strip())
				
				keys = []
				for i in range(len(key_vals)):
					xpub = key_vals[i]
					if xpub.lower().startswith('xpub') or xpub.lower().startswith('tpub'):
						fingerprint = key_vals[i-1]
						keys.append((xpub, fingerprint))
		
				if len(keys) != n:
					raise ValueError('Expected %d keys, found %d' % (n, len(keys)))
 
				derivation = key_vals[key_vals.index('Derivation') + 1]

				keys.sort()
				keys = ['[%s/%s]%s' % (key[1], derivation[2:], key[0]) for key in keys]

				self.descriptor = Descriptor.from_string(('wsh(sortedmulti(%d,' % m) + ','.join(keys) + '))')
				if key_vals.index('Name') >= 0:
					self.label = key_vals[key_vals.index('Name') + 1]
				return
		except: pass

		raise ValueError('Invalid wallet format')

	def wallet_qr(self):
		return (self.wallet_data, self.wallet_qr_format)
  
	def matches_tx_policy(self, tx_policy):
		return tx_policy['cosigners'] == self.cosigners and tx_policy['m'] == self.m and tx_policy['n'] == self.n

def psbt_qr(signed_psbt, qr_format):
	trimmed_psbt = psbt.PSBT(signed_psbt.tx)
	for i, inp in enumerate(signed_psbt.inputs):
		trimmed_psbt.inputs[i].partial_sigs = inp.partial_sigs

	if qr_format == FORMAT_UR:
		return (UR(CRYPTO_PSBT.type, urtypes.crypto.PSBT(trimmed_psbt.serialize()).to_cbor()), FORMAT_UR)

	return (trimmed_psbt.to_base64(), FORMAT_PMOFN)

class PSBTSigner:
	def __init__(self, psbt_data, qr_format):
		self.qr_format = qr_format
		self.base_encoding = None
		self.ur_type = None
		if isinstance(psbt_data, UR):
			try:
				self.psbt = psbt.PSBT.parse(urtypes.crypto.PSBT.from_cbor(psbt_data.cbor).data)
				self.ur_type = CRYPTO_PSBT
			except:
				self.psbt = psbt.PSBT.parse(urtypes.Bytes.from_cbor(psbt_data.cbor).data)
				self.ur_type = BYTES
		else:
			try:
				psbt_data, base = try_decode(psbt_data)
				self.base_encoding = base
			except: pass
			self.psbt = psbt.PSBT.parse(psbt_data)
   
	def validate(self, multisig_wallet):
		policy = get_tx_policy(self.psbt, multisig_wallet)
  
  		if not is_multisig(policy):
			raise ValueError('not multisig tx')

		if multisig_wallet and not multisig_wallet.matches_tx_policy(policy):
			raise ValueError('policy mismatch')

	def outputs(self, multisig_wallet, network):
		return get_tx_output_amount_messages(self.psbt, multisig_wallet, network)

	def sign(self, root_key):
		sigs_added = self.psbt.sign_with(root_key)
		if sigs_added == 0:
			raise ValueError('cannot sign')

		trimmed_psbt = psbt.PSBT(self.psbt.tx)
		for i, inp in enumerate(self.psbt.inputs):
			trimmed_psbt.inputs[i].partial_sigs = inp.partial_sigs

		self.psbt = trimmed_psbt
  
		psbt_data = self.psbt.serialize()
		if self.ur_type == CRYPTO_PSBT:
			return (UR(CRYPTO_PSBT.type, urtypes.crypto.PSBT(psbt_data).to_cbor()), self.qr_format)
		elif self.ur_type == BYTES:
			return (UR(BYTES.type, urtypes.Bytes(psbt_data).to_cbor()), self.qr_format)
		elif self.ur_type is None:
			if self.base_encoding is not None:
				psbt_data = base_encode(psbt_data, self.base_encoding).strip().decode()
			return (psbt_data, self.qr_format)