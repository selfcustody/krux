import sys
import time
from unittest import mock
import pygame as pg
from kruxsim.mocks.board import BUTTON_A, BUTTON_B
from kruxsim.mocks.fpioa_manager import fm_map

sequence_executor = None


def register_sequence_executor(s):
    global sequence_executor
    sequence_executor = s


class GPIO:
    IN = 0
    OUT = 3
    PULL_NONE = 0
    PULL_UP = 2
    PULL_DOWN = 1
    GPIOHS0 = 0
    GPIOHS1 = 1
    GPIOHS2 = 2
    GPIOHS3 = 3
    GPIOHS4 = 4
    GPIOHS5 = 5
    GPIOHS6 = 6
    GPIOHS7 = 7
    GPIOHS8 = 8
    GPIOHS9 = 9
    GPIOHS10 = 10
    GPIOHS11 = 11
    GPIOHS12 = 12
    GPIOHS13 = 13
    GPIOHS14 = 14
    GPIOHS15 = 15
    GPIOHS16 = 16
    GPIOHS17 = 17
    GPIOHS18 = 18
    GPIOHS19 = 19
    GPIOHS20 = 20
    GPIOHS21 = 21
    GPIOHS22 = 22
    GPIOHS23 = 23
    GPIOHS24 = 24
    GPIOHS25 = 25
    GPIOHS26 = 26
    GPIOHS27 = 27
    GPIOHS28 = 28
    GPIOHS29 = 29
    GPIOHS30 = 30
    GPIOHS31 = 31
    GPIO0 = 32
    GPIO1 = 33
    GPIO2 = 34
    GPIO3 = 35
    GPIO4 = 36
    GPIO5 = 37
    GPIO6 = 38
    GPIO7 = 39

    def __init__(self, gpio_num, dir, val):
        self.key = None
        pin = fm_map[gpio_num]
        if pin == BUTTON_A:
            self.key = pg.K_RETURN
        if pin == BUTTON_B:
            self.key = pg.K_SPACE

    def value(self):
        if not self.key:
            return 1
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


if "Maix" not in sys.modules:
    sys.modules["Maix"] = mock.MagicMock(
        GPIO=GPIO,
    )
