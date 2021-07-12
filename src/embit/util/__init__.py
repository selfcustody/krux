from . import secp256k1

try:
    from micropython import const
except:
    const = lambda x: x
