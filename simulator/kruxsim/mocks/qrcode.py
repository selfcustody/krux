import sys
from unittest import mock
import pyqrcode


def encode_to_string(data):
    code_str = pyqrcode.create(data, error="L", mode="binary").text()
    size = 0
    while code_str[size] != "\n":
        size += 1
    i = 0
    padding = 0
    while code_str[i] != "1":
        if code_str[i] == "\n":
            padding += 1
        i += 1
    code_str = code_str[(padding) * (size + 1) : -(padding) * (size + 1)]
    size -= 2 * padding

    new_code_str = ""
    for i in range(size):
        for j in range(size + 2 * padding + 1):
            if padding <= j < size + padding:
                index = i * (size + 2 * padding + 1) + j
                new_code_str += code_str[index]
        new_code_str += "\n"

    return new_code_str


if "qrcode" not in sys.modules:
    sys.modules["qrcode"] = mock.MagicMock(
        encode_to_string=encode_to_string,
    )
