from ..shared_mocks import mock_context
from . import create_ctx
from .home_pages.test_home import tdata
from unittest.mock import patch

SINGLE_SIG_12W_BINARY_QR = bytearray(
    b"\x7fT\xc8?\xa8P\nvA$\xdd\xae\xdb\xab\xdb%\x84t\x83\xb6\xa3\xe0_U\xf5\x07p\x0e\x00\xdf\xbb\xb7*\xb4\x0ei.Q\x96\xa4\x07H\xcc\xa8\xe4z\xeb.\xb2\x94\xa2s%\xe1\xca\x85\xe6\xc8V\xa6\xb7\xaeGKi\x16A\xd2\xbcX(\x18Pwz\xff\x00\xfa0\xea\xdf%V\n\xb2\xa2H]\xa1\xf7\xaf+\x0bUv\xc5\x16\xbd\xa0'\xfe\xf4\x17zr\x00"
)
TEST_DATA = "test code"
TEST_DATA_QR_SIZE = 21
TEST_DATA_QR_SIZE_FRAMED = 23
TEST_TITLE = "Test QR Code"
TEST_CODE_BINARY_QR = bytearray(
    b'\x7f\xdd?\x88\tv-\xdd\xae\xa9\xdb\x95t\x83\xbc\xe0_\xf5\x07\xc0\x00O?\xd7T\xf7R1c\x9cFUF\xb5\x00\xd2\xd6\x1f\xe6\t"x]T\xa4kIuM\x91\xa0\x11\xf9\x17R\x00'
)
FRAMED_TEST_CODE_BINARY_QR = bytearray(
    b"\x00\x00\x00\x7f\xdd\x9f &H\xd7\xd2\xa5k\xea\xd2\x95t\t\xf2\x82\xfcU\x7f\x000\x00O?\x17S\xdd\x0b\x153\x06\xa7QQF\xb5\x00H[\xfca\x1e\x82\x08\x1e]T\x84\xae%E\xd7\x14!hD\xf2\x17R\x00\x00\x00\x00"
)
PBM_TEST_CODE_BINARY_QR = bytearray(
    b"P4\n23 23\n\x00\x00\x00\x7f]\xfcA\x19\x04]it]et]ItA=\x04\x7fU\xfc\x00\x0c\x00y~t2\xae\xf4\x15\x19\x8c\x0eX\xa8S\x15h\x00Kh\x7f\x0c\xf0A\x10x]\x15\x10]i(]e\x10Ab$\x7fBP\x00\x00\x00"
)


TEST_QR_CODE = bytearray(
    b"\x08e0c595c5\x00\x00\x00\n\xfb`e$\x90\xed\xfb\xd0r\x13\x1d1%\\6\xd3\xee0\xc4\xb8\x80h1>'\xf5\x9a5\x1cO\x97\xaa"
)

TEST_QR_CODE_SVG = b'<svg xmlns="http://www.w3.org/2000/svg" width="310" height="310">\n<rect stroke="black" stroke-width="0" x="10" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="20" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="30" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="50" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="60" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="100" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="140" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="240" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="270" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="280" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="290" y="10" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="20" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="20" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="20" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="100" y="20" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="120" y="20" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="130" y="20" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="140" y="20" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="20" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="160" y="20" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="170" y="20" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="180" y="20" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="190" y="20" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="20" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="290" y="20" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="30" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="30" y="30" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="30" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="50" y="30" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="30" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="100" y="30" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="110" y="30" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="120" y="30" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="160" y="30" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="200" y="30" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="30" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="30" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="30" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="270" y="30" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="290" y="30" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="30" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="50" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="100" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="120" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="140" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="160" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="170" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="190" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="270" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="290" y="40" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="50" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="30" y="50" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="50" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="50" y="50" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="50" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="110" y="50" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="130" y="50" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="180" y="50" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="200" y="50" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="50" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="50" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="50" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="50" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="270" y="50" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="290" y="50" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="60" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="60" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="60" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="110" y="60" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="140" y="60" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="60" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="160" y="60" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="60" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="290" y="60" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="20" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="30" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="50" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="60" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="110" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="130" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="170" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="190" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="240" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="270" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="280" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="290" y="70" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="130" y="80" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="140" y="80" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="80" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="160" y="80" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="20" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="30" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="50" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="80" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="100" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="110" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="130" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="140" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="180" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="190" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="220" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="240" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="280" y="90" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="100" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="20" y="100" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="60" y="100" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="100" y="100" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="100" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="170" y="100" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="100" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="220" y="100" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="100" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="280" y="100" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="290" y="100" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="80" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="100" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="120" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="130" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="160" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="190" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="200" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="220" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="270" y="110" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="30" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="50" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="60" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="80" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="100" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="110" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="120" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="140" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="160" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="200" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="220" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="280" y="120" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="20" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="30" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="80" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="100" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="120" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="160" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="180" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="190" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="200" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="270" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="280" y="130" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="20" y="140" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="140" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="140" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="110" y="140" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="130" y="140" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="140" y="140" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="140" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="160" y="140" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="190" y="140" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="200" y="140" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="140" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="140" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="140" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="140" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="290" y="140" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="150" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="150" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="110" y="150" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="140" y="150" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="200" y="150" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="150" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="220" y="150" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="150" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="150" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="150" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="280" y="150" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="20" y="160" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="160" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="50" y="160" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="160" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="110" y="160" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="130" y="160" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="160" y="160" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="160" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="160" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="160" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="170" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="20" y="170" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="50" y="170" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="170" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="80" y="170" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="130" y="170" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="140" y="170" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="170" y="170" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="200" y="170" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="170" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="170" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="270" y="170" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="180" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="20" y="180" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="30" y="180" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="60" y="180" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="180" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="110" y="180" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="180" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="180" y="180" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="200" y="180" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="180" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="220" y="180" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="180" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="180" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="270" y="180" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="280" y="180" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="290" y="180" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="190" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="190" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="190" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="80" y="190" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="110" y="190" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="120" y="190" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="130" y="190" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="190" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="200" y="190" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="220" y="190" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="190" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="190" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="200" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="200" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="50" y="200" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="60" y="200" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="80" y="200" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="120" y="200" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="200" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="160" y="200" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="170" y="200" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="190" y="200" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="220" y="200" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="200" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="280" y="200" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="30" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="60" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="80" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="110" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="120" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="130" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="160" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="180" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="190" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="220" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="240" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="270" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="280" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="290" y="210" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="220" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="100" y="220" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="110" y="220" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="130" y="220" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="140" y="220" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="220" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="160" y="220" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="170" y="220" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="200" y="220" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="220" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="220" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="220" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="280" y="220" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="20" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="30" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="50" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="60" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="110" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="130" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="180" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="280" y="230" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="240" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="240" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="110" y="240" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="120" y="240" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="130" y="240" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="160" y="240" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="180" y="240" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="190" y="240" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="240" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="240" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="240" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="30" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="50" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="100" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="120" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="130" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="160" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="170" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="200" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="220" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="240" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="270" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="290" y="250" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="260" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="30" y="260" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="260" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="50" y="260" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="260" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="260" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="120" y="260" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="130" y="260" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="140" y="260" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="260" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="280" y="260" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="290" y="260" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="30" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="50" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="120" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="140" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="160" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="180" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="190" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="200" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="220" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="230" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="270" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="280" y="270" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="280" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="280" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="280" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="120" y="280" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="140" y="280" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="150" y="280" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="170" y="280" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="180" y="280" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="210" y="280" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="240" y="280" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="280" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="280" y="280" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="10" y="290" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="20" y="290" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="30" y="290" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="40" y="290" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="50" y="290" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="60" y="290" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="70" y="290" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="90" y="290" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="110" y="290" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="180" y="290" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="240" y="290" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="250" y="290" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="260" y="290" width="10" height="10" fill="black"/>\n<rect stroke="black" stroke-width="0" x="270" y="290" width="10" height="10" fill="black"/>\n</svg>'

FILES_FOLDER = "files"


import pytest


@pytest.fixture
def mocker_sd_card(mocker):
    from krux.pages import file_operations

    mock_open = mocker.mock_open()
    mocker.patch("builtins.open", mock_open, create=True)

    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
    )

    savefile_mock = mocker.patch.object(
        file_operations,
        "SaveFile",
        autospec=True,
    ).return_value

    return mock_open, savefile_mock


@pytest.fixture
def mocker_save_file_esc(mocker):
    from krux.pages import ESC_KEY, file_operations

    savefile_mock = mocker.MagicMock()
    savefile_mock.set_filename.return_value = ESC_KEY
    mocker.patch.object(file_operations, "SaveFile", return_value=savefile_mock)
    return savefile_mock


@pytest.fixture
def mocker_sd_card_svg(mocker):
    import os

    from krux.pages import file_operations

    file_path = os.path.join(os.path.dirname(__file__), FILES_FOLDER, "qr_image.svg")
    with open(file_path, "r", encoding="utf-8") as f:
        svg_content = f.read().encode("utf-8")

    savefile_mock = mocker.patch.object(
        file_operations,
        "SaveFile",
        autospec=True,
    ).return_value

    return savefile_mock, svg_content


@pytest.fixture
def mocker_theme_background_white(mocker):
    from krux.themes import WHITE, theme

    mocker.patch.object(theme, "bg_color", WHITE)


def test_init_qr_view_background_white(amigo, mocker, mocker_theme_background_white):
    from krux.pages.qr_view import SeedQRView
    from krux.themes import WHITE

    ctx = mock_context(mocker)
    qr_view = SeedQRView(ctx, data=TEST_DATA, title=TEST_TITLE)

    assert qr_view.qr_foreground == WHITE


def test_load_qr_no_title(mocker, amigo):
    from krux.input import BUTTON_TOUCH
    from krux.pages import MENU_CONTINUE
    from krux.pages.qr_view import SeedQRView

    # When call display_qr with no title, it should use the default title
    # we want to cover a line where the self.title is None
    # and assert the local variable to label = ""
    ctx = mock_context(mocker)
    qr_view = SeedQRView(ctx, data=TEST_DATA, title=None)

    # we need to mock these because
    # display_qr() heavily depends on
    # UI methods like wait_for_button,
    # draw_hcentered_text, draw_grided_qr, etc..
    mocker.patch.object(qr_view, "draw_grided_qr")
    mocker.patch.object(qr_view.ctx.input, "wait_for_button", return_value=BUTTON_TOUCH)
    mocker.patch.object(qr_view.ctx.display, "height", return_value=240)
    mocker.patch.object(qr_view.ctx.display, "width", return_value=240)
    mocker.patch.object(qr_view.ctx.display, "qr_offset", return_value=10)
    mocker.patch.object(qr_view.ctx.display, "draw_hcentered_text")

    result = qr_view.display_qr(
        allow_export=False, transcript_tools=False, quick_exit=True
    )

    assert result == MENU_CONTINUE


def test_display_qr_toggle_brightness(amigo, mocker):
    from krux.input import BUTTON_PAGE, BUTTON_TOUCH
    from krux.pages import MENU_CONTINUE
    from krux.pages.qr_view import SeedQRView
    from krux.themes import DARKGREY, WHITE

    # we need to cover the toogle brightness local method
    # since it isnt callable from the test
    # we need to mock the ctx.display
    ctx = mock_context(mocker)

    ctx.input = mocker.Mock()
    ctx.input.wait_for_button.side_effect = [
        BUTTON_PAGE,
        BUTTON_TOUCH,
    ]

    ctx.display = mocker.Mock()
    ctx.display.height.return_value = 240
    ctx.display.width.return_value = 240
    ctx.display.qr_offset.return_value = 10
    ctx.display.draw_hcentered_text = mocker.Mock()

    qr_view = SeedQRView(ctx, data=TEST_DATA, title="Test Title")

    # we need to set the initial color
    # to check if the toggle works
    qr_view.qr_foreground = WHITE

    mocker.patch.object(qr_view, "draw_grided_qr")

    result = qr_view.display_qr(
        allow_export=False, transcript_tools=False, quick_exit=True
    )

    # After toggle, it should switch from WHITE to DARKGREY
    assert qr_view.qr_foreground == DARKGREY
    assert result == MENU_CONTINUE


def test_load_qr_view(amigo, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV, SWIPE_LEFT, SWIPE_RIGHT

    BTN_SEQUENCE = [
        SWIPE_LEFT,  # lines mode
        BUTTON_ENTER,  # move to line 1
        SWIPE_LEFT,  # zoomed regions mode
        SWIPE_LEFT,  # regions mode
        SWIPE_LEFT,  # grided mode
        SWIPE_LEFT,  # back to standard mode
        SWIPE_LEFT,  # lines mode again
        SWIPE_RIGHT,  # back to standard mode
        BUTTON_ENTER,  # leave
        BUTTON_PAGE_PREV,  # move to "Back to Menu"
        BUTTON_ENTER,  # confirm
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    data = TEST_DATA
    seed_qr_view = SeedQRView(ctx, data=data, title=TEST_TITLE)
    seed_qr_view.display_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.display.draw_qr_code.call_count == 8
    assert ctx.display.draw_qr_code.call_args[0][0] == TEST_CODE_BINARY_QR


def test_load_seed_qr(amigo, mocker, tdata):
    from krux.pages.qr_view import SeedQRView
    from krux.themes import WHITE
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV, SWIPE_LEFT, SWIPE_RIGHT
    from krux.wallet import Wallet

    BTN_SEQUENCE = [
        SWIPE_LEFT,  # lines mode
        BUTTON_ENTER,  # move to line 1
        SWIPE_LEFT,  # zoomed regions mode
        SWIPE_LEFT,  # regions mode
        SWIPE_LEFT,  # grided mode
        SWIPE_LEFT,  # back to standard mode
        SWIPE_LEFT,  # lines mode again
        SWIPE_RIGHT,  # back to standard mode
        BUTTON_ENTER,  # Enter QR menu
        BUTTON_PAGE_PREV,  # move to "Back to Menu"
        BUTTON_ENTER,  # confirm
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE, Wallet(tdata.SINGLESIG_12_WORD_KEY), None)
    seed_qr_view = SeedQRView(ctx, binary=False)
    seed_qr_view.display_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.display.draw_qr_code.call_count == 8
    ctx.display.draw_qr_code.assert_called_with(
        # Standard SeedQR
        SINGLE_SIG_12W_BINARY_QR,
    )


def test_loop_through_regions(amigo, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV, SWIPE_LEFT, SWIPE_RIGHT
    from ..test_encryption import CBC_ENCRYPTED_QR

    BTN_SEQUENCE = (
        [
            SWIPE_LEFT,  # lines mode
            BUTTON_ENTER,  # move to line 1
            SWIPE_LEFT,  # zoomed regions mode
            SWIPE_LEFT,  # regions mode
        ]
        + [BUTTON_ENTER] * 49  # Loop through regions and return to A1
        + [
            SWIPE_LEFT,  # grided mode
            SWIPE_LEFT,  # back to standard mode
            SWIPE_LEFT,  # lines mode again
            SWIPE_RIGHT,  # back to standard mode
            BUTTON_ENTER,  # leave
            BUTTON_PAGE_PREV,  # move to Back to Menu
            BUTTON_ENTER,  # confirm
        ]
    )

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    data = CBC_ENCRYPTED_QR  # Will produce an QR code with 48 regions, max=G7
    seed_qr_view = SeedQRView(ctx, data=data, title=TEST_TITLE)
    seed_qr_view.display_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.display.draw_qr_code.call_count == 57


def test_loop_through_brightness(amigo, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.themes import WHITE, DARKGREY
    from krux.input import BUTTON_TOUCH
    from krux.wallet import Wallet

    TOUCH_SEQ = [
        # Open touch menu
        1,  # Toggle brightness to bright
        # Open touch menu
        1,  # Toggle brightness to dark
        # Open touch menu
        1,  # Toggle brightness to default
        # Open touch menu
        4,  # Exit
    ]

    BTN_SEQUENCE = [BUTTON_TOUCH] * 8

    ctx = create_ctx(mocker, BTN_SEQUENCE, touch_seq=TOUCH_SEQ)
    data = TEST_DATA
    seed_qr_view = SeedQRView(ctx, data=data, title=TEST_TITLE)
    seed_qr_view.display_qr()
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.display.draw_qr_code.call_count == 4
    assert ctx.display.draw_qr_code.call_args_list == [
        mocker.call(TEST_CODE_BINARY_QR),  # Default
        mocker.call(TEST_CODE_BINARY_QR, light_color=WHITE),  # Brighter
        mocker.call(TEST_CODE_BINARY_QR, light_color=DARKGREY),  # Darker
        mocker.call(TEST_CODE_BINARY_QR),  # Default
    ]


def test_add_frame(amigo, mocker):
    from krux.pages.qr_view import SeedQRView

    ctx = mock_context(mocker)
    framed_code, new_size = SeedQRView(ctx, data=TEST_DATA, title=TEST_TITLE).add_frame(
        TEST_CODE_BINARY_QR, TEST_DATA_QR_SIZE
    )

    assert new_size == TEST_DATA_QR_SIZE_FRAMED
    assert framed_code == FRAMED_TEST_CODE_BINARY_QR


def test_save_pbm_image(amigo, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.sd_card import PBM_IMAGE_EXTENSION
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV, SWIPE_LEFT, SWIPE_RIGHT

    BTN_SEQUENCE = [
        BUTTON_PAGE_PREV,  # move to "Back to Menu"
        BUTTON_ENTER,  # confirm
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)

    mocker.patch("os.listdir", new=mocker.MagicMock(return_value=["file1"]))
    with patch("krux.sd_card.SDHandler.write_binary") as mock_write_binary:
        qr_viewer = SeedQRView(ctx, data=TEST_DATA, title="Test QR Code")
        qr_viewer.save_pbm_image(TEST_TITLE)

        mock_write_binary.assert_called_once_with(
            TEST_TITLE + PBM_IMAGE_EXTENSION, PBM_TEST_CODE_BINARY_QR
        )
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_save_bmp_image(amigo, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.sd_card import BMP_IMAGE_EXTENSION
    import sys
    from krux.input import BUTTON_ENTER, BUTTON_PAGE_PREV, SWIPE_LEFT, SWIPE_RIGHT

    BTN_SEQUENCE = [
        BUTTON_PAGE_PREV,  # move to "Back to Menu"
        BUTTON_ENTER,  # confirm
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)

    #  mock SDHandler listdir call
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
    )

    qr_viewer = SeedQRView(ctx, data=TEST_DATA, title="Test QR Code")
    qr_viewer.save_bmp_image(TEST_TITLE, TEST_DATA_QR_SIZE_FRAMED * 2)
    sys.modules["image"].Image.return_value.save.assert_called_once_with(
        "/sd/" + TEST_TITLE + BMP_IMAGE_EXTENSION
    )
    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)


def test_save_bmp_image_no_sd_card(amigo, mocker):
    from krux.pages.qr_view import SeedQRView

    flash_text = mocker.spy(SeedQRView, "flash_text")

    ctx = create_ctx(mocker, [])

    qr_viewer = SeedQRView(ctx, data=TEST_QR_CODE, title="Test QR Code")
    qr_viewer.save_bmp_image(TEST_TITLE, TEST_DATA_QR_SIZE_FRAMED * 2)
    flash_text.assert_called_once_with(qr_viewer, "SD card not detected.")


def test_save_bmp_image_esc_key(amigo, mocker, mocker_save_file_esc):
    from krux.pages.qr_view import SeedQRView
    from krux.sd_card import BMP_IMAGE_EXTENSION

    ctx = create_ctx(mocker, [])

    #  mock SDHandler listdir call
    mocker.patch(
        "os.listdir",
        new=mocker.MagicMock(return_value=["somefile", "otherfile"]),
    )

    qr_viewer = SeedQRView(ctx, data=TEST_QR_CODE, title="Test QR Code")
    qr_viewer.save_bmp_image(TEST_TITLE, TEST_DATA_QR_SIZE_FRAMED * 2)

    mocker_save_file_esc.set_filename.assert_called_once_with(
        TEST_TITLE, file_extension=BMP_IMAGE_EXTENSION
    )


def test_save_svg_image(amigo, mocker, mocker_sd_card_svg):

    from krux.pages.qr_view import SeedQRView
    from krux.sd_card import SVG_IMAGE_EXTENSION

    savefile_mock, svg_content = mocker_sd_card_svg

    ctx = create_ctx(mocker, [])

    qr_viewer = SeedQRView(ctx, data=TEST_QR_CODE, title="Test QR Code")
    qr_viewer.save_svg_image(TEST_TITLE)

    savefile_mock.save_file.assert_called_once_with(
        svg_content,
        TEST_TITLE,
        file_extension=SVG_IMAGE_EXTENSION,
        save_as_binary=True,
        prompt=False,
    )


def test_save_qr_image_menu_pbm(amigo, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # Enter QR menu
        BUTTON_PAGE,
        BUTTON_PAGE,  # Move to "Save QR image to SD card"
        BUTTON_ENTER,  # Save QR image to SD card
        BUTTON_ENTER,  # Confirm first resolution - PBM format
        BUTTON_PAGE,
        BUTTON_PAGE,  # Move to "Back to Menu"
        BUTTON_ENTER,  # Confirm
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    data = TEST_DATA
    seed_qr_view = SeedQRView(ctx, data=data, title=TEST_TITLE)
    mocker.patch.object(seed_qr_view, "has_sd_card", new=lambda: True)

    mock_save_pbm_image = mocker.patch.object(seed_qr_view, "save_pbm_image")
    seed_qr_view.display_qr(allow_export=True)

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.display.draw_qr_code.call_count == 1
    mock_save_pbm_image.assert_called_once_with(
        TEST_TITLE.replace(" ", "_")[:10]
    )  # 10 is the max length for a suggested filename


def save_qr_image_menu_pbm(amigo, mocker):
    from krux.pages.qr_view import SeedQRView
    from krux.input import BUTTON_ENTER, BUTTON_PAGE, BUTTON_PAGE_PREV

    BTN_SEQUENCE = [
        BUTTON_ENTER,  # enter QR menu
        BUTTON_PAGE,
        BUTTON_PAGE,  # Move to "Save QR image to SD card"
        BUTTON_ENTER,  # Save QR image to SD card
        BUTTON_PAGE_PREV,  # On filename prompt, move to "Go"
        BUTTON_ENTER,  # Confirm
        BUTTON_PAGE,  # Go to first resolution - BMP format
        BUTTON_ENTER,  # Confirm first resolution - BMP format
        BUTTON_ENTER,  # Enter QR menu again
        BUTTON_PAGE_PREV,  # Move to "Back to Menu"
        BUTTON_ENTER,  # Confirm
    ]

    ctx = create_ctx(mocker, BTN_SEQUENCE)
    data = TEST_DATA
    seed_qr_view = SeedQRView(ctx, data=data, title=TEST_TITLE)
    mocker.patch.object(seed_qr_view, "has_sd_card", new=lambda: True)

    mock_save_bmp_image = mocker.patch.object(seed_qr_view, "save_bmp_image")
    seed_qr_view.display_qr(allow_export=True)

    assert ctx.input.wait_for_button.call_count == len(BTN_SEQUENCE)
    assert ctx.display.draw_qr_code.call_count == 2  # 1 for before, 1 for after saving
    mock_save_bmp_image.assert_called_once_with(
        TEST_TITLE.replace(" ", "_")[:10]
    )  # 10 is the max length for a suggested filename
