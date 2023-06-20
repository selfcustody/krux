import sys
from unittest import mock
import os

UOS_DIRECTORY_TYPE = 0x4000
UOS_FILE_TYPE = 0x8000


def statvfs(path):
    return (8192, 8192, 1896512, 1338303, 1338303, 0, 0, 0, 0, 255)


def stat(path):
    path = path.lstrip("/") if path.startswith("/sd") else path
    return os.stat(path)


if "uos" not in sys.modules:
    sys.modules["uos"] = mock.MagicMock(
        statvfs=statvfs,
        stat=stat,
    )
