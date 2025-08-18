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
QR_CAPACITY_BYTE = [
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

QR_CAPACITY_ALPHANUMERIC = [
    25,
    47,
    77,
    114,
    154,
    195,
    224,
    279,
    335,
    395,
    468,
    535,
    619,
    667,
    758,
    854,
    938,
    1046,
    1153,
    1249,
]


class QRPartParser:
    """Responsible for parsing either a singular or animated series of QR codes
    and returning the final decoded, combined data
    """

    def __init__(self):
        self.parts = {}
        self.total = -1
        self.format = None
        self.decoder = None
        self.bbqr = None

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
            self.format, self.bbqr = detect_format(data)

        if self.format == FORMAT_NONE:
            self.parts[1] = data
            self.total = 1
        elif self.format == FORMAT_PMOFN:
            part, index, total = parse_pmofn_qr_part(data)
            self.parts[index] = part
            self.total = total
            return index - 1
        elif self.format == FORMAT_UR:
            if not self.decoder:
                from ur.ur_decoder import URDecoder

                self.decoder = URDecoder()
            self.decoder.receive_part(data)
        elif self.format == FORMAT_BBQR:
            from .bbqr import parse_bbqr

            part, index, total = parse_bbqr(data)
            self.parts[index] = part
            self.total = total
            return index
        return None

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
            from ur.ur import UR

            return UR(self.decoder.result.type, bytearray(self.decoder.result.cbor))

        if self.format == FORMAT_BBQR:
            from .bbqr import decode_bbqr

            return decode_bbqr(self.parts, self.bbqr.encoding, self.bbqr.file_type)

        code_buffer = io.StringIO("")
        for _, part in sorted(self.parts.items()):
            if isinstance(part, bytes):
                # Encoded data won't write on StringIO
                return part
            code_buffer.write(part)
        code = code_buffer.getvalue()
        code_buffer.close()
        return code


def to_qr_codes(data, max_width, qr_format):
    """Returns the list of QR codes necessary to represent the data in the qr format, given
    the max_width constraint
    """
    if qr_format == FORMAT_NONE:
        code = qrcode.encode(data)
        yield (code, 1)
    else:
        num_parts, part_size = find_min_num_parts(data, max_width, qr_format)
        if qr_format == FORMAT_PMOFN:
            part_index = 0
            while True:
                part_number = "p%dof%d " % (part_index + 1, num_parts)
                if isinstance(data, bytes):
                    part_number = part_number.encode()
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
            from .bbqr import int2base36

            part_index = 0
            while True:
                header = "B$%s%s%s%s" % (
                    data.encoding,
                    data.file_type,
                    int2base36(num_parts),
                    int2base36(part_index),
                )
                part = None
                if part_index == num_parts - 1:
                    part = header + data.payload[part_index * part_size :]
                    part_index = 0
                else:
                    part = (
                        header
                        + data.payload[
                            part_index * part_size : (part_index + 1) * part_size
                        ]
                    )
                    part_index += 1
                code = qrcode.encode(part)
                yield (code, num_parts)


def get_size(qr_code):
    """Returns the size of the qr code as the number of chars until the first newline"""
    size = math.sqrt(len(qr_code) * 8)
    return int(size)


def max_qr_bytes(max_width, encoding="byte"):
    """Calculates the maximum length, in bytes, a QR code of a given size can store"""
    # Given qr_size = 17 + 4 * version + 2 * frame_size
    max_width -= 2  # Subtract frame width
    qr_version = (max_width - 17) // 4
    if encoding == "alphanumeric":
        capacity_list = QR_CAPACITY_ALPHANUMERIC
    else:
        capacity_list = QR_CAPACITY_BYTE

    try:
        return capacity_list[qr_version - 1]
    except:
        # Limited to version 20
        return capacity_list[-1]


def find_min_num_parts(data, max_width, qr_format):
    """Finds the minimum number of QR parts necessary to encode the data in
    the specified format within the max_width constraint
    """
    encoding = "alphanumeric" if qr_format == FORMAT_BBQR else "byte"
    qr_capacity = max_qr_bytes(max_width, encoding)
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
        qr_capacity = max(UR_MIN_FRAGMENT_LENGTH, qr_capacity)
        data_length = len(data.cbor)
        data_length *= 2  # UR will Bytewords.encode, which multiply bytes length by 2
        num_parts = (data_length + qr_capacity - 1) // qr_capacity
        # For UR, part size will be the input for "max_fragment_len"
        part_size = len(data.cbor) // num_parts
        part_size = max(part_size, UR_MIN_FRAGMENT_LENGTH)
        # UR won't use "num_parts", will use encoder.fountain_encoder.seq_len() instead
    elif qr_format == FORMAT_BBQR:
        data_length = len(data.payload)
        max_part_size = qr_capacity - BBQR_PREFIX_LENGTH
        if data_length < max_part_size:
            return 1, data_length
        # Round max_part_size to the nearest lower multiple of 8
        max_part_size = (max_part_size // 8) * 8
        # Calculate the number of parts required (rounded up)
        num_parts = (data_length + max_part_size - 1) // max_part_size
        # Calculate the optimal part size
        part_size = data_length // num_parts
        # Round to the nearest higher multiple of 8
        part_size = ((part_size + 7) // 8) * 8
        # Check if the part size is within the limits
        if part_size > max_part_size:
            num_parts += 1
            part_size = data_length // num_parts
            # Round to the nearest higher multiple of 8 again
            part_size = ((part_size + 7) // 8) * 8
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


def detect_format(data):
    """Detects the QR format of the given data"""
    qr_format = FORMAT_NONE
    try:
        if data.startswith("p"):
            header = data.split(" ")[0]
            if "of" in header and header[1:].split("of")[0].isdigit():
                qr_format = FORMAT_PMOFN
        elif data.lower().startswith("ur:"):
            qr_format = FORMAT_UR
        elif data.startswith("B$"):
            from .bbqr import BBQrCode, KNOWN_ENCODINGS, KNOWN_FILETYPES

            if data[3] in KNOWN_FILETYPES:
                bbqr_file_type = data[3]
                if data[2] in KNOWN_ENCODINGS:
                    bbqr_encoding = data[2]
                    return FORMAT_BBQR, BBQrCode(None, bbqr_encoding, bbqr_file_type)

    except:
        pass
    return qr_format, None
