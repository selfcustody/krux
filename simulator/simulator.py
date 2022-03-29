import os
import sys
import argparse
import threading
import pygame as pg
from kruxsim import devices, events
from kruxsim.sequence import SequenceExecutor

parser = argparse.ArgumentParser()
parser.add_argument("--device", type=str, default=devices.M5STICKV, required=False)
parser.add_argument("--with-printer", type=bool, default=False, required=False)
parser.add_argument("--with-sd", type=bool, default=False, required=False)
parser.add_argument("--sequence", type=str, default="", required=False)
parser.add_argument("--exit-after-sequence", type=bool, default=True, required=False)
args = parser.parse_args()

sequence_executor = None
if args.sequence:
    sequence_executor = SequenceExecutor(args.sequence)

pg.init()

from kruxsim.mocks import board

board.register_device(args.device)

if args.with_sd:
    from kruxsim.mocks import uopen

from kruxsim.mocks import usys
from kruxsim.mocks import utime
from kruxsim.mocks import fpioa_manager
from kruxsim.mocks import Maix
from kruxsim.mocks import flash
from kruxsim.mocks import machine

if args.with_printer:
    machine.simulate_printer()

from kruxsim.mocks import secp256k1
from kruxsim.mocks import qrcode
from kruxsim.mocks import sensor
from kruxsim.mocks import lcd

Maix.register_sequence_executor(sequence_executor)
sensor.register_sequence_executor(sequence_executor)


def run_krux():
    with open("../src/boot.py") as boot_file:
        exec(boot_file.read())


t = threading.Thread(target=run_krux)
t.daemon = True

screen = pg.display.set_mode((1024, 768), pg.SCALED)
screen.fill(lcd.COLOR_BLACK)
buffer_image = screen.copy()

pg.display.set_caption("Krux Simulator")

device_image = pg.image.load(
    os.path.join("assets", "%s.png" % args.device)
).convert_alpha()

clock = pg.time.Clock()
t.start()
while True:
    clock.tick(30)

    if sequence_executor:
        if not sequence_executor.commands and args.exit_after_sequence:
            pg.quit()
            sys.exit()
        sequence_executor.execute()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type >= pg.USEREVENT:
            if event.type == events.SCREENSHOT_EVENT:
                rect = device_image.get_rect()
                if args.device == devices.M5STICKV:
                    rect.width -= 20
                    rect.height -= 205
                    rect.center = (
                        screen.get_rect().center[0] - 1,
                        screen.get_rect().center[1] + 57,
                    )
                sub = screen.subsurface(rect)
                pg.image.save(sub, os.path.join("screenshots", event.dict["filename"]))
            else:
                event.dict["f"]()

    if lcd.screen:
        lcd_rect = lcd.screen.get_rect()
        lcd_rect.center = buffer_image.get_rect().center
        buffer_image.blit(lcd.screen, lcd_rect)

    device_rect = device_image.get_rect()
    device_rect.center = buffer_image.get_rect().center
    buffer_image.blit(device_image, device_rect)

    scaled_image = buffer_image
    if args.device == devices.M5STICKV:
        scaled_image = pg.transform.smoothscale(
            buffer_image, (screen.get_width() * 0.95, screen.get_height() * 0.85)
        )
        scaled_rect = scaled_image.get_rect()
        scaled_rect.center = buffer_image.get_rect().center

    screen.blit(scaled_image, scaled_rect)

    pg.display.flip()
