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
import math
from unittest import mock
import pygame as pg
import cv2
from kruxsim import events
from kruxsim.mocks.board import BOARD_CONFIG

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

WIDTH = BOARD_CONFIG["lcd"]["width"]
HEIGHT = BOARD_CONFIG["lcd"]["height"]

screen = None
portrait = True
landscape = False


def rgb565torgb888(color):
    """convert from gggbbbbbrrrrrggg to tuple"""
    MASK5 = 0b11111
    MASK3 = 0b111

    red = (color >> 3) & MASK5
    red *= 255
    red //= 31
    green = color >> 13
    green += (color & MASK3) << 3
    green *= 255
    green //= 63
    blue = (color >> 8) & MASK5
    blue *= 255
    blue //= 31
    return (red, green, blue)


def clear(color):
    def run():
        if screen:
            screen.fill(color)

    color = rgb565torgb888(color)
    pg.event.post(pg.event.Event(events.LCD_CLEAR_EVENT, {"f": run}))


def init(*args, **kwargs):
    pass


def register(addr, val):
    pass


def display(img, oft=(0, 0), roi=None):
    if roi:
        image_width = roi[3]
        image_height = roi[2]
    else:
        image_width = 240
        image_height = 320
    

    def run():
        try:
            frame = img.get_frame()
            frame = cv2.resize(
                frame,
                (image_width, image_height),
                interpolation=cv2.INTER_AREA,
            )
            frame = frame.swapaxes(0, 1)
        except:
            return

        # Create a surface for the frame
        frame_surface = pg.surfarray.make_surface(frame)

        # Blit this surface onto the screen at the specified offset
        screen.blit(frame_surface, oft)

    pg.event.post(pg.event.Event(events.LCD_DISPLAY_EVENT, {"f": run}))


def rotation(r):
    global screen
    global portrait
    global landscape

    def run():
        global screen
        global portrait
        global landscape
        if not screen:
            portrait = True
            screen = pg.Surface((HEIGHT, WIDTH)).convert()
        if r == 2:
            landscape = True
        else:
            landscape = False

    pg.event.post(pg.event.Event(events.LCD_ROTATION_EVENT, {"f": run}))


def width():
    return HEIGHT if portrait else WIDTH


def height():
    return WIDTH if portrait else HEIGHT


def draw_string(x, y, s, color, bgcolor=COLOR_BLACK):
    def run():
        from kruxsim import devices

        text, _ = devices.load_font(BOARD_CONFIG["type"]).render(s, color, bgcolor)
        if landscape:
            text = pg.transform.rotate(text, 90)
            screen.blit(
                text,
                (
                    height() - text.get_width() - y
                    if BOARD_CONFIG["krux"]["display"]["inverted_coordinates"]
                    else y,
                    x,
                ),
            )
        else:
            screen.blit(
                text,
                (
                    width() - text.get_width() - x
                    if BOARD_CONFIG["krux"]["display"]["inverted_coordinates"]
                    else x,
                    y,
                ),
            )

    color = rgb565torgb888(color)
    bgcolor = rgb565torgb888(bgcolor)
    pg.event.post(pg.event.Event(events.LCD_DRAW_STRING_EVENT, {"f": run}))


def draw_qr_code(offset_y, code_str, max_width, dark_color, light_color, background):
    def run():
        starting_size = 0
        while code_str[starting_size] != "\n":
            starting_size += 1
        scale = max_width // starting_size
        qr_width = starting_size * scale
        offset = (max_width - qr_width) // 2
        for og_y in range(starting_size):
            for i in range(scale):
                y = og_y * scale + i
                for og_x in range(starting_size):
                    for j in range(scale):
                        x = og_x * scale + j
                        og_yx_index = og_y * (starting_size + 1) + og_x
                        screen.set_at(
                            (offset + x, offset + offset_y + y),
                            dark_color if code_str[og_yx_index] == "1" else light_color,
                        )

    dark_color = rgb565torgb888(dark_color)
    light_color = rgb565torgb888(light_color)
    pg.event.post(pg.event.Event(events.LCD_DRAW_QR_CODE_EVENT, {"f": run}))

def draw_qr_code_binary(offset_y, code_bin, max_width, dark_color, light_color, background):
    def run():
        starting_size = int(math.sqrt(len(code_bin) * 8))
        block_size_divisor = starting_size + 2;  # adds 2 to create room for a 1 block border
        scale = max_width // block_size_divisor
        width = starting_size * scale
        border_size = (max_width - width) // 2
        opposite_border_offset = border_size + width - 1
        # Top border
        for rx in range(max_width):
            for ry in range(border_size):
                screen.set_at((rx, ry),light_color)

        # Bottom border
        for rx in range(max_width):
            for ry in range(opposite_border_offset, max_width):
                screen.set_at((rx, ry),light_color)

        # Left border
        for rx in range(border_size):
            for ry in range(border_size, opposite_border_offset):
                screen.set_at((rx, ry),light_color)

        # Right border
        for rx in range(opposite_border_offset, max_width):
            for ry in range(border_size, opposite_border_offset):
                screen.set_at((rx, ry),light_color)
        # QR code rendering
        for og_y in range(starting_size):
            for og_x in range(starting_size):
                og_yx_index = og_y * starting_size + og_x
                color_byte = code_bin[og_yx_index >> 3]
                color_byte &= (1 << (og_yx_index % 8))
                color = dark_color if color_byte else light_color
                for i in range(scale):
                    y = border_size + og_y * scale + i
                    for j in range(scale):
                        x = border_size + og_x * scale + j
                        screen.set_at((x, y),color)

    dark_color = rgb565torgb888(dark_color)
    light_color = rgb565torgb888(light_color)
    pg.event.post(pg.event.Event(events.LCD_DRAW_QR_CODE_EVENT, {"f": run}))


def fill_rectangle(x, y, w, h, color):
    def run():
        pg.draw.rect(
            screen,
            color,
            (
                width() - w - x
                if BOARD_CONFIG["krux"]["display"]["inverted_coordinates"]
                else x,
                y,
                w,
                h,
            ),
        )

    color = rgb565torgb888(color)
    pg.event.post(pg.event.Event(events.LCD_FILL_RECTANGLE_EVENT, {"f": run}))


if "lcd" not in sys.modules:
    sys.modules["lcd"] = mock.MagicMock(
        init=init,
        register=register,
        display=display,
        clear=clear,
        rotation=rotation,
        width=width,
        height=height,
        draw_string=draw_string,
        draw_qr_code=draw_qr_code,
        draw_qr_code_binary=draw_qr_code_binary,
        fill_rectangle=fill_rectangle,
        BLACK=COLOR_BLACK,
        WHITE=COLOR_WHITE,
    )
