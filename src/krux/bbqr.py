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

FORMAT_BBQR = 3
FORMAT_COMPRESSED_BBQR = 4
FORMAT_HEX_BBQR = 5

BBQR_FORMATS = [FORMAT_BBQR, FORMAT_COMPRESSED_BBQR, FORMAT_HEX_BBQR]

B32CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
assert len(B32CHARS) == 32


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
    return data[8:], part_index, part_total, encoding, file_type


def decode_bbqr(parts, encoding, file_type):
    """Decodes the given data as BBQR, returning the decoded data"""

    if encoding == "H":
        from binascii import unhexlify

        return b"".join(unhexlify(part) for part in sorted(parts.values()))

    binary_data = b""
    for _, part in sorted(parts.items()):
        padding = (8 - (len(part) % 8)) % 8
        padded_part = part + (padding * "=")
        binary_data += base32_decode(padded_part)

    if encoding == "Z":
        try:
            import deflate
            from io import BytesIO

            # Decompress
            with deflate.DeflateIO(BytesIO(binary_data)) as d:
                decompressed = d.read()
            if file_type == "U":
                return decompressed.decode("utf-8")
            return decompressed
        except Exception as e:
            print("Error decompressing BBQR: ", e)
            raise ValueError("Error decompressing BBQR")
    if file_type == "U":
        return binary_data.decode("utf-8")
    return binary_data


def encode_bbqr(data, qr_format=FORMAT_BBQR):
    """Encodes the given data as BBQR, returning the encoded data and format"""

    if qr_format == FORMAT_HEX_BBQR:
        from binascii import hexlify

        return hexlify(data).decode(), FORMAT_HEX_BBQR

    import deflate
    from io import BytesIO

    stream = BytesIO()
    with deflate.DeflateIO(stream) as d:
        d.write(data)
    cmp = stream.getvalue()
    if len(cmp) >= len(data):
        qr_format = FORMAT_BBQR
    else:
        qr_format = FORMAT_COMPRESSED_BBQR
        data = cmp
    data = data.encode("utf-8") if isinstance(data, str) else data
    data = base32_encode(data).rstrip("=")
    return data, qr_format


# Base 32 encoding/decoding, used in BBQR only


def base32_decode(encoded_str):
    """Decodes a Base32 string according to RFC 4648."""

    # Reverse lookup table
    base32_index = {ch: index for index, ch in enumerate(B32CHARS)}

    # Strip padding
    encoded_str = encoded_str.rstrip("=")

    # Convert Base32 characters to binary string
    bits = ""
    for char in encoded_str:
        if char not in base32_index:
            raise ValueError("Invalid Base32 character: %s" % char)
        index = base32_index[char]
        binary_str = ""
        for i in range(5):
            binary_str = str(index & 1) + binary_str
            index >>= 1
        bits += binary_str

    # Convert binary string to bytes
    n = len(bits) // 8 * 8  # Only take complete groups of 8 bits
    bytes_list = []
    for i in range(0, n, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | int(bits[i + j])
        bytes_list.append(byte)

    return bytes(bytes_list)


def base32_encode(data):
    """Encodes bytes into a Base32 string according to RFC 4648."""

    def byte_to_bin(byte):
        """Convert a single byte to a binary string."""
        return "".join(str((byte >> i) & 1) for i in range(7, -1, -1))

    # Collect bits as a string of '1's and '0's
    bits = "".join(byte_to_bin(byte) for byte in data)

    # Prepare to segment bits into groups of 5
    padding_length = (5 - len(bits) % 5) % 5
    bits += "0" * padding_length  # Pad bits to make length a multiple of 5

    # Encode bits to Base32
    encoded = ""
    for i in range(0, len(bits), 5):
        index = int(bits[i : i + 5], 2)
        encoded += B32CHARS[index]

    # Calculate required padding for the encoded string
    padding = "=" * ((8 - len(encoded) % 8) % 8)
    return encoded + padding
