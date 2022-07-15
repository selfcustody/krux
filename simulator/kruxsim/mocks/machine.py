import sys
from unittest import mock
import pygame as pg
from krux.settings import settings

simulating_printer = False


def simulate_printer():
    global simulating_printer
    simulating_printer = True


def reset():
    pg.event.post(pg.event.Event(pg.QUIT))


class UART:
    UART1 = 0
    UART2 = 1
    UART3 = 2
    UART4 = 3
    UARTHS = 4

    def __init__(self, pin, baudrate):
        pass

    def read(self, num_bytes):
        if simulating_printer:
            if (
                settings.printer.module == "thermal"
                and settings.printer.cls == "AdafruitPrinter"
            ):
                return chr(0b00000000)
        return None

    def readline(self):
        if simulating_printer:
            if (
                settings.printer.module == "cnc"
                and settings.printer.cls == "GRBLPrinter"
            ):
                return "ok\n".encode()
        return None

    def write(self, data):
        print(data.decode())


if "machine" not in sys.modules:
    sys.modules["machine"] = mock.MagicMock(
        reset=reset, UART=mock.MagicMock(wraps=UART)
    )
