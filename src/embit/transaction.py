import sys
try:
    import uio as io
except ImportError:
    import io
import hashlib
from . import compact
from .script import Script, Witness
from . import hashes
from .base import EmbitBase, EmbitError

class TransactionError(EmbitError):
    pass

# micropython doesn't support typing and Enum
class SIGHASH:
    ALL = 1
    NONE = 2
    SINGLE = 3
    ANYONECANPAY = 0x80

    @classmethod
    def check(cls, sighash: int):
        anyonecanpay = False
        if sighash & cls.ANYONECANPAY:
            # remove ANYONECANPAY flag
            sighash = sighash ^ cls.ANYONECANPAY
            anyonecanpay = True
        if sighash not in [cls.ALL, cls.NONE, cls.SINGLE]:
            raise TransactionError("Invalid SIGHASH type")
        return sighash, anyonecanpay

# API similar to bitcoin-cli decoderawtransaction


class Transaction(EmbitBase):
    def __init__(self, version=2, vin=[], vout=[], locktime=0):
        self.version = version
        self.locktime = locktime
        self.vin = vin
        self.vout = vout
        # cache for digests
        self._hash_prevouts = None
        self._hash_sequence = None
        self._hash_outputs = None

    @property
    def is_segwit(self):
        # transaction is segwit if at least one input is segwit
        for inp in self.vin:
            if inp.is_segwit:
                return True
        return False

    def write_to(self, stream):
        """Returns the byte serialization of the transaction"""
        res = stream.write(self.version.to_bytes(4, "little"))
        if self.is_segwit:
            res += stream.write(b"\x00\x01")  # segwit marker and flag
        res += stream.write(compact.to_bytes(len(self.vin)))
        for inp in self.vin:
            res += inp.write_to(stream)
        res += stream.write(compact.to_bytes(len(self.vout)))
        for out in self.vout:
            res += out.write_to(stream)
        if self.is_segwit:
            for inp in self.vin:
                res += inp.witness.write_to(stream)
        res += stream.write(self.locktime.to_bytes(4, "little"))
        return res

    def hash(self):
        h = hashlib.sha256()
        h.update(self.version.to_bytes(4, "little"))
        h.update(compact.to_bytes(len(self.vin)))
        for inp in self.vin:
            h.update(inp.serialize())
        h.update(compact.to_bytes(len(self.vout)))
        for out in self.vout:
            h.update(out.serialize())
        h.update(self.locktime.to_bytes(4, "little"))
        hsh = hashlib.sha256(h.digest()).digest()
        return hsh

    def txid(self):
        return bytes(reversed(self.hash()))

    @classmethod
    def read_vout(cls, stream, idx):
        """Returns a tuple TransactionOutput, tx_hash without storing the whole tx in memory"""
        h = hashlib.sha256()
        h.update(stream.read(4))
        num_vin = compact.read_from(stream)
        # if num_vin is zero it is a segwit transaction
        is_segwit = num_vin == 0
        if is_segwit:
            marker = stream.read(1)
            if marker != b"\x01":
                raise TransactionError("Invalid segwit marker")
            num_vin = compact.read_from(stream)
        h.update(compact.to_bytes(num_vin))
        for i in range(num_vin):
            txin = TransactionInput.read_from(stream)
            h.update(txin.serialize())
        num_vout = compact.read_from(stream)
        h.update(compact.to_bytes(num_vout))
        if idx >= num_vout or idx < 0:
            raise TransactionError("Invalid vout index %d, max is %d" % (idx, num_vout-1))
        res = None
        for i in range(num_vout):
            vout = TransactionOutput.read_from(stream)
            if idx == i:
                res = vout
            h.update(vout.serialize())
        if is_segwit:
            for i in range(num_vin):
                Witness.read_from(stream)
        h.update(stream.read(4))
        return res, hashlib.sha256(h.digest()).digest()

    @classmethod
    def read_from(cls, stream):
        ver = int.from_bytes(stream.read(4), "little")
        num_vin = compact.read_from(stream)
        # if num_vin is zero it is a segwit transaction
        is_segwit = num_vin == 0
        if is_segwit:
            marker = stream.read(1)
            if marker != b"\x01":
                raise TransactionError("Invalid segwit marker")
            num_vin = compact.read_from(stream)
        vin = []
        for i in range(num_vin):
            vin.append(TransactionInput.read_from(stream))
        num_vout = compact.read_from(stream)
        vout = []
        for i in range(num_vout):
            vout.append(TransactionOutput.read_from(stream))
        if is_segwit:
            for inp in vin:
                inp.witness = Witness.read_from(stream)
        locktime = int.from_bytes(stream.read(4), "little")
        return cls(version=ver, vin=vin, vout=vout, locktime=locktime)

    def hash_prevouts(self):
        if self._hash_prevouts is None:
            h = hashlib.sha256()
            for inp in self.vin:
                h.update(bytes(reversed(inp.txid)))
                h.update(inp.vout.to_bytes(4, "little"))
            self._hash_prevouts = h.digest()
        return self._hash_prevouts

    def hash_sequence(self):
        if self._hash_sequence is None:
            h = hashlib.sha256()
            for inp in self.vin:
                h.update(inp.sequence.to_bytes(4, "little"))
            self._hash_sequence = h.digest()
        return self._hash_sequence

    def hash_outputs(self):
        if self._hash_outputs is None:
            h = hashlib.sha256()
            for out in self.vout:
                h.update(out.serialize())
            self._hash_outputs = h.digest()
        return self._hash_outputs

    def sighash_segwit(self, input_index, script_pubkey, value, sighash=SIGHASH.ALL):
        """check out bip-143"""
        if input_index < 0 or input_index >= len(self.vin):
            raise TransactionError("Invalid input index")
        sh, anyonecanpay = SIGHASH.check(sighash)
        inp = self.vin[input_index]
        zero = b"\x00"*32 # for sighashes
        h = hashlib.sha256()
        h.update(self.version.to_bytes(4, "little"))
        if anyonecanpay:
            h.update(zero)
        else:
            h.update(hashlib.sha256(self.hash_prevouts()).digest())
        if anyonecanpay or sh in [SIGHASH.NONE, SIGHASH.SINGLE]:
            h.update(zero)
        else:
            h.update(hashlib.sha256(self.hash_sequence()).digest())
        h.update(bytes(reversed(inp.txid)))
        h.update(inp.vout.to_bytes(4, "little"))
        h.update(script_pubkey.serialize())
        h.update(int(value).to_bytes(8, "little"))
        h.update(inp.sequence.to_bytes(4, "little"))
        if not (sh in [SIGHASH.NONE, SIGHASH.SINGLE]):
            h.update(hashlib.sha256(self.hash_outputs()).digest())
        elif sh == SIGHASH.SINGLE and input_index < len(self.vout):
            h.update(hashlib.sha256(
                hashlib.sha256(self.vout[input_index].serialize()).digest()
            ).digest())
        else:
            h.update(zero)
        h.update(self.locktime.to_bytes(4, "little"))
        h.update(sighash.to_bytes(4, "little"))
        return hashlib.sha256(h.digest()).digest()

    def sighash_legacy(self, input_index, script_pubkey, sighash=SIGHASH.ALL):
        if input_index < 0 or input_index >= len(self.vin):
            raise TransactionError("Invalid input index")
        sh, anyonecanpay = SIGHASH.check(sighash)
        # no corresponding output for this input, we sign 00...01
        if sh == SIGHASH.SINGLE and input_index >= len(self.vout):
            return b"\x00"*31+b"\x01"

        h = hashlib.sha256()
        h.update(self.version.to_bytes(4, "little"))
        # ANYONECANPAY - only one input is serialized
        if anyonecanpay:
            h.update(compact.to_bytes(1))
            h.update(self.vin[input_index].serialize(script_pubkey))
        else:
            h.update(compact.to_bytes(len(self.vin)))
            for i, inp in enumerate(self.vin):
                if input_index == i:
                    h.update(inp.serialize(script_pubkey))
                else:
                    h.update(inp.serialize(Script(b""), sighash))
        # no outputs
        if sh == SIGHASH.NONE:
            h.update(compact.to_bytes(0))
        # one output on the same index, others are empty
        elif sh == SIGHASH.SINGLE:
            h.update(compact.to_bytes(input_index+1))
            empty = TransactionOutput(0xFFFFFFFF, Script(b"")).serialize()
            # this way we commit to input index
            for i in range(input_index):
                h.update(empty)
            # last is ours
            h.update(self.vout[input_index].serialize())
        elif sh == SIGHASH.ALL:
            h.update(compact.to_bytes(len(self.vout)))
            for out in self.vout:
                h.update(out.serialize())
        else:
            # shouldn't happen
            raise TransactionError("Invalid sighash")
        h.update(self.locktime.to_bytes(4, "little"))
        h.update(sighash.to_bytes(4, "little"))
        return hashlib.sha256(h.digest()).digest()


class TransactionInput(EmbitBase):
    def __init__(self, txid, vout, script_sig=None, sequence=0xFFFFFFFF, witness=None):
        if script_sig is None:
            script_sig = Script(b"")
        if witness is None:
            witness = Witness([])
        self.txid = txid
        self.vout = vout
        self.script_sig = script_sig
        self.sequence = sequence
        self.witness = witness

    @property
    def is_segwit(self):
        return not (self.witness.serialize() == b"\x00")

    def write_to(self, stream, script_sig=None, sighash=SIGHASH.ALL):
        sh, anyonecanpay = SIGHASH.check(sighash)
        if anyonecanpay or sh in [SIGHASH.SINGLE, SIGHASH.NONE]:
            sequence = 0
        else:
            sequence = self.sequence
        res = stream.write(bytes(reversed(self.txid)))
        res += stream.write(self.vout.to_bytes(4, "little"))
        if script_sig is None:
            res += stream.write(self.script_sig.serialize())
        else:
            res += stream.write(script_sig.serialize())
        res += stream.write(sequence.to_bytes(4, "little"))
        return res

    @classmethod
    def read_from(cls, stream):
        txid = bytes(reversed(stream.read(32)))
        vout = int.from_bytes(stream.read(4), "little")
        script_sig = Script.read_from(stream)
        sequence = int.from_bytes(stream.read(4), "little")
        return cls(txid, vout, script_sig, sequence)


class TransactionOutput(EmbitBase):
    def __init__(self, value, script_pubkey):
        self.value = value
        self.script_pubkey = script_pubkey

    def write_to(self, stream):
        res = stream.write(self.value.to_bytes(8, "little"))
        res += stream.write(self.script_pubkey.serialize())
        return res

    @classmethod
    def read_from(cls, stream):
        value = int.from_bytes(stream.read(8), "little")
        script_pubkey = Script.read_from(stream)
        return cls(value, script_pubkey)
