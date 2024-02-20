from . import create_ctx
from ..shared_mocks import MockPrinter
from unittest.mock import patch

TEST_QR_DATA = "Krux Printer Test QR"
TEST_QR_TITLE = "Krux Printer Test"
TEST_QR_CODE = bytearray(
    b"\x7fn\xfd\x830\x08v9\xd6\xedj\xa0\xdbUU7\xc8\xa0\xe0_U\x7f\x00i\x00\xe3\xd61P\x08\xf5Q\xef^\xfe`\xe8\xc1\x7f\xdex\x936Y\x91\xb8\xeb\xd29c\xd5\xd4\x7f\x00\n#\xfe\xcd\xd7\rJ\x8e\xd9\xe5\xf8\xb9K\xe6x\x17\xb9\xca\xa0\x9a\x9a\x7f\xbb\x1b\x01"
)


def test_print_qr_code(mocker, amigo_tft):
    """Test that the print tool is called with the correct text"""
    from krux.pages.print_page import PrintPage
    from krux.input import BUTTON_ENTER

    BTN_SEQUENCE = [BUTTON_ENTER]  # Confirm print, then leave

    ctx = create_ctx(mocker, BTN_SEQUENCE, printer=MockPrinter())
    with patch(
        "krux.printers.thermal.AdafruitPrinter.print_qr_code"
    ) as mocked_print_qr_code:
        with patch(
            "krux.printers.thermal.AdafruitPrinter.print_string"
        ) as mocked_print_string:
            test_print = PrintPage(ctx)
            test_print.print_qr(TEST_QR_DATA, title=TEST_QR_TITLE)
            mocked_print_string.assert_called_once_with(TEST_QR_TITLE + "\n\n")
            mocked_print_qr_code.assert_called_once_with(TEST_QR_CODE)
