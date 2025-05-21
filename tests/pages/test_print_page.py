from . import create_ctx
from ..shared_mocks import MockPrinter
from unittest.mock import patch

TEST_QR_DATA = "Krux Printer Test QR"
TEST_QR_TITLE = "Krux Printer Test"
TEST_QR_CODE = bytearray(
    b"\x7fn\xfd\x830\x08v9\xd6\xedj\xa0\xdbUU7\xc8\xa0\xe0_U\x7f\x00i\x00\xe3\xd61P\x08\xf5Q\xef^\xfe`\xe8\xc1\x7f\xdex\x936Y\x91\xb8\xeb\xd29c\xd5\xd4\x7f\x00\n#\xfe\xcd\xd7\rJ\x8e\xd9\xe5\xf8\xb9K\xe6x\x17\xb9\xca\xa0\x9a\x9a\x7f\xbb\x1b\x01"
)


def test_printer_not_defined(mocker, amigo):
    from krux.input import BUTTON_ENTER
    from krux.pages.print_page import PrintPage

    ctx = create_ctx(mocker, [BUTTON_ENTER], printer=None)
    test_print = PrintPage(ctx)
    mocker.spy(test_print, "flash_error")

    test_print.print_qr(TEST_QR_DATA, title=TEST_QR_TITLE)
    test_print.flash_error.assert_called_once_with("Printer Driver not set!")


def test_print_qr_code(mocker, amigo):
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


def test_print_qr_code_throught_cnc_file_driver(mocker, amigo):
    from krux.krux_settings import CNC_FILE_DRIVER
    from krux.pages.print_page import PrintPage

    # lets redefine the printer driver to be CNC_FILE_DRIVER
    # through the mocked settings, so we can test the export to SD card
    hardware_mock = mocker.MagicMock()
    printer_mock = mocker.MagicMock()
    printer_mock.driver = CNC_FILE_DRIVER
    hardware_mock.printer = printer_mock

    mocked_settings = mocker.patch("krux.pages.print_page.Settings", autospec=True)
    mocked_settings.return_value.hardware = hardware_mock

    mocker.patch(
        "krux.pages.print_page.create_printer", return_value=mocker.MagicMock()
    )

    ctx = create_ctx(mocker, [])
    test_print = PrintPage(ctx)
    mocker.spy(test_print.ctx.display, "draw_centered_text")
    test_print.print_qr(TEST_QR_DATA, title=TEST_QR_TITLE)
    test_print.ctx.display.draw_centered_text.assert_any_call(
        "Exporting qr.nc to SD card.."
    )
