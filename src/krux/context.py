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
import time
import board
from .logging import logger
from .display import Display
from .input import Input
from .camera import Camera
from .light import Light
from .themes import theme

SCREENSAVER_ANIMATION_TIME = 150


class Context:
    """Context is a singleton containing all 'global' state that lives throughout the
    duration of the program, including references to all device interfaces.
    """

    def __init__(self, logo=None):
        self.display = Display()

        if logo is None:
            logo = []
        self.logo = logo
        for _ in range((self.display.total_lines - len(logo)) // 2):
            self.logo.insert(0, "")
            self.logo.append("")
        self.logo.append("")
        self.logo.append("")

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
        screensaver_time = 0

        fg_color = theme.fg_color
        bg_color = theme.bg_color

        self.display.clear()

        while True:
            if screensaver_time + SCREENSAVER_ANIMATION_TIME < time.ticks_ms():
                screensaver_time = time.ticks_ms()

                # show animation on the screeen
                if anim_frame < len(self.logo):
                    self.display.draw_line_hcentered_with_fullw_bg(
                        self.logo[anim_frame], anim_frame, fg_color, bg_color
                    )

                anim_frame = anim_frame + 1
                if anim_frame > len(self.logo) * 1.4:
                    anim_frame = 0
                    bg_color, fg_color = fg_color, bg_color

            if self.input.wait_for_button(block=False) is not None:
                break
