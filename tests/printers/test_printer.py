import pytest


@pytest.fixture
def bad_printer_cls():
    from krux.printers import Printer

    class BadPrinter(Printer):
        def __init__(self):
            pass

    return BadPrinter


def test_init_fails(mocker, m5stickv):
    from krux.printers import Printer

    with pytest.raises(NotImplementedError):
        Printer()


def test_qr_data_width_fails(mocker, m5stickv, bad_printer_cls):
    printer = bad_printer_cls()

    with pytest.raises(NotImplementedError):
        printer.qr_data_width()


def test_clear_fails(mocker, m5stickv, bad_printer_cls):
    printer = bad_printer_cls()

    with pytest.raises(NotImplementedError):
        printer.clear()


def test_print_qr_code_fails(mocker, m5stickv, bad_printer_cls):
    printer = bad_printer_cls()

    with pytest.raises(NotImplementedError):
        printer.print_qr_code("")
