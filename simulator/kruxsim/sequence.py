from collections import deque
import os
import time
import pygame as pg
import PIL
import PIL.Image
from kruxsim import events

COMMANDS = ["press", "qrcode", "screenshot", "wait", "include", "x"]


class SequenceExecutor:
    def __init__(self, sequence_filepath):
        self.filepath = sequence_filepath
        self.commands = deque(load_commands(self.filepath))
        self.commands.append(("wait", ["1"]))
        self.command = None
        self.command_params = []
        self.command_fn = None
        self.command_timer = 0
        self.key = None
        self.key_press_timer = 0
        self.camera_image = None

    def execute(self):
        if self.command_fn:
            if time.time() - self.command_timer > 0.5:
                print("Executing (%s, %r)" % (self.command, self.command_params))
                self.command_timer = 0
                self.command_fn()
                self.command_fn = None
                self.command_params = []
        elif self.commands:
            cmd, params = self.commands.popleft()
            self.command_timer = time.time()
            self.command = cmd
            self.command_params = params
            if cmd == "press":
                self.command_fn = self.press_key
            elif cmd == "qrcode":
                self.command_fn = self.show_qrcode
            elif cmd == "screenshot":
                self.command_fn = self.request_screenshot
            elif cmd == "wait":
                self.command_timer += float(params[0])
                self.command_fn = self.wait

    def press_key(self):
        key = self.command_params[0]
        self.key = None
        self.key_press_timer = time.time()
        if key == "BUTTON_A":
            self.key = pg.K_RETURN
        elif key == "BUTTON_B":
            self.key = pg.K_SPACE

    def show_qrcode(self):
        filename = self.command_params[0]
        self.camera_image = PIL.Image.open(
            os.path.join(os.path.dirname(self.filepath), "qrcodes", filename)
        )

    def request_screenshot(self):
        filename = self.command_params[0]
        pg.event.post(pg.event.Event(events.SCREENSHOT_EVENT, {"filename": filename}))

    def wait(self):
        pass


def load_commands(sequence_filepath):
    commands = []
    with open(sequence_filepath, "r") as sequence_file:
        raw_commands = sequence_file.readlines()
        for raw_command in raw_commands:
            if not any(raw_command.startswith(cmd) for cmd in COMMANDS):
                continue
            num_times = 1
            if raw_command.startswith("x"):
                num_times = int(raw_command[1:].split()[0])
                raw_command = raw_command.split(" ", 1)[1]
            cmd_parts = raw_command.strip().split()
            cmd = cmd_parts[0]
            params = cmd_parts[1:] if len(cmd_parts) > 1 else []
            for _ in range(num_times):
                if cmd == "include":
                    commands.extend(
                        load_commands(
                            os.path.join(os.path.dirname(sequence_filepath), params[0])
                        )
                    )
                else:
                    commands.append((cmd, params))
    return commands
