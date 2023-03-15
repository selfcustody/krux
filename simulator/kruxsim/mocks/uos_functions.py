import sys
from unittest import mock

def statvfs(dir):
    return (8192, 8192, 1896512, 1338303, 1338303, 0, 0, 0, 0, 255)

if "uos" not in sys.modules:
    sys.modules["uos"] = mock.MagicMock(
        statvfs=statvfs,
    )
