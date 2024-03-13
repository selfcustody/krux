# The MIT License (MIT)

# Copyright (c) 2021-2023 Krux contributors

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
import sys
from unittest import mock
import pygame as pg
from . import lcd

sequence_executor = None


def register_sequence_executor(s):
    global sequence_executor
    sequence_executor = s


class FT6X36:
    def __init__(self):
        self.event_flag = False

    def to_screen_pos(self, pos):
        if lcd.screen:
            rect = lcd.screen.get_rect()
            rect.center = pg.display.get_surface().get_rect().center
            if rect.collidepoint(pos):
                out = pos[0] - rect.left, pos[1] - rect.top
                return out
        return None

    def activate_irq(self, irq_pin):
        pass

    def current_point(self):
        return (
            self.to_screen_pos(pg.mouse.get_pos())
            if pg.mouse.get_pressed()[0]
            else None
        )

    def trigger_event(self):
        self.event_flag = True
        self.irq_point = self.current_point()

    def event(self):
        if sequence_executor and sequence_executor.touch_pos is not None:
            sequence_executor.touch_pos = None
            return True
        flag = self.event_flag
        self.event_flag = False  # Always clean event flag
        return flag

    def threshold(self, value):
        pass


touch_control = FT6X36()


if "krux.touchscreens.ft6x36" not in sys.modules:
    sys.modules["krux.touchscreens.ft6x36"] = mock.MagicMock(
        touch_control=touch_control,
    )
