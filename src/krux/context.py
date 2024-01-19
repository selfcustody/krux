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
import gc
import board
from .logging import logger
from .display import Display, SPLASH
from .input import Input
from .camera import Camera
from .light import Light
from .themes import theme


class Context:
    """Context is a singleton containing all 'global' state that lives throughout the
    duration of the program, including references to all device interfaces.
    """

    def __init__(self):
        self.display = Display()
        self.input = Input(screensaver_fallback=self.screensaver)
        self.camera = Camera()
        self.light = Light() if "LED_W" in board.config["krux"]["pins"] else None
        self.power_manager = None
        self.printer = None
        self.wallet = None

    @property
    def log(self):
        """Returns the default logger"""
        return logger

    def clear(self):
        """Clears all sensitive data from the context, resetting it"""
        self.wallet = None
        if self.printer is not None:
            self.printer.clear()
        gc.collect()

    def screensaver(self):
        """Displays a screensaver until user input"""
        anim_frame = 0
        initial_offset = (self.display.total_lines - len(SPLASH)) // 2
        fg_color = theme.fg_color
        bg_color = theme.bg_color
        self.display.clear()
        button_press = None
        while not button_press:
            # show animation on the screeen
            offset_y = anim_frame * self.display.font_height
            self.display.fill_rectangle(
                0, offset_y, self.display.width(), self.display.font_height, bg_color
            )
            if initial_offset <= anim_frame < len(SPLASH) + initial_offset:
                self.display.draw_hcentered_text(
                    SPLASH[anim_frame - initial_offset], offset_y, fg_color, bg_color
                )
            anim_frame += 1
            if anim_frame > len(SPLASH) + 2 * initial_offset:
                anim_frame = 0
                bg_color, fg_color = fg_color, bg_color
            # wait_duration(animation period) can be modified here
            button_press = self.input.wait_for_button(block=False)
