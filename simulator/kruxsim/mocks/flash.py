import sys
from unittest import mock

flash = bytearray(8 * 1024 * 1024)


def read_data(addr, amount):
    return flash[addr : addr + amount]


def write_data(addr, data):
    flash[addr : addr + len(data)] = data


if "flash" not in sys.modules:
    sys.modules["flash"] = mock.MagicMock(read=read_data, write=write_data)
