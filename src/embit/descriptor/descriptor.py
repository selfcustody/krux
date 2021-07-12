from binascii import hexlify, unhexlify
try:
    import uio as io
except ImportError:
    import io
from .. import hashes, compact, ec, bip32, script
from ..networks import NETWORKS
from .errors import DescriptorError
from .base import DescriptorBase
from .miniscript import Miniscript
from .arguments import Key


class Descriptor(DescriptorBase):
    def __init__(self, miniscript=None, sh=False, wsh=True, key=None, wpkh=True):
        if key is None and miniscript is None:
            raise DescriptorError("Provide either miniscript or a key")
        if miniscript is not None:
            # will raise if can't verify
            miniscript.verify()
            if miniscript.type != "B":
                raise DescriptorError("Top level miniscript should be 'B'")
            branches = [k.branches for k in miniscript.keys]
            branch = None
            for b in branches:
                if b is not None:
                    if branch is None:
                        branch = b
                    else:
                        if len(branch) != len(b):
                            raise DescriptorError(
                                "All branches should have the same length"
                            )
        self.sh = sh
        self.wsh = wsh
        self.key = key
        self.miniscript = miniscript
        self.wpkh = wpkh

    @property
    def script_len(self):
        if self.miniscript:
            return len(self.miniscript)
        if self.wpkh:
            return 22 # 00 <20:pkh>
        return 25 # OP_DUP OP_HASH160 <20:pkh> OP_EQUALVERIFY OP_CHECKSIG

    @property
    def num_branches(self):
        return max([k.num_branches for k in self.keys])

    def branch(self, branch_index=None):
        if self.miniscript:
            return type(self)(
                self.miniscript.branch(branch_index),
                self.sh,
                self.wsh,
                None,
                self.wpkh,
            )
        else:
            return type(self)(
                None, self.sh, self.wsh, self.key.branch(branch_index), self.wpkh
            )


    @property
    def is_wildcard(self):
        return any([key.is_wildcard for key in self.keys])

    @property
    def is_wrapped(self):
        return self.sh and self.is_segwit

    @property
    def is_legacy(self):
        return not self.is_segwit

    @property
    def is_segwit(self):
        return (self.wsh and self.miniscript) or (self.wpkh and self.key)

    @property
    def is_pkh(self):
        return self.key is not None

    @property
    def is_basic_multisig(self):
        return self.miniscript and self.miniscript.NAME in ["multi", "sortedmulti"]

    @property
    def is_sorted(self):
        return self.is_basic_multisig and self.miniscript.NAME == "sortedmulti"

    def scriptpubkey_type(self):
        if self.sh:
            return "p2sh"
        if self.is_pkh:
            if self.is_legacy:
                return "p2pkh"
            if self.is_segwit:
                return "p2wpkh"
        else:
            return "p2wsh"

    @property
    def brief_policy(self):
        if self.key:
            return "single key"
        if self.is_basic_multisig:
            return (
                str(self.miniscript.args[0])
                + " of "
                + str(len(self.keys))
                + " multisig"
                + (" (sorted)" if self.is_sorted else "")
            )
        return "miniscript"

    @property
    def full_policy(self):
        if self.key or self.is_basic_multisig:
            return self.brief_policy
        s = str(self.miniscript)
        for i, k in enumerate(self.keys):
            s = s.replace(str(k), chr(65 + i))
        return s

    def derive(self, idx, branch_index=None):
        if self.miniscript:
            return type(self)(
                self.miniscript.derive(idx, branch_index),
                self.sh,
                self.wsh,
                None,
                self.wpkh,
            )
        else:
            return type(self)(
                None, self.sh, self.wsh, self.key.derive(idx, branch_index), self.wpkh
            )

    def owns(self, psbt_scope):
        """Checks if psbt input or output belongs to this descriptor"""
        # we can't check if we don't know script_pubkey
        if psbt_scope.script_pubkey is None:
            return False
        # quick check of script_pubkey type
        if psbt_scope.script_pubkey.script_type() != self.scriptpubkey_type():
            return False
        for pub, der in psbt_scope.bip32_derivations.items():
            # check of the fingerprints
            for k in self.keys:
                if not k.is_extended:
                    continue
                res = k.check_derivation(der)
                if res:
                    idx, branch_idx = res
                    sc = self.derive(idx, branch_index=branch_idx).script_pubkey()
                    # if derivation is found but scriptpubkey doesn't match - fail
                    return (sc == psbt_scope.script_pubkey)
        return False

    def check_derivation(self, derivation_path):
        for k in self.keys:
            # returns a tuple branch_idx, idx
            der = k.check_derivation(derivation_path)
            if der is not None:
                return der
        return None

    def witness_script(self):
        if self.wsh and self.miniscript is not None:
            return script.Script(self.miniscript.compile())

    def redeem_script(self):
        if not self.sh:
            return None
        if self.miniscript:
            if not self.wsh:
                return script.Script(self.miniscript.compile())
            else:
                return script.p2wsh(script.Script(self.miniscript.compile()))
        else:
            return script.p2wpkh(self.key)

    def script_pubkey(self):
        # covers sh-wpkh, sh and sh-wsh
        if self.sh:
            return script.p2sh(self.redeem_script())
        if self.wsh:
            return script.p2wsh(self.witness_script())
        if self.miniscript:
            return script.Script(self.miniscript.compile())
        if self.wpkh:
            return script.p2wpkh(self.key)
        return script.p2pkh(self.key)

    def address(self, network=NETWORKS["main"]):
        return self.script_pubkey().address(network)

    @property
    def keys(self):
        if self.key:
            return [self.key]
        return self.miniscript.keys

    @classmethod
    def from_string(cls, desc):
        s = io.BytesIO(desc.encode())
        res = cls.read_from(s)
        left = s.read()
        if len(left) > 0 and not left.startswith(b"#"):
            raise DescriptorError("Unexpected characters after descriptor: %r" % left)
        return res

    @classmethod
    def read_from(cls, s):
        # starts with sh(wsh()), sh() or wsh()
        start = s.read(7)
        sh = False
        wsh = False
        wpkh = False
        is_miniscript = True
        if start.startswith(b"sh(wsh("):
            sh = True
            wsh = True
        elif start.startswith(b"wsh("):
            sh = False
            wsh = True
            s.seek(-3, 1)
        elif start.startswith(b"sh(wpkh"):
            is_miniscript = False
            sh = True
            wpkh = True
            assert s.read(1) == b"("
        elif start.startswith(b"wpkh("):
            is_miniscript = False
            wpkh = True
            s.seek(-2, 1)
        elif start.startswith(b"pkh("):
            is_miniscript = False
            s.seek(-3, 1)
        elif start.startswith(b"sh("):
            sh = True
            wsh = False
            s.seek(-4, 1)
        else:
            raise ValueError("Invalid descriptor")
        if is_miniscript:
            miniscript = Miniscript.read_from(s)
            key = None
            nbrackets = int(sh) + int(wsh)
        else:
            miniscript = None
            key = Key.read_from(s)
            nbrackets = 1 + int(sh)
        end = s.read(nbrackets)
        if end != b")" * nbrackets:
            raise ValueError("Invalid descriptor")
        return cls(miniscript, sh=sh, wsh=wsh, key=key, wpkh=wpkh)

    def to_string(self):
        if self.miniscript is not None:
            res = str(self.miniscript)
            if self.wsh:
                res = "wsh(%s)" % res
        else:
            if self.wpkh:
                res = "wpkh(%s)" % self.key
            else:
                res = "pkh(%s)" % self.key
        if self.sh:
            res = "sh(%s)" % res
        return res
