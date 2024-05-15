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
# pylint: disable=E1101
import io
import math
import qrcode
from ur.ur_decoder import URDecoder
from ur.ur import UR

FORMAT_NONE = 0
FORMAT_PMOFN = 1
FORMAT_UR = 2
FORMAT_BBQR = 3

PMOFN_PREFIX_LENGTH_1D = 6
PMOFN_PREFIX_LENGTH_2D = 8
BBQR_PREFIX_LENGTH = 8
UR_GENERIC_PREFIX_LENGTH = 22

# CBOR_PREFIX = 6 bytes for tags, 1 for index, 1 for max_index, 2 for message len, 4 for checksum
# Check UR's fountain_encoder.py file, on Part.cbor() function for more details
UR_CBOR_PREFIX_LEN = 14
UR_BYTEWORDS_CRC_LEN = 4  # 32 bits CRC used on Bytewords encoding

UR_MIN_FRAGMENT_LENGTH = 10

# List of capacities, based on versions
# Version 1(index 0)=21x21px = 17 bytes, version 2=25x25px = 32 bytes ...
# Limited to version 20
QR_CAPACITY = [
    17,
    32,
    53,
    78,
    106,
    134,
    154,
    192,
    230,
    271,
    321,
    367,
    425,
    458,
    520,
    586,
    644,
    718,
    792,
    858,
]

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


class QRPartParser:
    """Responsible for parsing either a singular or animated series of QR codes
    and returning the final decoded, combined data
    """

    def __init__(self):
        self.parts = {}
        self.total = -1
        self.format = None
        self.decoder = URDecoder()
        self.bbqr_encoding = None
        self.bbqr_file_type = None

    def parsed_count(self):
        """Returns the number of parsed parts so far"""
        if self.format == FORMAT_UR:
            # Single-part URs have no expected part indexes
            if self.decoder.fountain_decoder.expected_part_indexes is None:
                return 1 if self.decoder.result is not None else 0
            completion_pct = self.decoder.estimated_percent_complete()
            return math.ceil(completion_pct * self.total_count() / 2) + len(
                self.decoder.fountain_decoder.received_part_indexes
            )
        return len(self.parts)

    def processed_parts_count(self):
        """Returns quantity of processed QR code parts"""
        if self.format == FORMAT_UR:
            return self.decoder.fountain_decoder.processed_parts_count
        return len(self.parts)

    def total_count(self):
        """Returns the total number of parts there should be"""
        if self.format == FORMAT_UR:
            # Single-part URs have no expected part indexes
            if self.decoder.fountain_decoder.expected_part_indexes is None:
                return 1
            return self.decoder.expected_part_count() * 2
        return self.total

    def parse(self, data):
        """Parses the QR data, extracting part information"""
        if self.format is None:
            self.format = detect_format(data)

        if self.format == FORMAT_NONE:
            self.parts[1] = data
            self.total = 1
        elif self.format == FORMAT_PMOFN:
            part, index, total = parse_pmofn_qr_part(data)
            self.parts[index] = part
            self.total = total
        elif self.format == FORMAT_UR:
            self.decoder.receive_part(data)
        elif self.format == FORMAT_BBQR:
            part, index, total, encoding, file_type = parse_bbqr(data)
            self.parts[index] = part
            self.total = total
            self.bbqr_encoding = encoding
            self.bbqr_file_type = file_type

    def is_complete(self):
        """Returns a boolean indicating whether or not enough parts have been parsed"""
        if self.format == FORMAT_UR:
            return self.decoder.is_complete()
        keys_check = (
            sum(range(1, self.total + 1))
            if self.format in (FORMAT_PMOFN, FORMAT_NONE)
            else sum(range(self.total))
        )
        return (
            self.total != -1
            and self.parsed_count() == self.total_count()
            and sum(self.parts.keys()) == keys_check
        )

    def result(self):
        """Returns the combined part data"""
        if self.format == FORMAT_UR:
            return UR(self.decoder.result.type, bytearray(self.decoder.result.cbor))
        if self.format == FORMAT_BBQR:
            from .baseconv import base_decode

            if self.bbqr_encoding == "H":
                from binascii import unhexlify

                return b"".join(unhexlify(part) for part in sorted(self.parts.values()))

            binary_data = b""
            for _, part in sorted(self.parts.items()):
                padding = (8 - (len(part) % 8)) % 8
                padded_part = part + (padding * "A")
                binary_data += base_decode(padded_part.encode("utf-8"), 32)

            if self.bbqr_encoding == "Z":
                try:
                    import uzlib

                    stream = io.BytesIO(binary_data)

                    # Decompress
                    decompressor = uzlib.DecompIO(stream, -10)
                    decompressed = decompressor.read()
                    if self.bbqr_file_type == "U":
                        return decompressed.decode("utf-8")
                    return decompressed
                except Exception as e:
                    print("Error decompressing BBQR: ", e)
            if self.bbqr_file_type == "U":
                return binary_data.decode("utf-8")
            return binary_data

        code_buffer = io.StringIO("")
        for _, part in sorted(self.parts.items()):
            if isinstance(part, bytes):
                # Encoded data won't write on StringIO
                return part
            code_buffer.write(part)
        code = code_buffer.getvalue()
        code_buffer.close()
        return code


def int2base36(n):
    """Convert integer n to a base36 string."""
    assert 0 <= n <= 1295  # ensure the number is within the valid range

    def tostr(x):
        """Convert integer x to a base36 character."""
        return chr(48 + x) if x < 10 else chr(65 + x - 10)

    quotient, remainder = divmod(n, 36)
    return tostr(quotient) + tostr(remainder)


def to_qr_codes(data, max_width, qr_format, file_type=None):
    """Returns the list of QR codes necessary to represent the data in the qr format, given
    the max_width constraint
    """
    if qr_format == FORMAT_NONE:
        code = qrcode.encode(data)
        yield (code, 1)
    else:
        if qr_format == FORMAT_BBQR:
            # Compress data and check if it's worth it
            # import uzlib
            from .baseconv import base32_encode

            # cmp = uzlib.compress(data)
            # if len(cmp) >= len(data):
            #     encoding = "2"
            # else:
            #     encoding = "Z"
            #     data = cmp
            encoding = "2"  # Current micropython does not have compression on uzlib
            data = data.encode("utf-8") if isinstance(data, str) else data
            data = base32_encode(data)
        num_parts, part_size = find_min_num_parts(data, max_width, qr_format)
        if qr_format == FORMAT_PMOFN:
            part_index = 0
            while True:
                part_number = "p%dof%d " % (part_index + 1, num_parts)
                part = None
                if part_index == num_parts - 1:
                    part = part_number + data[part_index * part_size :]
                    part_index = 0
                else:
                    part = (
                        part_number
                        + data[part_index * part_size : (part_index + 1) * part_size]
                    )
                    part_index += 1
                code = qrcode.encode(part)
                yield (code, num_parts)
        elif qr_format == FORMAT_UR:
            from ur.ur_encoder import UREncoder

            encoder = UREncoder(data, part_size, 0)
            while True:
                part = encoder.next_part()
                code = qrcode.encode(part)
                yield (code, encoder.fountain_encoder.seq_len())
        elif qr_format == FORMAT_BBQR:
            part_index = 0
            while True:
                header = "B$%s%s%s%s" % (
                    encoding,
                    file_type,
                    int2base36(num_parts),
                    int2base36(part_index),
                )
                part = None
                if part_index == num_parts - 1:
                    part = header + data[part_index * part_size :]
                    part_index = 0
                else:
                    part = (
                        header
                        + data[part_index * part_size : (part_index + 1) * part_size]
                    )
                    part_index += 1
                code = qrcode.encode(part)
                yield (code, num_parts)


def get_size(qr_code):
    """Returns the size of the qr code as the number of chars until the first newline"""
    size = math.sqrt(len(qr_code) * 8)
    return int(size)


def max_qr_bytes(max_width):
    """Calculates the maximum length, in bytes, a QR code of a given size can store"""
    # Given qr_size =  17 + 4 * version + 2 * frame_size
    max_width -= 2  # Subtract frame width
    qr_version = (max_width - 17) // 4
    try:
        return QR_CAPACITY[qr_version - 1]
    except:
        # Limited to version 20
        return QR_CAPACITY[-1]


def find_min_num_parts(data, max_width, qr_format):
    """Finds the minimum number of QR parts necessary to encode the data in
    the specified format within the max_width constraint
    """
    qr_capacity = max_qr_bytes(max_width)
    if qr_format == FORMAT_PMOFN:
        data_length = len(data)
        part_size = qr_capacity - PMOFN_PREFIX_LENGTH_1D
        # where prefix = "pXofY " where Y < 9
        num_parts = (data_length + part_size - 1) // part_size
        if num_parts > 9:  # Prefix has 2 digits numbers, so re-calculate
            part_size = qr_capacity - PMOFN_PREFIX_LENGTH_2D
            # where prefix = "pXXofYY " where max YY = 99
            num_parts = (data_length + part_size - 1) // part_size
        part_size = (data_length + num_parts - 1) // num_parts
    elif qr_format == FORMAT_UR:
        qr_capacity -= (
            # This is an approximation, UR index grows indefinitely
            UR_GENERIC_PREFIX_LENGTH  # index: ~ "ur:crypto-psbt/xxx-xx/"
        )
        # UR will add a bunch of info (some duplicated) on the body of each QR
        # Info's lenght is multiplied by 2 in Bytewords.encode step
        qr_capacity -= (UR_CBOR_PREFIX_LEN + UR_BYTEWORDS_CRC_LEN) * 2
        data_length = len(data.cbor)
        data_length *= 2  # UR will Bytewords.encode, which multiply bytes length by 2
        num_parts = (data_length + qr_capacity - 1) // qr_capacity
        # For UR, part size will be the input for "max_fragment_len"
        part_size = len(data.cbor) // num_parts
        part_size = max(part_size, UR_MIN_FRAGMENT_LENGTH)
    elif qr_format == FORMAT_BBQR:
        data_length = len(data)
        part_size = qr_capacity - BBQR_PREFIX_LENGTH
        num_parts = (data_length + part_size - 1) // part_size

        # Ensure part_size is a multiple of 8
        part_size = (data_length + num_parts - 1) // num_parts
        part_size -= part_size % 8  # Adjust to the nearest lower multiple of 8

        # Recalculate num_parts with the adjusted part_size
        num_parts = (data_length + part_size - 1) // part_size

    else:
        raise ValueError("Invalid format type")
    return num_parts, part_size


def parse_pmofn_qr_part(data):
    """Parses the QR as a P M-of-N part, extracting the part's content, index, and total"""
    of_index = data.index("of")
    space_index = data.index(" ")
    part_index = int(data[1:of_index])
    part_total = int(data[of_index + 2 : space_index])
    return data[space_index + 1 :], part_index, part_total


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


def detect_format(data):
    """Detects the QR format of the given data"""
    qr_format = FORMAT_NONE
    try:
        if data.startswith("p") and data.index("of") <= 5:
            qr_format = FORMAT_PMOFN
        elif data.lower().startswith("ur:"):
            qr_format = FORMAT_UR
        elif data.startswith("B$"):
            qr_format = FORMAT_BBQR

    except:
        pass
    return qr_format
