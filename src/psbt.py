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
import io
from ur.ur import UR
from embit import ec, script
from embit.networks import NETWORKS
from embit.psbt import DerivationPath, PSBT
import urtypes
from urtypes import BYTES
from urtypes.crypto import CRYPTO_PSBT
from baseconv import base_encode, try_decode

SATS_PER_BTC = const(100000000)

class PSBTSigner:
    """Responsible for validating and signing PSBTs"""

    def __init__(self, wallet, psbt_data):
        self.wallet = wallet
        self.base_encoding = None
        self.ur_type = None
        if isinstance(psbt_data, UR):
            try:
                self.psbt = PSBT.parse(urtypes.crypto.PSBT.from_cbor(psbt_data.cbor).data)
                self.ur_type = CRYPTO_PSBT
            except:
                self.psbt = PSBT.parse(urtypes.Bytes.from_cbor(psbt_data.cbor).data)
                self.ur_type = BYTES
        else:
            try:
                psbt_data, base = try_decode(psbt_data)
                self.base_encoding = base
            except:
                pass
            self.psbt = PSBT.parse(psbt_data)

    def validate(self):
        """Validates that the PSBT policy matches the wallet policy"""
        policy = get_tx_policy(self.psbt, self.wallet)

        if not self.wallet.is_multisig() and is_multisig(policy):
            raise ValueError('multisig tx')
        if self.wallet.is_multisig() and not is_multisig(policy):
            raise ValueError('not multisig tx')

        if self.wallet.is_loaded():
            if self.wallet.policy != policy:
                raise ValueError('policy mismatch')

    def outputs(self, network):
        """Returns a list of messages describing where amounts are going"""
        return get_tx_output_amount_messages(self.psbt, self.wallet, network)

    def sign(self):
        """Signs the PSBT and returns it"""
        sigs_added = self.psbt.sign_with(self.wallet.key.root)
        if sigs_added == 0:
            raise ValueError('cannot sign')

        trimmed_psbt = PSBT(self.psbt.tx)
        for i, inp in enumerate(self.psbt.inputs):
            trimmed_psbt.inputs[i].partial_sigs = inp.partial_sigs

        self.psbt = trimmed_psbt

        psbt_data = self.psbt.serialize()
        if self.ur_type == CRYPTO_PSBT:
            return UR(CRYPTO_PSBT.type, urtypes.crypto.PSBT(psbt_data).to_cbor())

        if self.ur_type == BYTES:
            return UR(BYTES.type, urtypes.Bytes(psbt_data).to_cbor())

        if self.base_encoding is not None:
            psbt_data = base_encode(psbt_data, self.base_encoding).strip().decode()
        return psbt_data

# Functions below adapted from: https://github.com/SeedSigner/seedsigner
def parse_multisig(sc):
    """Takes a script and extracts m,n and pubkeys from it"""
    # OP_m <len:pubkey> ... <len:pubkey> OP_n OP_CHECKMULTISIG
    # check min size
    if len(sc.data) < 37 or sc.data[-1] != 0xAE:
        raise ValueError('not a multisig script')
    m = sc.data[0] - 0x50
    if m < 1 or m > 16:
        raise ValueError('invalid multisig script')
    n = sc.data[-2] - 0x50
    if n < m or n > 16:
        raise ValueError('invalid multisig script')
    s = io.BytesIO(sc.data)
    # drop first byte
    s.read(1)
    # read pubkeys
    pubkeys = []
    for _ in range(n):
        char = s.read(1)
        if char != b'\x21':
            raise ValueError('invalid pubkey')
        pubkeys.append(ec.PublicKey.parse(s.read(33)))
    # check that nothing left
    if s.read() != sc.data[-2:]:
        raise ValueError('invalid multisig script')
    return m, n, pubkeys

def get_cosigners(pubkeys, derivations, xpubs):
    """Returns xpubs used to derive pubkeys using global xpub field from psbt"""
    cosigners = []
    for _, pubkey in enumerate(pubkeys):
        if pubkey not in derivations:
            raise ValueError('missing derivation')
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

def wallet_xpubs(wallet):
    """Returns the wallet's xpubs mapped to their derivations"""
    xpubs = {}
    if wallet.descriptor:
        if wallet.descriptor.key:
            xpubs[wallet.descriptor.key.key] = DerivationPath(
                wallet.descriptor.key.origin.fingerprint,
                wallet.descriptor.key.origin.derivation
            )
        else:
            for descriptor_key in wallet.descriptor.keys:
                xpubs[descriptor_key.key] = DerivationPath(
                    descriptor_key.origin.fingerprint,
                    descriptor_key.origin.derivation
                )
    return xpubs

def get_tx_policy(tx, wallet):
    """Check inputs of the transaction and check that they use the same script type
       For multisig parsed policy will look like this:
       { script_type: p2wsh, cosigners: [xpubs strings], m: 2, n: 3}
    """
    xpubs = tx.xpubs if tx.xpubs else wallet_xpubs(wallet)
    policy = None
    for inp in tx.inputs:
        # get policy of the input
        inp_policy = get_policy(inp, inp.witness_utxo.script_pubkey, xpubs)
        # if policy is None - assign current
        if policy is None:
            policy = inp_policy
        # otherwise check that everything in the policy is the same
        else:
            # check policy is the same
            if policy != inp_policy:
                raise RuntimeError('mixed inputs in the transaction')
    return policy

def get_tx_input_amount(tx):
    """Returns the the total input amount"""
    inp_amount = 0
    for inp in tx.inputs:
        inp_amount += inp.witness_utxo.value
    return inp_amount

def get_tx_input_amount_message(tx):
    """Returns the total input amount as a message for the user"""
    return ( 'Input:\n₿%s' ) % satcomma(get_tx_input_amount(tx))

def get_tx_output_amount_messages(tx, wallet, network='main'):
    """Returns the output amounts as messages for the user"""
    xpubs = tx.xpubs if tx.xpubs else wallet_xpubs(wallet)
    messages = []
    policy = get_tx_policy(tx, wallet)
    inp_amount = get_tx_input_amount(tx)
    spending = 0
    change = 0
    for i, out in enumerate(tx.outputs):
        out_policy = get_policy(out, tx.tx.vout[i].script_pubkey, xpubs)
        is_change = False
        # if policy is the same - probably change
        if out_policy == policy:
            # multisig, we know witness script
            if 'p2wsh' in policy['type']:
                # double-check that it's change
                # we already checked in get_cosigners and parse_multisig
                # that pubkeys are generated from cosigners,
                # and witness script is corresponding multisig
                # so we only need to check that scriptpubkey is generated from
                # witness script
                sc = script.Script(b'')
                if policy['type'] == 'p2wsh':
                    sc = script.p2wsh(out.witness_script)
                elif policy['type'] == 'p2sh-p2wsh':
                    sc = script.p2sh(script.p2wsh(out.witness_script))
                else:
                    raise RuntimeError('unexpected script type')
                if sc.data == tx.tx.vout[i].script_pubkey.data:
                    is_change = True
            elif policy['type'] == 'p2wpkh':
                # should be one or zero for single-key addresses
                for pub in out.bip32_derivations:
                    # check if it is our key
                    if out.bip32_derivations[pub].fingerprint == wallet.key.fingerprint:
                        hdkey = wallet.key.root.derive(out.bip32_derivations[pub].derivation)
                        mypub = hdkey.key.get_public_key()
                        if mypub != pub:
                            raise ValueError("bad derivation path")
                        # now check if provided scriptpubkey matches
                        sc = script.p2wpkh(mypub)
                        if sc == tx.tx.vout[i].script_pubkey:
                            is_change = True
        if is_change:
            change += tx.tx.vout[i].value
        else:
            spending += tx.tx.vout[i].value
            messages.append(
                ( 'Sending:\n₿%s\n\nTo:\n%s' )
                %
                (
                    satcomma(tx.tx.vout[i].value),
                    tx.tx.vout[i].script_pubkey.address(network=NETWORKS[network])
                )
            )
    fee = inp_amount - change - spending
    messages.append(( 'Fee:\n₿%s' ) % satcomma(fee))
    return messages

def add_commas(number, comma_sep=','):
    """Returns a number separated with commas"""
    triplets_num = len(number) // 3
    remainder = len(number) % 3
    triplets = [number[:remainder]] if remainder else []
    triplets += [number[remainder+i*3:remainder+3+i*3] for i in range(triplets_num)]
    return comma_sep.join(triplets)

def satcomma(amount):
    """Formats a BTC amount according to the Satcomma standard:
       https://medium.com/coinmonks/the-satcomma-standard-89f1e7c2aede
    """
    amount_str = '%.8f' % round(amount / SATS_PER_BTC, 8)
    msb = amount_str[:-9] # most significant bitcoin heh heh heh
    lsb = amount_str[len(msb)+1:]
    return add_commas(msb, ( ',' )) + ( '.' ) + add_commas(lsb, ( ',' ))

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
    """Returns a boolean indicating if the policy is a multisig"""
    return (
        'type' in policy and
        'p2wsh' in policy['type'] and
        'm' in policy and
        'n' in policy and
        'cosigners' in policy
    )
