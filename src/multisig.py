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
from embit.descriptor.descriptor import Descriptor

class MultisigPolicy:
	def __init__(self, policy):
		self.policy = policy
		self.label = policy['label']
		self.descriptor = Descriptor.from_string(policy['descriptor'])
		if not self.descriptor or not self.descriptor.is_basic_multisig:
			raise ValueError('Not multisig')
		self.m = int(str(self.descriptor.miniscript.args[0]))
		self.n = len(self.descriptor.keys)
		self.cosigners = [key.key.to_base58() for key in self.descriptor.keys]
		if self.descriptor.is_sorted:
			self.cosigners = sorted(self.cosigners)

	def matches_tx_policy(self, tx_policy):
		return tx_policy['cosigners'] == self.cosigners and tx_policy['m'] == self.m and tx_policy['n'] == self.n