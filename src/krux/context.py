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

SCREENSAVER_ANIMATION_TIME = 50
# adicionei 12 espaços nas primeiras linhas
# adicionei 3 linhas abaixo
SCREENSAVER_BLANK_LINE = "                                 "
SCREENSAVER = """
      ██                  
      ██                  
      ██                  
    ██████                
      ██                  
      ██  ██              
      ██ ██               
      ████                
      ██ ██               
      ██  ██              
      ██   ██             
"""[1:-1].split("\n")
SCREENSAVER_SIZE = len(SCREENSAVER)
SCREENSAVER = [SCREENSAVER_BLANK_LINE, SCREENSAVER_BLANK_LINE, SCREENSAVER_BLANK_LINE] + SCREENSAVER + [SCREENSAVER_BLANK_LINE, SCREENSAVER_BLANK_LINE, SCREENSAVER_BLANK_LINE, SCREENSAVER_BLANK_LINE, SCREENSAVER_BLANK_LINE, SCREENSAVER_BLANK_LINE]


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
        print("screensaver context!")

        anim_curr_text = ""
        anim_frame = 0
        screensaver_time = 0

        fg_color = theme.fg_color
        bg_color = theme.bg_color

        self.display.clear()

        while True:            
            if (screensaver_time + SCREENSAVER_ANIMATION_TIME < time.ticks_ms()):
                if (anim_frame < SCREENSAVER_SIZE*2):
                    anim_frame = anim_frame + 1
                else:
                    anim_frame = 1
                    tmp_color = bg_color
                    bg_color = fg_color
                    fg_color = tmp_color

                # show animation on the screeen
                anim_curr_text = SCREENSAVER[0:anim_frame]
                self.display.draw_hcentered_text(anim_curr_text, color=fg_color, bg_color=bg_color)
                
                screensaver_time = time.ticks_ms()
            
            if (self.input.wait_for_press(block=False) != None):
                print("break screensaver")
                break
            

            
