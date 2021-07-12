try:
    # if it's micropython
    from micropython import const
    from secp256k1 import *
except:
    # we are in python
    try:
        # try ctypes bindings
        from .ctypes_secp256k1 import *
    except:
        # fallback to python version
        from .py_secp256k1 import *
