# The MIT License (MIT)

# Copyright (c) 2021-2022 Krux contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import imp
import sys
import time
from unittest import mock
import pygame as pg
from . import lcd

sequence_executor = None


def register_sequence_executor(s):
    global sequence_executor
    sequence_executor = s


def to_screen_pos(pos):
    if lcd.screen:
        rect = lcd.screen.get_rect()
        rect.center = pg.display.get_surface().get_rect().center
        if rect.collidepoint(pos):
            out = pos[0] - rect.left, pos[1] - rect.top
            return out
    return None


class FT6X36:
    def __init__(self):
        pass

    def current_point(self):
        if sequence_executor and sequence_executor.touch_pos is not None:
            sequence_executor.touch_checks += 1
            # wait for release
            if sequence_executor.touch_checks == 1:
                return None
            # wait for press
            # if pressed
            elif (
                sequence_executor.touch_checks == 2
                or sequence_executor.touch_checks == 3
            ):
                return sequence_executor.touch_pos
            # released
            elif sequence_executor.touch_checks == 4:
                sequence_executor.touch_pos = None
                sequence_executor.touch_checks = 0
                return None
        return to_screen_pos(pg.mouse.get_pos()) if pg.mouse.get_pressed()[0] else None

    def threshold(self, value):
        pass


if "krux.touchscreens.ft6x36" not in sys.modules:
    sys.modules["krux.touchscreens.ft6x36"] = mock.MagicMock(
        FT6X36=FT6X36,
    )
