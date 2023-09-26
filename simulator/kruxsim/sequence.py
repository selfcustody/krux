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
from collections import deque
import os
import time
import pygame as pg
import cv2
from kruxsim import events
from kruxsim.mocks.board import BOARD_CONFIG

COMMANDS = ["press", "touch", "qrcode", "screenshot", "wait", "include", "x"]
THREAD_PERIOD = 0.1


class SequenceExecutor:
    def __init__(self, sequence_filepath):
        self.filepath = sequence_filepath
        self.command = None
        self.command_params = []
        self.command_fn = None
        self.command_timer = 0
        self.key = None
        self.key_checks = 0
        self.touch_pos = None
        self.touch_checks = 0
        self.camera_image = None
        commands = load_commands(self.filepath)
        if commands[0][0] == "wait" and BOARD_CONFIG["krux"]["display"]["touch"]:
            commands = commands[0:1] + [("press", ["BUTTON_A"])] + commands[1:]
        commands.append(("wait", ["1"]))
        self.commands = deque(commands)

    def execute(self):
        if self.command_fn:
            if time.time() > self.command_timer + THREAD_PERIOD:
                print("Executing (%s, %r)" % (self.command, self.command_params))
                self.command_timer = time.time()
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
            elif cmd == "touch":
                self.command_fn = self.touch
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
        self.key_checks = 0
        if key == "BUTTON_A":
            self.key = pg.K_RETURN
        elif key == "BUTTON_B":
            self.key = pg.K_DOWN
        elif key == "BUTTON_C":
            self.key = pg.K_UP

    def touch(self):
        self.touch_pos = (self.command_params[0], self.command_params[1])
        self.touch_checks = 0

    def show_qrcode(self):
        filename = self.command_params[0]
        self.camera_image = cv2.imread(
            os.path.join(os.path.dirname(self.filepath), "qrcodes", filename),
            cv2.IMREAD_COLOR,
        )

    def request_screenshot(self):
        filename = self.command_params[0]
        pg.event.post(pg.event.Event(events.SCREENSHOT_EVENT, {"filename": filename}))

    def wait(self):
        pass


def load_commands(sequence_filepath):
    commands = []

    # If the sequence doesn't exist, it may be board-specific; look for it within a subfolder named for the board
    filepath = sequence_filepath
    if not os.path.exists(filepath):
        filepath = os.path.join(
            os.path.dirname(sequence_filepath),
            BOARD_CONFIG["type"],
            os.path.basename(sequence_filepath),
        )

    with open(filepath, "r") as sequence_file:
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
