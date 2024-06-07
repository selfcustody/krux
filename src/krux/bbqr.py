# The MIT License (MIT)

# Copyright (c) 2021-2024 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# This code an adaptation of Coinkite's BBQr python implementation for Krux environment
# https://github.com/coinkite/BBQr

# BBQR
# Human names
FILETYPE_NAMES = {
    # PSBT and unicode text supported for now
    "P": "PSBT",
    # "T": "Transaction",
    # "J": "JSON",
    # "C": "CBOR",
    "U": "Unicode Text",
    # "X": "Executable",
    # "B": "Binary",
}

# Codes for PSBT vs. TXN and so on
KNOWN_FILETYPES = set(FILETYPE_NAMES.keys())

BBQR_ALWAYS_COMPRESS_THRESHOLD = 5000  # bytes

B32CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
assert len(B32CHARS) == 32


class BBQrCode:
    """A BBQr code, containing the data, encoding, and file type"""

    def __init__(self, payload, encoding=None, file_type=None):
        """Initializes the BBQr code with the given data, encoding, and file type"""

        if encoding not in "H2Z":
            raise ValueError("Invalid BBQr encoding")
        if file_type not in KNOWN_FILETYPES:
            raise ValueError("Invalid BBQr file type")
        self.payload = payload
        self.encoding = encoding
        self.file_type = file_type


def parse_bbqr(data):
    """
    Parses the QR as a BBQR part, extracting the part's content,
    encoding, file format, index, and total
    """
    try:
        encoding = data[2]
        if encoding not in "H2Z":
            raise ValueError("Invalid encoding")
        file_type = data[3]
        if file_type not in KNOWN_FILETYPES:
            raise ValueError("Invalid file type")
        part_total = int(data[4:6], 36)
        part_index = int(data[6:8], 36)
        if part_index >= part_total:
            raise ValueError("Invalid part index")
    except:
        raise ValueError("Invalid BBQR format")
    return data[8:], part_index, part_total


def deflate_compress(data):
    """Compresses the given data using deflate module"""
    try:
        import deflate
        from io import BytesIO

        stream = BytesIO()
        with deflate.DeflateIO(stream) as d:
            d.write(data)
        return stream.getvalue()
    except:
        raise ValueError("Error compressing BBQR")


def deflate_decompress(data):
    """Decompresses the given data using deflate module"""
    try:
        import deflate
        from io import BytesIO

        with deflate.DeflateIO(BytesIO(data)) as d:
            return d.read()
    except:
        raise ValueError("Error decompressing BBQR")


def decode_bbqr(parts, encoding, file_type):
    """Decodes the given data as BBQR, returning the decoded data"""

    if encoding not in "H2Z":
        raise ValueError("Invalid BBQr encoding")
    if file_type not in KNOWN_FILETYPES:
        raise ValueError("Invalid BBQr file type")

    if encoding == "H":
        from binascii import unhexlify

        return b"".join(unhexlify(part) for part in sorted(parts.values()))

    binary_data = b""
    for _, part in sorted(parts.items()):
        padding = (8 - (len(part) % 8)) % 8
        padded_part = part + (padding * "=")
        binary_data += base32_decode_stream(padded_part)

    if encoding == "Z":
        if file_type == "U":
            return deflate_decompress(binary_data).decode("utf-8")
        return deflate_decompress(binary_data)
    if file_type == "U":
        return binary_data.decode("utf-8")
    return binary_data


def encode_bbqr(data, encoding="Z", file_type="P"):
    """Encodes the given data as BBQR, returning the encoded data and format"""

    if encoding not in "H2Z":
        raise ValueError("Invalid BBQr encoding")
    if file_type not in KNOWN_FILETYPES:
        raise ValueError("Invalid BBQr file type")

    if encoding == "H":
        from binascii import hexlify

        data = hexlify(data).decode()

    if len(data) > BBQR_ALWAYS_COMPRESS_THRESHOLD:
        data = deflate_compress(data)
    else:
        # Check if compression is beneficial
        cmp = deflate_compress(data)
        if len(cmp) >= len(data):
            encoding = "2"
        else:
            encoding = "Z"
            data = cmp

    data = data.encode("utf-8") if isinstance(data, str) else data
    data = base32_encode_stream(data).rstrip("=")
    return BBQrCode(data, encoding, file_type)


# Base 32 encoding/decoding, used in BBQR only


def base32_decode_stream(encoded_str):
    """Decodes a Base32 string"""
    base32_index = {ch: index for index, ch in enumerate(B32CHARS)}

    # Strip padding
    encoded_str = encoded_str.rstrip("=")

    buffer = 0
    bits_left = 0
    decoded_bytes = bytearray()

    for char in encoded_str:
        if char not in base32_index:
            raise ValueError("Invalid Base32 character: %s" % char)
        index = base32_index[char]
        buffer = (buffer << 5) | index
        bits_left += 5

        while bits_left >= 8:
            bits_left -= 8
            decoded_bytes.append((buffer >> bits_left) & 0xFF)
            buffer &= (1 << bits_left) - 1  # Keep only the remaining bits

    # Process any remaining bits
    if bits_left >= 5:
        remaining_byte = (buffer << (8 - bits_left)) & 0xFF
        decoded_bytes.append(remaining_byte)

    return bytes(decoded_bytes)


def base32_encode_stream(data):
    """A streaming base32 encoder"""
    encoded = []
    buffer = 0
    bits_left = 0

    for byte in data:
        buffer = (buffer << 8) | byte
        bits_left += 8

        while bits_left >= 5:
            bits_left -= 5
            encoded.append(B32CHARS[(buffer >> bits_left) & 0x1F])
            buffer &= (1 << bits_left) - 1  # Keep only the remaining bits

    if bits_left > 0:
        buffer <<= 5 - bits_left
        encoded.append(B32CHARS[buffer & 0x1F])

    while len(encoded) % 8 != 0:
        encoded.append("=")  # Add padding

    return "".join(encoded)
