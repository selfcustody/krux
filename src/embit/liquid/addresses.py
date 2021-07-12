from .. import bech32, ec, script, base58
from . import blech32
import hmac
from .networks import NETWORKS

def address(script, blinding_key=None, network=NETWORKS['liquidv1']):
    if script.data == b"":
        return "Fee"
    if script.script_type() == "p2sh":
        data = script.data[2:-1]
        if blinding_key is None:
            return base58.encode_check(network["p2sh"]+data)
        else:
            return base58.encode_check(network["bp2sh"]+blinding_key.sec()+data)
    else:
        data = script.data
        ver = data[0]
        # FIXME: should be one of OP_N
        if ver > 0:
            ver = ver % 0x50
        if blinding_key is None:
            return bech32.encode(network["bech32"], ver, data[2:])
        else:
            return blech32.encode(network["blech32"], ver, blinding_key.sec() + data[2:])

# TODO: refactor with network
def addr_decode(addr):
    if addr == "Fee":
        return script.Script(), None
    if addr[:3] in ["lq1", "el1"]:
        hrp = addr.split("1")[0]
        ver, data = blech32.decode(hrp, addr)
        data = bytes(data)
        pub = ec.PublicKey.parse(data[:33])
        pubhash = data[33:]
        sc = script.Script(b"\x00"+bytes([len(pubhash)])+pubhash)
    elif addr[:3] in ["ex1", "ert"]:
        hrp = addr.split("1")[0]
        ver, data = bech32.decode(hrp, addr)
        pub = None
        sc = script.Script(b"\x00"+bytes([len(data)])+bytes(data))
    else:
        data = base58.decode_check(addr)
        if data[:2] in [b"\x0c\x27", b"\x04\x4b"]:
            pub = ec.PublicKey.parse(data[2:35])
            sc = script.Script(b"\xa9\x14"+data[35:]+b"\x87")
        elif data[:1] in [b"\x27", b"\x4b"]:
            pub = None
            sc = script.Script(b"\xa9\x14"+data[1:]+b"\x87")
        else:
            raise RuntimeError("Invalid address")
    return sc, pub

