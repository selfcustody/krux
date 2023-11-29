# The MIT License (MIT)

# Copyright (c) 2021-2023 Krux contributors

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

PMOFN_PREFIX_LENGTH_1D = 6
PMOFN_PREFIX_LENGTH_2D = 8
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


class QRPartParser:
    """Responsible for parsing either a singular or animated series of QR codes
    and returning the final decoded, combined data
    """

    def __init__(self):
        self.parts = {}
        self.total = -1
        self.format = None
        self.decoder = URDecoder()

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

    def is_complete(self):
        """Returns a boolean indicating whether or not enough parts have been parsed"""
        if self.format == FORMAT_UR:
            return self.decoder.is_complete()
        return (
            self.total != -1
            and self.parsed_count() == self.total_count()
            and sum(self.parts.keys()) == sum(range(1, self.total + 1))
        )

    def result(self):
        """Returns the combined part data"""
        if self.format == FORMAT_UR:
            return UR(self.decoder.result.type, bytearray(self.decoder.result.cbor))
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
        if data.startswith("p") and data.index("of") <= 5:
            qr_format = FORMAT_PMOFN
        elif data.lower().startswith("ur:"):
            qr_format = FORMAT_UR
    except:
        pass
    return qr_format
