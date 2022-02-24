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
import hashlib
import time
import urandom
from binascii import hexlify
from embit import bip32, bip39
from embit.wordlists.bip39 import WORDLIST
from embit.networks import NETWORKS

DER_SINGLE = 'm/84h/%dh/0h'
DER_MULTI  = 'm/48h/%dh/0h/2h'

class Key:
    """Represents a BIP-39 mnemonic-based private key"""

    def __init__(self, mnemonic, multisig, network=NETWORKS['test']):
        self.mnemonic = mnemonic
        self.multisig = multisig
        self.network = network
        self.root = bip32.HDKey.from_seed(bip39.mnemonic_to_seed(mnemonic), version=network['xprv'])
        self.fingerprint = self.root.child(0).fingerprint
        self.derivation = (DER_MULTI if self.multisig else DER_SINGLE) % network['bip32']
        self.account = self.root.derive(self.derivation).to_public()

    def xpub(self):
        """Returns the xpub representation of the extended master public key"""
        return self.account.to_base58()

    def xpub_btc_core(self):
        """Returns the xpub of the extended master public key, prefixed with
           fingerprint and derivation
        """
        return '[%s%s]%s' % (
            hexlify(self.fingerprint).decode('utf-8'),
            self.derivation[1:], # remove leading m
            self.account.to_base58()
        )

    def p2wsh_zpub(self):
        """Returns the Zpub representation of the extended master public key
           used for denoting P2WSH
        """
        return self.account.to_base58(self.network['Zpub'])

    def p2wsh_zpub_btc_core(self):
        """Returns the Zpub representation of the extended master public key
           used for denoting P2WSH, prefixed with fingerprint and derivation
        """
        return '[%s%s]%s' % (
            hexlify(self.fingerprint).decode('utf-8'),
            self.derivation[1:], # remove leading m
            self.account.to_base58(self.network['Zpub'])
        )

    def p2wpkh_zpub(self):
        """Returns the zpub representation of the extended master public key
           used for denoting P2WPKH
        """
        return self.account.to_base58(self.network['zpub'])

    def p2wpkh_zpub_btc_core(self):
        """Returns the zpub representation of the extended master public key
           used for denoting P2WPKH, prefixed with fingerprint and derivation
        """
        return '[%s%s]%s' % (
            hexlify(self.fingerprint).decode('utf-8'),
            self.derivation[1:], # remove leading m
            self.account.to_base58(self.network['zpub'])
        )

# Adapted from: https://github.com/trezor/python-mnemonic
def to_mnemonic_words(entropy):
    """Turns entropy into a mnemonic"""
    entropy_hash = hexlify(hashlib.sha256(entropy).digest()).decode()
    bits = (
        ('{:0>%d}' % (len(entropy) * 8)).format(bin(int.from_bytes(entropy, 'big'))[2:]) +
        ('{:0>256}'.format(bin(int(entropy_hash, 16))[2:])[: len(entropy) * 8 // 32])
    )
    words = []
    for i in range(len(bits) // 11):
        idx = int(bits[i * 11 : (i + 1) * 11], 2)
        words.append(WORDLIST[idx])
    return words

def pick_final_word(ctx, words):
    """Returns a random final word with a valid checksum for the given list of
       either 11 or 23 words
    """
    if (len(words) != 11 and len(words) != 23):
        raise ValueError('must provide 11 or 23 words')

    urandom.seed(int(time.ticks_ms() + ctx.input.entropy))
    while True:
        word = urandom.choice(WORDLIST)
        mnemonic = ' '.join(words) + ' ' + word
        if bip39.mnemonic_is_valid(mnemonic):
            return word
