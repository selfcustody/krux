import os
import pygame as pg

M5STICKV = "maixpy_m5stickv"
AMIGO_IPS = "maixpy_amigo_ips"
AMIGO_TFT = "maixpy_amigo_tft"
PC = "maixpy_pc"

WINDOW_SIZES = {
    M5STICKV: (320, 640),
    AMIGO_IPS: (480, 768),
    AMIGO_TFT: (480, 768),
    PC: (480, 640),
}


def with_prefix(device):
    return device if device.startswith("maixpy_") else "maixpy_" + device


images = {}


def load_image(device):
    device = with_prefix(device)
    if device == PC:
        return None
    if device not in images:
        images[device] = pg.image.load(
            os.path.join("assets", "%s.png" % device)
        ).convert_alpha()
    return images[device]


fonts = {}


def load_font(device):
    device = with_prefix(device)
    if device not in fonts:
        size = 14 if device == M5STICKV else 24
        fonts[device] = pg.freetype.Font(
            os.path.join("..", "firmware", "font", "ter-u%dn.bdf" % size)
        )
    return fonts[device]


def screenshot_rect(device):
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
