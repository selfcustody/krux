"""Base classes"""
try:
    import uio as io
except ImportError:
    import io
from binascii import hexlify, unhexlify


class EmbitError(Exception):
    """Generic Embit error"""

    pass


class EmbitBase:
    @classmethod
    def read_from(cls, stream, *args, **kwargs):
        """All classes should be readable from stream"""
        raise NotImplementedError(
            "%s doesn't implement reading from stream" % type(cls).__name__
        )

    @classmethod
    def parse(cls, s, *args, **kwargs):
        """Parses a string or a byte sequence"""
        if isinstance(s, str):
            s = s.encode()
        stream = io.BytesIO(s)
        res = cls.read_from(stream, *args, **kwargs)
        if len(stream.read(1)) > 0:
            raise EmbitError("Unexpected extra bytes")
        return res

    def write_to(self, stream, *args, **kwargs):
        """All classes should be writable to stream"""
        raise NotImplementedError(
            "%s doesn't implement writing to stream" % type(self).__name__
        )

    def serialize(self, *args, **kwargs):
        stream = io.BytesIO()
        self.write_to(stream, *args, **kwargs)
        return stream.getvalue()

    def to_string(self, *args, **kwargs):
        """Default string representation is hex of serialized instance or base58 if available"""
        if hasattr(self, "to_base58"):
            return self.to_base58(*args, **kwargs)
        return hexlify(self.serialize(*args, **kwargs)).decode()

    @classmethod
    def from_string(cls, s, *args, **kwargs):
        """Default string representation is hex of serialized instance or base58 if availabe"""
        if hasattr(cls, "from_base58"):
            return cls.from_base58(s, *args, **kwargs)
        return cls.parse(unhexlify(s))

    def __str__(self):
        """to_string() can accept kwargs with defaults so str() should work"""
        return self.to_string()

    def __repr__(self):
        try:
            return type(self).__name__ + "(%s)" % str(self)
        except:
            return type(self).__name__ + "()"

    def __eq__(self, other):
        return self.serialize() == other.serialize()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.serialize())


class EmbitKey(EmbitBase):
    def sec(self):
        """Any EmbitKey should implement sec() method that returns sec-serialized public key"""
        raise NotImplementedError(
            "%s doesn't implement sec() method" % type(self).__name__
        )

    @property
    def is_private(self) -> bool:
        """Any EmbitKey should implement is_private property"""
        raise NotImplementedError(
            "%s doesn't implement is_private property" % type(self).__name__
        )

    def __lt__(self, other):
        # for lexagraphic ordering
        return self.sec() < other.sec()

    def __gt__(self, other):
        # for lexagraphic ordering
        return self.sec() > other.sec()

    def __hash__(self):
        return hash(self.serialize())
