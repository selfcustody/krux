import hmac
from ..ec import PrivateKey

DOMAIN = b"Symmetric key seed"
LABEL = b"SLIP-0077"

def master_blinding_from_seed(seed):
    root = hmac.new(DOMAIN, seed, digestmod='sha512').digest()
    node = hmac.new(root[0:32], b"\x00" + LABEL, digestmod='sha512').digest()
    return PrivateKey(node[32:])

def blinding_key(mbk, script_pubkey):
    bpk = hmac.new(mbk.secret, script_pubkey.data, digestmod='sha256').digest()
    return PrivateKey(bpk)