import sys
from unittest import mock

if "image" not in sys.modules:
    sys.modules["image"] = mock.MagicMock()
