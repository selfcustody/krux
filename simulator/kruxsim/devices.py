import os
import pygame as pg

M5STICKV = "maixpy_m5stickv"
AMIGO = "maixpy_amigo_ips"
PC = "maixpy_pc"

WINDOW_SIZES = {
    M5STICKV: (320, 640),
    AMIGO: (480, 768),
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
        images[device] = pg.image.load(os.path.join("assets", "%s.png" % device)).convert_alpha()
    return images[device]

fonts = {}
def load_font(device):
    device = with_prefix(device)
    if device not in fonts:
        size = 16 if device == M5STICKV else 24
        fonts[device] = pg.font.Font(
            os.path.join("assets", "Terminess (TTF) Nerd Font Complete Mono.ttf"), size
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
    elif device == AMIGO:
        rect.width -= 370
        rect.height -= 95
        rect.center = (
            screen.get_rect().center[0],
            screen.get_rect().center[1],
        )
    return rect