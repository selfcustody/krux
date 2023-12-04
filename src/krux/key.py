# The MIT License (MIT)

# Copyright (c) 2021-2023 Krux contributors

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
# pylint: disable=W0102
import time

try:
    import urandom as random
except:
    import random
from binascii import hexlify
from embit import bip32, bip39
from embit.wordlists.bip39 import WORDLIST
from embit.networks import NETWORKS
from .krux_settings import t

DER_SINGLE = "m/84h/%dh/0h"
DER_MULTI = "m/48h/%dh/0h/2h"
HARDENED_STR_REPLACE = "'"


class Key:
    """Represents a BIP-39 mnemonic-based private key"""

    def __init__(self, mnemonic, multisig, network=NETWORKS["test"], passphrase=""):
        self.mnemonic = mnemonic
        self.multisig = multisig
        self.network = network
        self.root = bip32.HDKey.from_seed(
            bip39.mnemonic_to_seed(mnemonic, passphrase), version=network["xprv"]
        )
        self.fingerprint = self.root.child(0).fingerprint
        self.derivation = self.get_default_derivation(self.multisig, network)
        self.account = self.root.derive(self.derivation).to_public()

    def xpub(self, version=None):
        """Returns the xpub representation of the extended master public key"""
        return self.account.to_base58(version)

    def key_expression(self, version=None):
        """Returns the extended master public key (xpub/ypub/zpub) in key expression format
        per https://github.com/bitcoin/bips/blob/master/bip-0380.mediawiki#key-expressions,
        prefixed with fingerprint and derivation.
        """
        return "[%s%s]%s" % (
            self.fingerprint_hex_str(False),
            self.derivation[
                1:
            ],  # remove leading m, necessary for creating a descriptor
            self.account_pubkey_str(version),
        )

    def account_pubkey_str(self, version=None):
        """Returns the account extended public key (xpub/ypub/zpub)"""
        return self.account.to_base58(version)

    def fingerprint_hex_str(self, pretty=False):
        """Returns the master key fingerprint in hex format"""
        formatted_txt = t("⊚ %s") if pretty else "%s"
        return formatted_txt % hexlify(self.fingerprint).decode("utf-8")

    def derivation_str(self, pretty=False):
        """Returns the derivation path for the Hierarchical Deterministic Wallet to
        be displayed as string
        """
        formatted_txt = t("↳ %s") if pretty else "%s"
        return (formatted_txt % self.derivation).replace("h", HARDENED_STR_REPLACE)

    def sign(self, message_hash):
        """Signs a message with the extended master private key"""
        return self.root.derive(self.derivation).sign(message_hash)

    def sign_at(self, derivation, message_hash):
        """Signs a message at an adress derived from master key (code adapted from specterDIY)"""
        from embit import ec
        from embit.util import secp256k1

        prv = self.root.derive(derivation).key
        sig = secp256k1.ecdsa_sign_recoverable(
            message_hash, prv._secret  # pylint: disable=W0212
        )
        flag = sig[64]
        flag = bytes([27 + flag + 4])
        ec_signature = ec.Signature(sig[:64])
        ser = flag + secp256k1.ecdsa_signature_serialize_compact(
            ec_signature._sig  # pylint: disable=W0212
        )
        return ser

    @staticmethod
    def pick_final_word(entropy, words):
        """Returns a random final word with a valid checksum for the given list of
        either 11 or 23 words
        """
        if len(words) != 11 and len(words) != 23:
            raise ValueError("must provide 11 or 23 words")

        random.seed(int(time.ticks_ms() + entropy))
        while True:
            word = random.choice(WORDLIST)
            mnemonic = " ".join(words) + " " + word
            if bip39.mnemonic_is_valid(mnemonic):
                return word

    @staticmethod
    def get_default_derivation(multisig, network):
        """Return the Krux default derivation path for single-sig or multisig"""
        return (DER_MULTI if multisig else DER_SINGLE) % network["bip32"]

    @staticmethod
    def get_default_derivation_str(multisig, network):
        """Return the Krux default derivation path for single-sig or multisig to
        be displayd as string
        """
        return "↳ " + Key.get_default_derivation(multisig, network).replace(
            "h", HARDENED_STR_REPLACE
        )
