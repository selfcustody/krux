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


def test_print_string_fails(mocker, m5stickv, bad_printer_cls):
    printer = bad_printer_cls()
    with pytest.raises(NotImplementedError):
        printer.print_string("")


def test_create_printer_none_driver(mocker, m5stickv):
    from krux.krux_settings import Settings
    from krux.printers import create_printer

    Settings().hardware.printer.driver = "none"
    printer = create_printer()
    assert printer is None


def test_create_printer_adafruit_driver(mocker, m5stickv):
    from krux.krux_settings import Settings
    from krux.printers import create_printer

    Settings().hardware.printer.driver = "thermal/adafruit"
    printer = create_printer()
    assert printer is not None
    assert printer.__class__.__name__ == "AdafruitPrinter"


def test_create_printer_fileprinter_driver(mocker, m5stickv):
    from krux.krux_settings import Settings
    from krux.printers import create_printer

    Settings().hardware.printer.driver = "cnc/file"
    printer = create_printer()
    assert printer is not None
    assert printer.__class__.__name__ == "FilePrinter"


def test_create_grbl_driver(mocker, m5stickv):
    from krux.krux_settings import Settings
    from krux.printers import create_printer

    Settings().hardware.printer.driver = "cnc/grbl"
    printer = create_printer()
    assert printer is not None
    assert printer.__class__.__name__ == "GRBLPrinter"
