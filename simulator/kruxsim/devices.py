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
import os
import pygame as pg

M5STICKV = "maixpy_m5stickv"
AMIGO_IPS = "maixpy_amigo_ips"
AMIGO_TFT = "maixpy_amigo_tft"
PC = "maixpy_pc"
DOCK = "maixpy_dock"

WINDOW_SIZES = {
    M5STICKV: (320, 640),
    AMIGO_IPS: (480, 768),
    AMIGO_TFT: (480, 768),
    PC: (480, 640),
    DOCK: (440, 820),
}

##################################
# Handle absolute path of assets #
##################################
dirname = os.path.dirname(os.path.abspath(__file__))

def with_prefix(device: str):
    """
    Add prefix to device name. If its a maixpy one, add `maixpy_` string.
    
    :param device
    :return str
    """
    return device if device.startswith("maixpy_") else "maixpy_" + device


images = {}

def load_image(device: str):
    """
    Load an image asset as :mod:`pygame.Surface`

    :param device
    :return pygame.Surface
    """
    device = with_prefix(device)
    if device == PC:
        return None
    if device not in images:
        asset_path = os.path.abspath(f"{dirname}/../assets/{device}.png")
        images[device] = pg.image.load(asset_path).convert_alpha()
    return images[device]


fonts = {}


def load_font(device: str):
    """
    Load a :mod:`pygame.freetype.Font`

    :param device: str
    :return pygame.freetype.Font
    """
    device = with_prefix(device)
    if device not in fonts:
        # Get the current dir of current file
        # to dynamically get the absolute path of bdf font
        dirname = os.path.dirname(os.path.abspath(__file__))

        # now get the bdf font
        if device == M5STICKV:
            ter_u14n_path = os.path.abspath(f"{dirname}/../../firmware/font/ter-u14n.bdf")
            fonts[device] = pg.freetype.Font(ter_u14n_path)
        elif device == DOCK:
            ter_u16n_path = os.path.abspath(f"{dirname}/../../firmware/font/ter-u16n.bdf")
            fonts[device] = pg.freetype.Font(ter_u16n_path)
        else:
            ter_u24b_path = os.path.abspath(f"{dirname}/../../firmware/font/ter-u24b.bdf")
            fonts[device] = pg.freetype.Font(ter_u24b_path)

    return fonts[device]


def screenshot_rect(device: str):
    """
    Make a :class:`pygame.Surface` screenshot

    :param device: str
    :return pygame.Surface  
    """
    screen = pg.display.get_surface()
    if device == PC:
        return screen.get_rect()

    rect = load_image(device).get_rect()
    if device == M5STICKV:
        rect.width -= 20
        rect.height -= 205
        rect.center = (
            screen.get_rect().center[0] - 1,
            screen.get_rect().center[1] + 57,
        )
    elif device == AMIGO_IPS or device == AMIGO_TFT:
        rect.width -= 370
        rect.height -= 95
        rect.center = (
            screen.get_rect().center[0],
            screen.get_rect().center[1],
        )
    return rect
