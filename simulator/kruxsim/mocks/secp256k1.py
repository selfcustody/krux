import sys
from embit.util import secp256k1

if "secp256k1" not in sys.modules:
    sys.modules["secp256k1"] = secp256k1
