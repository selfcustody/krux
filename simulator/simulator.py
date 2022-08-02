import os
import sys
import argparse
import threading
import pygame as pg
from kruxsim import devices, events

parser = argparse.ArgumentParser()
parser.add_argument("--device", type=str, default=devices.PC, required=False)
parser.add_argument("--with-printer", type=bool, default=False, required=False)
parser.add_argument("--with-sd", type=bool, default=False, required=False)
parser.add_argument("--sequence", type=str, default="", required=False)
parser.add_argument("--exit-after-sequence", type=bool, default=True, required=False)
args = parser.parse_args()

pg.init()
pg.freetype.init()

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
from kruxsim.mocks import pmu

if args.with_printer:
    machine.simulate_printer()

from kruxsim.mocks import secp256k1
from kruxsim.mocks import qrcode
from kruxsim.mocks import sensor
from kruxsim.mocks import lcd
from kruxsim.mocks import ft6x36
from kruxsim.sequence import SequenceExecutor

sequence_executor = None
if args.sequence:
    sequence_executor = SequenceExecutor(args.sequence)

Maix.register_sequence_executor(sequence_executor)
sensor.register_sequence_executor(sequence_executor)
ft6x36.register_sequence_executor(sequence_executor)

def run_krux():
    with open("../src/boot.py") as boot_file:
        exec(boot_file.read())

t = threading.Thread(target=run_krux)
t.daemon = True

screen = pg.display.set_mode(devices.WINDOW_SIZES[args.device], pg.SCALED)
screen.fill(lcd.COLOR_BLACK)
buffer_image = screen.copy().convert()

pg.display.set_caption("Krux Simulator")

device_image = devices.load_image(args.device)

t.start()

def shutdown():
    if t.is_alive():
        t.alive = False
    
    pg.quit()
    sys.exit()
    
try:
    while True:
        if sequence_executor:
            if not sequence_executor.commands and args.exit_after_sequence:
                shutdown()
            sequence_executor.execute()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                shutdown()
            elif event.type >= pg.USEREVENT:
                if event.type == events.SCREENSHOT_EVENT:
                    sub = screen.subsurface(devices.screenshot_rect(args.device))
                    pg.image.save(sub, os.path.join("screenshots", event.dict["filename"]))
                else:
                    event.dict["f"]()
                
        if lcd.screen:
            lcd_rect = lcd.screen.get_rect()
            lcd_rect.center = buffer_image.get_rect().center
            buffer_image.blit(lcd.screen, lcd_rect)

        if device_image:
            device_rect = device_image.get_rect()
            device_rect.center = buffer_image.get_rect().center
            buffer_image.blit(device_image, device_rect)

        scaled_image = buffer_image
        scaled_rect = scaled_image.get_rect()
        scaled_rect.center = buffer_image.get_rect().center
        if args.device == devices.M5STICKV:
            scaled_image = pg.transform.smoothscale(
                buffer_image, (screen.get_width() * 0.95, screen.get_height() * 0.85)
            )
            scaled_rect = scaled_image.get_rect()
            scaled_rect.center = buffer_image.get_rect().center
        screen.blit(scaled_image, scaled_rect)

        pg.display.flip()
except KeyboardInterrupt:
    shutdown()