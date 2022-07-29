import sys
import time
from unittest import mock
import pygame as pg

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
            if time.time() - sequence_executor.key_press_timer > 0.25:
                sequence_executor.key_press_timer = 0
                sequence_executor.key = None
            return 0
        return 0 if pg.key.get_pressed()[self.key] else 1


if "pmu" not in sys.modules:
    sys.modules["pmu"] = mock.MagicMock(
        PMU_Button=PMU_Button,
    )
