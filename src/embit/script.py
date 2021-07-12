from .networks import NETWORKS
from . import base58
from . import bech32
from . import hashes
from . import compact
from .base import EmbitBase, EmbitError
try:
    import uio as io
except ImportError:
    import io
SIGHASH_ALL = 1


class Script(EmbitBase):
    def __init__(self, data):
        self.data = data

    def address(self, network=NETWORKS["main"]):
        script_type = self.script_type()
        data = self.data

        if script_type is None:
            raise ValueError("This type of script doesn't have address representation")

        if script_type == "p2pkh":
            d = network["p2pkh"] + data[3:23]
            return base58.encode_check(d)

        if script_type == "p2sh":
            d = network["p2sh"] + data[2:22]
            return base58.encode_check(d)

        if script_type in ["p2wpkh", "p2wsh"]:
            ver = data[0]
            # FIXME: should be one of OP_N
            if ver > 0:
                ver = ver % 0x50
            return bech32.encode(network["bech32"], ver, data[2:])

        # we should never get here
        raise ValueError("Unsupported script type")

    def script_type(self):
        data = self.data
        # OP_DUP OP_HASH160 <20:hash160(pubkey)> OP_EQUALVERIFY OP_CHECKSIG
        if len(data) == 25 and data[:3] == b"\x76\xa9\x14" and data[-2:] == b"\x88\xac":
            return "p2pkh"
        # OP_HASH160 <20:hash160(script)> OP_EQUAL
        if len(data) == 23 and data[:2] == b"\xa9\x14" and data[-1] == 0x87:
            return "p2sh"
        # 0 <20:hash160(pubkey)>
        if len(data) == 22 and data[:2] == b"\x00\x14":
            return "p2wpkh"
        # 0 <32:sha256(script)>
        if len(data) == 34 and data[:2] == b"\x00\x20":
            return "p2wsh"
        # unknown type
        return None

    def write_to(self, stream):
        res = stream.write(compact.to_bytes(len(self.data)))
        res += stream.write(self.data)
        return res

    @classmethod
    def read_from(cls, stream):
        l = compact.read_from(stream)
        data = stream.read(l)
        if len(data) != l:
            raise ValueError("Cant read %d bytes" % l)
        return cls(data)

    def __eq__(self, other):
        return self.data == other.data

    def __ne__(self, other):
        return self.data != other.data


class Witness(EmbitBase):
    def __init__(self, items):
        self.items = items[:]

    def write_to(self, stream):
        res = stream.write(compact.to_bytes(len(self.items)))
        for item in self.items:
            res += stream.write(compact.to_bytes(len(item)))
            res += stream.write(item)
        return res

    @classmethod
    def read_from(cls, stream):
        num = compact.read_from(stream)
        items = []
        for i in range(num):
            l = compact.read_from(stream)
            data = stream.read(l)
            items.append(data)
        return cls(items)


def p2pkh(pubkey):
    """Return Pay-To-Pubkey-Hash ScriptPubkey"""
    return Script(b"\x76\xa9\x14" + hashes.hash160(pubkey.sec()) + b"\x88\xac")


def p2sh(script):
    """Return Pay-To-Script-Hash ScriptPubkey"""
    return Script(b"\xa9\x14" + hashes.hash160(script.data) + b"\x87")


def p2wpkh(pubkey):
    """Return Pay-To-Witness-Pubkey-Hash ScriptPubkey"""
    return Script(b"\x00\x14" + hashes.hash160(pubkey.sec()))


def p2wsh(script):
    """Return Pay-To-Witness-Pubkey-Hash ScriptPubkey"""
    return Script(b"\x00\x20" + hashes.sha256(script.data))


def p2pkh_from_p2wpkh(script):
    """Convert p2wpkh to p2pkh script"""
    return Script(b"\x76\xa9" + script.serialize()[2:] + b"\x88\xac")


def multisig(m: int, pubkeys):
    if m <= 0 or m > 16:
        raise ValueError("m must be between 1 and 16")
    n = len(pubkeys)
    if n < m or n > 16:
        raise ValueError("Number of pubkeys must be between %d and 16" % m)
    data = bytes([80 + m])
    for pubkey in pubkeys:
        sec = pubkey.sec()
        data += bytes([len(sec)]) + sec
    # OP_m <len:pubkey> ... <len:pubkey> OP_n OP_CHECKMULTISIG
    data += bytes([80 + n, 0xAE])
    return Script(data)


def address_to_scriptpubkey(addr):
    # try with base58 address
    try:
        data = base58.decode_check(addr)
        prefix = data[:1]
        for net in NETWORKS.values():
            if prefix == net["p2pkh"]:
                return Script(b"\x76\xa9\x14" + data[1:] + b"\x88\xac")
            elif prefix == net["p2sh"]:
                return Script(b"\xa9\x14" + data[1:] + b"\x87")
    except:
        # fail - then it's bech32 address
        hrp = addr.split("1")[0]
        ver, data = bech32.decode(hrp, addr)
        if ver != 0 or len(data) not in [20, 32]:
            raise EmbitError("Invalid bech32 address")
        return Script(bytes([ver, len(data)] + data))


def script_sig_p2pkh(signature, pubkey):
    sec = pubkey.sec()
    der = signature.serialize() + bytes([SIGHASH_ALL])
    data = compact.to_bytes(len(der)) + der + compact.to_bytes(len(sec)) + sec
    return Script(data)


def script_sig_p2sh(redeem_script):
    """Creates scriptsig for p2sh"""
    # FIXME: implement for legacy p2sh as well
    return Script(redeem_script.serialize())


def witness_p2wpkh(signature, pubkey):
    return Witness([signature.serialize() + bytes([SIGHASH_ALL]), pubkey.sec()])
