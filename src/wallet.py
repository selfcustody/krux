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
	import uio as io
except ImportError:
	import io
import random
from binascii import hexlify
from embit.wordlists.ubip39 import WORDLIST
from embit import bip32, bip39, ec, script
from embit.networks import NETWORKS

SATS_PER_BTC = const(100000000)

class Wallet:
	def __init__(self, mnemonic, network=NETWORKS['test']):
		self.mnemonic = mnemonic
		self.network = network
		seed = bip39.mnemonic_to_seed(mnemonic)
		self.root = bip32.HDKey.from_seed(seed, version=network['xprv'])
		self.fingerprint = self.root.child(0).fingerprint
		self.derivation = 'm/48h/%dh/0h/2h' % network['bip32'] # contains coin type - 0 for main, 1 for test
		self.account = self.root.derive(self.derivation).to_public()
		
	def xpub(self):
		return self.account.to_base58()

	def xpub_btc_core(self):
		return '[%s%s]%s' % (
			hexlify(self.fingerprint).decode('utf-8'),
			self.derivation[1:], # remove leading m
			self.account.to_base58()
		)
	
def pick_final_word(words):
	if len(words) != 11:
		return None
	
	while True:
		word = random.choice(WORDLIST)
		mnemonic = ' '.join(words) + ' ' + word
		if bip39.mnemonic_is_valid(mnemonic):
			return word
	return None
		
# Functions below adapted from: https://github.com/SeedSigner/seedsigner
def parse_multisig(sc):
	"""Takes a script and extracts m,n and pubkeys from it"""
	# OP_m <len:pubkey> ... <len:pubkey> OP_n OP_CHECKMULTISIG
	# check min size
	if len(sc.data) < 37 or sc.data[-1] != 0xAE:
		raise ValueError('Not a multisig script')
	m = sc.data[0] - 0x50
	if m < 1 or m > 16:
		raise ValueError('Invalid multisig script')
	n = sc.data[-2] - 0x50
	if n < m or n > 16:
		raise ValueError('Invalid multisig script')
	s = io.BytesIO(sc.data)
	# drop first byte
	s.read(1)
	# read pubkeys
	pubkeys = []
	for i in range(n):
		char = s.read(1)
		if char != b'\x21':
			raise ValueError('Invalid pubkey')
		pubkeys.append(ec.PublicKey.parse(s.read(33)))
	# check that nothing left
	if s.read() != sc.data[-2:]:
		raise ValueError('Invalid multisig script')
	return m, n, pubkeys

def get_cosigners(pubkeys, derivations, xpubs):
	"""Returns xpubs used to derive pubkeys using global xpub field from psbt"""
	cosigners = []
	for i, pubkey in enumerate(pubkeys):
		if pubkey not in derivations:
			raise ValueError('Missing derivation')
		der = derivations[pubkey]
		for xpub in xpubs:
			origin_der = xpubs[xpub]
			# check fingerprint
			if origin_der.fingerprint == der.fingerprint:
				# check derivation - last two indexes give pub from xpub
				if origin_der.derivation == der.derivation[:-2]:
					# check that it derives to pubkey actually
					if xpub.derive(der.derivation[-2:]).key == pubkey:
						# append strings so they can be sorted and compared
						cosigners.append(xpub.to_base58())
						break
	return sorted(cosigners)

def get_tx_policy(tx):
	# Check inputs of the transaction and check that they use the same script type
	# For multisig parsed policy will look like this:
	# { script_type: p2wsh, cosigners: [xpubs strings], m: 2, n: 3}
	policy = None
	for inp in tx.inputs:
		# get policy of the input
		inp_policy = get_policy(inp, inp.witness_utxo.script_pubkey, tx.xpubs)
		# if policy is None - assign current
		if policy is None:
			policy = inp_policy
		# otherwise check that everything in the policy is the same
		else:
			# check policy is the same
			if policy != inp_policy:
				raise RuntimeError('Mixed inputs in the transaction')
	return policy

def get_tx_input_amount(tx):
	inp_amount = 0
	for inp in tx.inputs:
		inp_amount += inp.witness_utxo.value
	return inp_amount

def get_tx_input_amount_message(tx):
	return 'Input:\n%.8f BTC' % round(get_tx_input_amount(tx) / SATS_PER_BTC, 8)

def get_tx_output_amount_messages(tx, network='main'):
	messages = []
	policy = get_tx_policy(tx)
	inp_amount = get_tx_input_amount(tx)
	spending = 0
	change = 0
	for i, out in enumerate(tx.outputs):
		out_policy = get_policy(out, tx.tx.vout[i].script_pubkey, tx.xpubs)
		is_change = False
		# if policy is the same - probably change
		if out_policy == policy:
			# double-check that it's change
			# we already checked in get_cosigners and parse_multisig
			# that pubkeys are generated from cosigners,
			# and witness script is corresponding multisig
			# so we only need to check that scriptpubkey is generated from
			# witness script

			# empty script by default
			sc = script.Script(b'')
			# multisig, we know witness script
			if policy['type'] == 'p2wsh':
				sc = script.p2wsh(out.witness_script)
			elif policy['type'] == 'p2sh-p2wsh':
				sc = script.p2sh(script.p2wsh(out.witness_script))
			else:
				raise RuntimeError('Unexpected single sig')
			if sc.data == tx.tx.vout[i].script_pubkey.data:
				is_change = True
		if is_change:
			change += tx.tx.vout[i].value
		else:
			spending += tx.tx.vout[i].value
			messages.append(
				'Sending:\n%.8f BTC\n\nTo:\n%s'
				% (round(tx.tx.vout[i].value / SATS_PER_BTC, 8), tx.tx.vout[i].script_pubkey.address(network=NETWORKS[network]))
			)
	fee = inp_amount - change - spending
	messages.append('Fee:\n%.8f BTC' % round(fee / SATS_PER_BTC, 8))
 	messages.sort(reverse=True)
	return messages

def get_policy(scope, scriptpubkey, xpubs):
	"""Parse scope and get policy"""
	# we don't know the policy yet, let's parse it
	script_type = scriptpubkey.script_type()
	# p2sh can be either legacy multisig, or nested segwit multisig
	# or nested segwit singlesig
	if script_type == 'p2sh':
		if scope.witness_script is not None:
			script_type = 'p2sh-p2wsh'
		elif (
			scope.redeem_script is not None
			and scope.redeem_script.script_type() == 'p2wpkh'
		):
			script_type = 'p2sh-p2wpkh'
	policy = {'type': script_type}
	# expected multisig
	if 'p2wsh' in script_type and scope.witness_script is not None:
		m, n, pubkeys = parse_multisig(scope.witness_script)
		# check pubkeys are derived from cosigners
		cosigners = get_cosigners(pubkeys, scope.bip32_derivations, xpubs)
		policy.update({'m': m, 'n': n, 'cosigners': cosigners})
	return policy

def is_multisig(policy):
	return 'm' in policy and 'n' in policy and 'cosigners' in policy
