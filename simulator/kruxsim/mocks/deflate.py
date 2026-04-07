import sys
from unittest import mock
import zlib
from io import BytesIO

# Must match DEFLATEIO_MAX_DECOMPRESSED_SIZE in moddeflate.c
MAX_DECOMPRESSED_SIZE = 100 * 1024  # 100 KB


class DeflateIO:
    def __init__(self, stream) -> None:
        self.stream = stream
        self.data = stream.read()
        self._total_out = 0

    def read(self, size=-1):
        if not hasattr(self, "_decompressed"):
            self._decompressed = BytesIO(zlib.decompress(self.data, wbits=-10))
        chunk = self._decompressed.read() if size == -1 else self._decompressed.read(size)
        if chunk:
            self._total_out += len(chunk)
            if self._total_out > MAX_DECOMPRESSED_SIZE:
                raise ValueError("decompressed data exceeds size limit")
        return chunk

    def write(self, input_data):
        compressor = zlib.compressobj(wbits=-10)
        compressed_data = compressor.compress(input_data)
        compressed_data += compressor.flush()
        self.stream.seek(0)  # Ensure we overwrite the stream from the beginning
        self.stream.write(compressed_data)
        self.stream.truncate()  # Remove any remaining part of the old data

    def __enter__(self):
        # Return the instance itself when entering the context
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Handle cleanup here if necessary
        pass


if "deflate" not in sys.modules:
    sys.modules["deflate"] = mock.MagicMock(DeflateIO=DeflateIO)
