try:
    import uio as io
except ImportError:
    import io


def read_until(s, chars=b",)(#"):
    res = b""
    chunk = b""
    char = None
    while True:
        chunk = s.read(1)
        if len(chunk) == 0:
            return res, None
        if chunk in chars:
            return res, chunk
        res += chunk
    return res, None


class DescriptorBase:
    def __repr__(self):
        return type(self).__name__ + "(%s)" % str(self)

    @classmethod
    def read_from(cls, stream):
        raise NotImplementedError(
            "%s doesn't implement reading from stream" % type(cls)
        )

    @classmethod
    def parse(cls, b):
        stream = io.BytesIO(b)
        return cls.read_from(stream)

    @classmethod
    def from_string(cls, s):
        return cls.parse(s.encode())

    def __str__(self):
        return self.to_string()
