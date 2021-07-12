from binascii import hexlify, unhexlify
try:
    import uio as io
except ImportError:
    import io
from .. import hashes, compact, ec, bip32, script
from ..networks import NETWORKS
from .errors import MiniscriptError
from .base import DescriptorBase
from .arguments import *


class Miniscript(DescriptorBase):
    def __init__(self, *args):
        self.args = args

    def compile(self):
        return self.inner_compile()

    def verify(self):
        for arg in self.args:
            if isinstance(arg, Miniscript):
                arg.verify()

    @property
    def keys(self):
        return sum(
            [arg.keys for arg in self.args if isinstance(arg, Miniscript)],
            [k for k in self.args if isinstance(k, Key) or isinstance(k, KeyHash)],
        )

    def derive(self, idx, branch_index=None):
        args = [
            arg.derive(idx, branch_index) if hasattr(arg, "derive") else arg
            for arg in self.args
        ]
        return type(self)(*args)

    def branch(self, branch_index):
        args = [
            arg.branch(branch_index) if hasattr(arg, "branch") else arg
            for arg in self.args
        ]
        return type(self)(*args)

    @property
    def properties(self):
        return self.PROPS

    @property
    def type(self):
        return self.TYPE

    @classmethod
    def read_from(cls, s):
        op, char = read_until(s, b"(")
        op = op.decode()
        wrappers = ""
        if ":" in op:
            wrappers, op = op.split(":")
        if char != b"(":
            raise MiniscriptError("Missing operator")
        if op not in OPERATOR_NAMES:
            raise MiniscriptError("Unknown operator '%s'" % op)
        # number of arguments, classes of arguments, compile function, type, validity checker
        MiniscriptCls = OPERATORS[OPERATOR_NAMES.index(op)]
        args = MiniscriptCls.read_arguments(s)
        miniscript = MiniscriptCls(*args)
        for w in reversed(wrappers):
            if w not in WRAPPER_NAMES:
                raise MiniscriptError("Unknown wrapper")
            WrapperCls = WRAPPERS[WRAPPER_NAMES.index(w)]
            miniscript = WrapperCls(miniscript)
        return miniscript

    @classmethod
    def read_arguments(cls, s):
        args = []
        if cls.NARGS is None:
            if type(cls.ARGCLS) == tuple:
                firstcls, nextcls = cls.ARGCLS
            else:
                firstcls, nextcls = cls.ARGCLS, cls.ARGCLS
            args.append(firstcls.read_from(s))
            while True:
                char = s.read(1)
                if char == b",":
                    args.append(nextcls.read_from(s))
                elif char == b")":
                    break
                else:
                    raise MiniscriptError(
                        "Expected , or ), got: %s" % (char + s.read())
                    )
        else:
            for i in range(cls.NARGS):
                args.append(cls.ARGCLS.read_from(s))
                if i < cls.NARGS - 1:
                    char = s.read(1)
                    if char != b",":
                        raise MiniscriptError("Missing arguments, %s" % char)
            char = s.read(1)
            if char != b")":
                raise MiniscriptError("Expected ) got %s" % (char + s.read()))
        return args

    def __str__(self):
        return type(self).NAME + "(" + ",".join([str(arg) for arg in self.args]) + ")"

    def __len__(self):
        """Length of the compiled script, override this if you know the length"""
        return len(self.compile())

    def len_args(self):
        return sum([len(arg) for arg in self.args])

########### Known fragments (miniscript operators) ##############


class OneArg(Miniscript):
    NARGS = 1
    # small handy functions
    @property
    def arg(self):
        return self.args[0]

    @property
    def carg(self):
        return self.arg.compile()


class PkK(OneArg):
    # <key>
    NAME = "pk_k"
    ARGCLS = Key
    TYPE = "K"
    PROPS = "ondu"

    def inner_compile(self):
        return self.carg

    def __len__(self):
        return self.len_args()


class PkH(OneArg):
    # DUP HASH160 <HASH160(key)> EQUALVERIFY
    NAME = "pk_h"
    ARGCLS = KeyHash
    TYPE = "K"
    PROPS = "ndu"

    def inner_compile(self):
        return b"\x76\xa9" + self.carg + b"\x88"

    def __len__(self):
        return self.len_args() + 3

class Older(OneArg):
    # <n> CHECKSEQUENCEVERIFY
    NAME = "older"
    ARGCLS = Number
    TYPE = "B"
    PROPS = "z"

    def inner_compile(self):
        return self.carg + b"\xb2"

    def verify(self):
        super().verify()
        if (self.arg.num < 1) or (self.arg.num >= 0x80000000):
            raise MiniscriptError(
                "%s should have an argument in range [1, 0x80000000)" % self.NAME
            )

    def __len__(self):
        return self.len_args() + 1

class After(Older):
    # <n> CHECKLOCKTIMEVERIFY
    NAME = "after"

    def inner_compile(self):
        return self.carg + b"\xb1"


class Sha256(OneArg):
    # SIZE <32> EQUALVERIFY SHA256 <h> EQUAL
    NAME = "sha256"
    ARGCLS = Raw32
    TYPE = "B"
    PROPS = "ondu"

    def inner_compile(self):
        return b"\x82" + Number(32).compile() + b"\x88\xa8" + self.carg + b"\x87"

    def __len__(self):
        return self.len_args() + 6

class Hash256(Sha256):
    # SIZE <32> EQUALVERIFY HASH256 <h> EQUAL
    NAME = "hash256"

    def inner_compile(self):
        return b"\x82" + Number(32).compile() + b"\x88\xaa" + self.carg + b"\x87"


class Ripemd160(Sha256):
    # SIZE <32> EQUALVERIFY RIPEMD160 <h> EQUAL
    NAME = "ripemd160"
    ARGCLS = Raw20

    def inner_compile(self):
        return b"\x82" + Number(32).compile() + b"\x88\xa6" + self.carg + b"\x87"


class Hash160(Ripemd160):
    # SIZE <32> EQUALVERIFY HASH160 <h> EQUAL
    NAME = "hash160"

    def inner_compile(self):
        return b"\x82" + Number(32).compile() + b"\x88\xa9" + self.carg + b"\x87"


class AndOr(Miniscript):
    # [X] NOTIF [Z] ELSE [Y] ENDIF
    NAME = "andor"
    NARGS = 3
    ARGCLS = Miniscript

    @property
    def type(self):
        # type: same as Y/Z
        return self.args[1].type

    def verify(self):
        # requires: X is Bdu; Y and Z are both B, K, or V
        super().verify()
        if self.args[0].type != "B":
            raise MiniscriptError("andor: X should be 'B'")
        px = self.args[0].properties
        if "d" not in px and "u" not in px:
            raise MiniscriptError("andor: X should be 'du'")
        if self.args[1].type != self.args[2].type:
            raise MiniscriptError("andor: Y and Z should have the same types")
        if self.args[1].type not in "BKV":
            raise MiniscriptError("andor: Y and Z should be B K or V")

    @property
    def properties(self):
        # props: z=zXzYzZ; o=zXoYoZ or oXzYzZ; u=uYuZ; d=dZ
        props = ""
        px, py, pz = [arg.properties for arg in self.args]
        if "z" in px and "z" in py and "z" in pz:
            props += "z"
        if ("z" in px and "o" in py and "o" in pz) or (
            "o" in px and "z" in py and "z" in pz
        ):
            props += "o"
        if "u" in py and "u" in pz:
            props += "u"
        if "d" in pz:
            props += "d"
        return props

    def inner_compile(self):
        return (
            self.args[0].compile()
            + b"\x64"
            + self.args[2].compile()
            + b"\x67"
            + self.args[1].compile()
            + b"\x68"
        )

    def __len__(self):
        return self.len_args() + 3

class AndV(Miniscript):
    # [X] [Y]
    NAME = "and_v"
    NARGS = 2
    ARGCLS = Miniscript

    def inner_compile(self):
        return self.args[0].compile() + self.args[1].compile()

    def __len__(self):
        return self.len_args()

    def verify(self):
        # X is V; Y is B, K, or V
        super().verify()
        if self.args[0].type != "V":
            raise MiniscriptError("and_v: X should be 'V'")
        if self.args[1].type not in "BKV":
            raise MiniscriptError("and_v: Y should be B K or V")

    @property
    def type(self):
        # same as Y
        return self.args[1].type

    @property
    def properties(self):
        # z=zXzY; o=zXoY or zYoX; n=nX or zXnY; u=uY
        px, py = [arg.properties for arg in self.args]
        props = ""
        if "z" in px and "z" in py:
            props += "z"
        if ("z" in px and "o" in py) or ("z" in py and "o" in px):
            props += "o"
        if "n" in px or ("z" in px and "n" in py):
            props += "n"
        if "u" in py:
            props += "u"
        return props


class AndB(Miniscript):
    # [X] [Y] BOOLAND
    NAME = "and_b"
    NARGS = 2
    ARGCLS = Miniscript
    TYPE = "B"

    def inner_compile(self):
        return self.args[0].compile() + self.args[1].compile() + b"\x9a"

    def __len__(self):
        return self.len_args() + 1

    def verify(self):
        # X is B; Y is W
        super().verify()
        if self.args[0].type != "B":
            raise MiniscriptError("and_b: X should be B")
        if self.args[1].type != "W":
            raise MiniscriptError("and_b: Y should be W")

    @property
    def properties(self):
        # z=zXzY; o=zXoY or zYoX; n=nX or zXnY; d=dXdY; u
        px, py = [arg.properties for arg in self.args]
        props = ""
        if "z" in px and "z" in py:
            props += "z"
        if ("z" in px and "o" in py) or ("z" in py and "o" in px):
            props += "o"
        if "n" in px or ("z" in px and "n" in py):
            props += "n"
        if "d" in px and "d" in py:
            props += "d"
        props += "u"
        return props


class AndN(Miniscript):
    # [X] NOTIF 0 ELSE [Y] ENDIF
    # andor(X,Y,0)
    NAME = "and_n"
    NARGS = 2
    ARGCLS = Miniscript

    def inner_compile(self):
        return (
            self.args[0].compile()
            + b"\x64"
            + Number(0).compile()
            + b"\x67"
            + self.args[1].compile()
            + b"\x68"
        )

    def __len__(self):
        return self.len_args() + 4

    @property
    def type(self):
        # type: same as Y/Z
        return self.args[1].type

    def verify(self):
        # requires: X is Bdu; Y and Z are both B, K, or V
        super().verify()
        if self.args[0].type != "B":
            raise MiniscriptError("and_n: X should be 'B'")
        px = self.args[0].properties
        if "d" not in px and "u" not in px:
            raise MiniscriptError("and_n: X should be 'du'")
        if self.args[1].type != "B":
            raise MiniscriptError("and_n: Y should be B")

    @property
    def properties(self):
        # props: z=zXzYzZ; o=zXoYoZ or oXzYzZ; u=uYuZ; d=dZ
        props = ""
        px, py = [arg.properties for arg in self.args]
        pz = "zud"
        if "z" in px and "z" in py and "z" in pz:
            props += "z"
        if ("z" in px and "o" in py and "o" in pz) or (
            "o" in px and "z" in py and "z" in pz
        ):
            props += "o"
        if "u" in py and "u" in pz:
            props += "u"
        if "d" in pz:
            props += "d"
        return props


class OrB(Miniscript):
    # [X] [Z] BOOLOR
    NAME = "or_b"
    NARGS = 2
    ARGCLS = Miniscript
    TYPE = "B"

    def inner_compile(self):
        return self.args[0].compile() + self.args[1].compile() + b"\x9b"

    def __len__(self):
        return self.len_args() + 1

    def verify(self):
        # X is Bd; Z is Wd
        super().verify()
        if self.args[0].type != "B":
            raise MiniscriptError("or_b: X should be B")
        if "d" not in self.args[0].properties:
            raise MiniscriptError("or_b: X should be d")
        if self.args[1].type != "W":
            raise MiniscriptError("or_b: Z should be W")
        if "d" not in self.args[1].properties:
            raise MiniscriptError("or_b: Z should be d")

    @property
    def properties(self):
        # z=zXzZ; o=zXoZ or zZoX; d; u
        props = ""
        px, pz = [arg.properties for arg in self.args]
        if "z" in px and "z" in pz:
            props += "z"
        if ("z" in px and "o" in pz) or ("z" in pz and "o" in px):
            props += "o"
        props += "du"
        return props


class OrC(Miniscript):
    # [X] NOTIF [Z] ENDIF
    NAME = "or_c"
    NARGS = 2
    ARGCLS = Miniscript
    TYPE = "V"

    def inner_compile(self):
        return self.args[0].compile() + b"\x64" + self.args[1].compile() + b"\x68"

    def __len__(self):
        return self.len_args() + 2

    def verify(self):
        # X is Bdu; Z is V
        super().verify()
        if self.args[0].type != "B":
            raise MiniscriptError("or_c: X should be B")
        if self.args[1].type != "V":
            raise MiniscriptError("or_c: Z should be V")
        px = self.args[0].properties
        if "d" not in px or "u" not in px:
            raise MiniscriptError("or_c: X should be du")

    @property
    def properties(self):
        # z=zXzZ; o=oXzZ
        props = ""
        px, pz = [arg.properties for arg in self.args]
        if "z" in px and "z" in pz:
            props += "z"
        if "o" in px and "z" in pz:
            props += "o"
        return props


class OrD(Miniscript):
    # [X] IFDUP NOTIF [Z] ENDIF
    NAME = "or_d"
    NARGS = 2
    ARGCLS = Miniscript
    TYPE = "B"

    def inner_compile(self):
        return self.args[0].compile() + b"\x73\x64" + self.args[1].compile() + b"\x68"

    def __len__(self):
        return self.len_args() + 3

    def verify(self):
        # X is Bdu; Z is B
        super().verify()
        if self.args[0].type != "B":
            raise MiniscriptError("or_d: X should be B")
        if self.args[1].type != "B":
            raise MiniscriptError("or_d: Z should be B")
        px = self.args[0].properties
        if "d" not in px or "u" not in px:
            raise MiniscriptError("or_d: X should be du")

    @property
    def properties(self):
        # z=zXzZ; o=oXzZ; d=dZ; u=uZ
        props = ""
        px, pz = [arg.properties for arg in self.args]
        if "z" in px and "z" in pz:
            props += "z"
        if "o" in px and "z" in pz:
            props += "o"
        if "d" in pz:
            props += "d"
        if "u" in pz:
            props += "u"
        return props


class OrI(Miniscript):
    # IF [X] ELSE [Z] ENDIF
    NAME = "or_i"
    NARGS = 2
    ARGCLS = Miniscript

    def inner_compile(self):
        return (
            b"\x63"
            + self.args[0].compile()
            + b"\x67"
            + self.args[1].compile()
            + b"\x68"
        )

    def __len__(self):
        return self.len_args() + 3

    def verify(self):
        # both are B, K, or V
        super().verify()
        if self.args[0].type != self.args[1].type:
            raise MiniscriptError("or_i: X and Z should be the same type")
        if self.args[0].type not in "BKV":
            raise MiniscriptError("or_i: X and Z should be B K or V")

    @property
    def type(self):
        return self.args[0].type

    @property
    def properties(self):
        # o=zXzZ; u=uXuZ; d=dX or dZ
        props = ""
        px, pz = [arg.properties for arg in self.args]
        if "z" in px and "z" in pz:
            props += "o"
        if "u" in px and "u" in pz:
            props += "u"
        if "d" in px or "d" in pz:
            props += "d"
        return props


class Thresh(Miniscript):
    # [X1] [X2] ADD ... [Xn] ADD ... <k> EQUAL
    NAME = "thresh"
    NARGS = None
    ARGCLS = (Number, Miniscript)
    TYPE = "B"

    def inner_compile(self):
        return (
            self.args[1].compile()
            + b"\x93".join([arg.compile() for arg in self.args[2:]])
            + b"\x93"
            + self.args[0].compile()
            + b"\x87"
        )

    def __len__(self):
        return self.len_args() + len(self.args) - 1

    def verify(self):
        # 1 <= k <= n; X1 is Bdu; others are Wdu
        super().verify()
        if self.args[0].num < 1 or self.args[0].num >= len(self.args):
            raise MiniscriptError(
                "thresh: Invalid k! Should be 1 <= k <= %d, got %d"
                % (len(self.args) - 1, self.args[0].num)
            )
        if self.args[1].type != "B":
            raise MiniscriptError("thresh: X1 should be B")
        px = self.args[1].properties
        if "d" not in px or "u" not in px:
            raise MiniscriptError("thresh: X1 should be du")
        for i, arg in enumerate(self.args[2:]):
            if arg.type != "W":
                raise MiniscriptError("thresh: X%d should be W" % (i + 1))
            p = arg.properties
            if "d" not in p or "u" not in p:
                raise MiniscriptError("thresh: X%d should be du" % (i + 1))

    def properties(self):
        # z=all are z; o=all are z except one is o; d; u
        props = ""
        parr = [arg.properties for arg in self.args[1:]]
        zarr = ["z" for p in parr if "z" in p]
        if len(zarr) == len(parr):
            props += "z"
        noz = [p for p in parr if "z" not in p]
        if len(noz) == 1 and "o" in noz[0]:
            props += "o"
        props += "du"
        return props


class Multi(Miniscript):
    # <k> <key1> ... <keyn> <n> CHECKMULTISIG
    NAME = "multi"
    NARGS = None
    ARGCLS = (Number, Key)
    TYPE = "B"
    PROPS = "ndu"

    def inner_compile(self):
        return (
            b"".join([arg.compile() for arg in self.args])
            + Number(len(self.args) - 1).compile()
            + b"\xae"
        )

    def __len__(self):
        return self.len_args() + 2

    def verify(self):
        super().verify()
        if self.args[0].num < 1 or self.args[0].num > (len(self.args) - 1):
            raise MiniscriptError(
                "multi: 1 <= k <= %d, got %d" % ((len(self.args) - 1), self.args[0].num)
            )


class Sortedmulti(Multi):
    # <k> <key1> ... <keyn> <n> CHECKMULTISIG
    NAME = "sortedmulti"

    def inner_compile(self):
        return (
            self.args[0].compile()
            + b"".join(sorted([arg.compile() for arg in self.args[1:]]))
            + Number(len(self.args) - 1).compile()
            + b"\xae"
        )


class Pk(OneArg):
    # <key> CHECKSIG
    NAME = "pk"
    ARGCLS = Key
    TYPE = "B"
    PROPS = "ondu"

    def inner_compile(self):
        return self.carg + b"\xac"

    def __len__(self):
        return self.len_args() + 1


class Pkh(OneArg):
    # DUP HASH160 <HASH160(key)> EQUALVERIFY CHECKSIG
    NAME = "pkh"
    ARGCLS = KeyHash
    TYPE = "B"
    PROPS = "ndu"

    def inner_compile(self):
        return b"\x76\xa9" + self.carg + b"\x88\xac"

    def __len__(self):
        return self.len_args() + 4

    # TODO: 0, 1 - they are without brackets, so it should be different...


OPERATORS = [
    PkK,
    PkH,
    Older,
    After,
    Sha256,
    Hash256,
    Ripemd160,
    Hash160,
    AndOr,
    AndV,
    AndB,
    AndN,
    OrB,
    OrC,
    OrD,
    OrI,
    Thresh,
    Multi,
    Sortedmulti,
    Pk,
    Pkh,
]
OPERATOR_NAMES = [cls.NAME for cls in OPERATORS]


class Wrapper(OneArg):
    ARGCLS = Miniscript

    @property
    def op(self):
        return type(self).__name__.lower()

    def __str__(self):
        # more wrappers follow
        if isinstance(self.arg, Wrapper):
            return self.op + str(self.arg)
        # we are the last wrapper
        return self.op + ":" + str(self.arg)


class A(Wrapper):
    # TOALTSTACK [X] FROMALTSTACK
    TYPE = "W"

    def inner_compile(self):
        return b"\x6b" + self.carg + b"\x6c"

    def __len__(self):
        return len(self.arg) + 2

    def verify(self):
        super().verify()
        if self.arg.type != "B":
            raise MiniscriptError("a: X should be B")

    @property
    def properties(self):
        props = ""
        px = self.arg.properties
        if "d" in px:
            props += "d"
        if "u" in px:
            props += "u"
        return props


class S(Wrapper):
    # SWAP [X]
    TYPE = "W"

    def inner_compile(self):
        return b"\x7c" + self.carg

    def __len__(self):
        return len(self.arg) + 1

    def verify(self):
        super().verify()
        if self.arg.type != "B":
            raise MiniscriptError("s: X should be B")
        if "o" not in self.arg.properties:
            raise MiniscriptError("s: X should be o")

    @property
    def properties(self):
        props = ""
        px = self.arg.properties
        if "d" in px:
            props += "d"
        if "u" in px:
            props += "u"
        return props


class C(Wrapper):
    # [X] CHECKSIG
    TYPE = "B"

    def inner_compile(self):
        return self.carg + b"\xac"

    def __len__(self):
        return len(self.arg) + 1

    def verify(self):
        super().verify()
        if self.arg.type != "K":
            raise MiniscriptError("c: X should be K")

    @property
    def properties(self):
        props = ""
        px = self.arg.properties
        for p in ["o", "n", "d"]:
            if p in px:
                props += p
        props += "u"
        return props


class T(Wrapper):
    # [X] 1
    TYPE = "B"

    def inner_compile(self):
        return self.carg + Number(1).compile()

    def __len__(self):
        return len(self.arg) + 1

    @property
    def properties(self):
        # z=zXzY; o=zXoY or zYoX; n=nX or zXnY; u=uY
        px = self.arg.properties
        py = "zu"
        props = ""
        if "z" in px and "z" in py:
            props += "z"
        if ("z" in px and "o" in py) or ("z" in py and "o" in px):
            props += "o"
        if "n" in px or ("z" in px and "n" in py):
            props += "n"
        if "u" in py:
            props += "u"
        return props


class D(Wrapper):
    # DUP IF [X] ENDIF
    TYPE = "B"

    def inner_compile(self):
        return b"\x76\x63" + self.carg + b"\x68"

    def __len__(self):
        return len(self.arg) + 3

    def verify(self):
        super().verify()
        if self.arg.type != "V":
            raise MiniscriptError("d: X should be V")
        if "z" not in self.arg.properties:
            raise MiniscriptError("d: X should be z")

    @property
    def properties(self):
        props = "ndu"
        px = self.arg.properties
        if "z" in px:
            props += "o"
        return props


class V(Wrapper):
    # [X] VERIFY (or VERIFY version of last opcode in [X])
    TYPE = "V"

    def inner_compile(self):
        """Checks last check code and makes it verify"""
        if self.carg[-1] in [0xAC, 0xAE, 0x9C, 0x87]:
            return self.carg[:-1] + bytes([self.carg[-1] + 1])
        return self.carg + b"\x69"

    def verify(self):
        super().verify()
        if self.arg.type != "B":
            raise MiniscriptError("v: X should be B")

    @property
    def properties(self):
        props = ""
        px = self.arg.properties
        for p in ["z", "o", "n"]:
            if p in px:
                props += p
        return props


class J(Wrapper):
    # SIZE 0NOTEQUAL IF [X] ENDIF
    TYPE = "B"

    def inner_compile(self):
        return b"\x82\x92\x63" + self.carg + b"\x68"

    def verify(self):
        super().verify()
        if self.arg.type != "B":
            raise MiniscriptError("j: X should be B")
        if "n" not in self.arg.properties:
            raise MiniscriptError("j: X should be n")

    @property
    def properties(self):
        props = "nd"
        px = self.arg.properties
        for p in ["o", "u"]:
            if p in px:
                props += p
        return props


class N(Wrapper):
    # [X] 0NOTEQUAL
    TYPE = "B"

    def inner_compile(self):
        return self.carg + b"\x92"

    def __len__(self):
        return len(self.arg) + 1

    def verify(self):
        super().verify()
        if self.arg.type != "B":
            raise MiniscriptError("n: X should be B")

    @property
    def properties(self):
        props = "u"
        px = self.arg.properties
        for p in ["z", "o", "n", "d"]:
            if p in px:
                props += p
        return props


class L(Wrapper):
    # IF 0 ELSE [X] ENDIF
    TYPE = "B"

    def inner_compile(self):
        return b"\x63" + Number(0).compile() + b"\x67" + self.carg + b"\x68"

    def __len__(self):
        return len(self.arg) + 4

    def verify(self):
        # both are B, K, or V
        super().verify()
        if self.arg.type != "B":
            raise MiniscriptError("or_i: X and Z should be the same type")

    @property
    def properties(self):
        # o=zXzZ; u=uXuZ; d=dX or dZ
        props = "d"
        pz = self.arg.properties
        if "z" in pz:
            props += "o"
        if "u" in pz:
            props += "u"
        return props


class U(L):
    # IF [X] ELSE 0 ENDIF
    def inner_compile(self):
        return b"\x63" + self.carg + b"\x67" + Number(0).compile() + b"\x68"

    def __len__(self):
        return len(self.arg) + 4


WRAPPERS = [A, S, C, T, D, V, J, N, L, U]
WRAPPER_NAMES = [w.__name__.lower() for w in WRAPPERS]
