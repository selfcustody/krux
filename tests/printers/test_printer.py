import pytest
from krux.printers import Printer


class BadPrinter(Printer):
    def __init__(self):
        pass


def test_init_fails():
    with pytest.raises(NotImplementedError):
        Printer()


def test_qr_data_width_fails():
    printer = BadPrinter()

    with pytest.raises(NotImplementedError):
        printer.qr_data_width()


def test_clear_fails():
    printer = BadPrinter()

    with pytest.raises(NotImplementedError):
        printer.clear()


def test_print_qr_code_fails():
    printer = BadPrinter()

    with pytest.raises(NotImplementedError):
        printer.print_qr_code("")
