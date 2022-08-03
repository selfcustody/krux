import sys
import time
from unittest import mock
import pygame as pg

PRESSED = 0
RELEASED = 1

sequence_executor = None


def register_sequence_executor(s):
    global sequence_executor
    sequence_executor = s


class PMU_Button:
    def __init__(self):
        self.key = pg.K_UP

    def value(self):
        if (
            sequence_executor
            and sequence_executor.key is not None
            and sequence_executor.key == self.key
        ):
            sequence_executor.key_checks += 1
            # wait for release
            if sequence_executor.key_checks == 1:
                return RELEASED
            # wait for press
            # if pressed
            elif sequence_executor.key_checks == 2 or sequence_executor.key_checks == 3:
                return PRESSED
            # released
            elif sequence_executor.key_checks == 4:
                sequence_executor.key = None
                sequence_executor.key_checks = 0
                return RELEASED
        return 0 if pg.key.get_pressed()[self.key] else 1


if "pmu" not in sys.modules:
    sys.modules["pmu"] = mock.MagicMock(
        PMU_Button=PMU_Button,
    )
