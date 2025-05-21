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
import pygame as pg

# print(pg.USEREVENT, "pg.USEREVENT") #32866
LCD_CLEAR_EVENT = pg.USEREVENT + 1 #32867
LCD_INIT_EVENT = pg.USEREVENT + 2 #32868
LCD_DISPLAY_EVENT = pg.USEREVENT + 3 #32869
LCD_ROTATION_EVENT = pg.USEREVENT + 4 #32870
LCD_DRAW_STRING_EVENT = pg.USEREVENT + 5 #32871
LCD_DRAW_QR_CODE_EVENT = pg.USEREVENT + 6 #32872
LCD_FILL_RECTANGLE_EVENT = pg.USEREVENT + 7
LCD_DRAW_CIRCLE_EVENT = pg.USEREVENT + 8
LCD_DRAW_LINE_EVENT = pg.USEREVENT + 9
LCD_DRAW_OUTLINE_EVENT = pg.USEREVENT + 10

SCREENSHOT_EVENT = pg.USEREVENT + 11
