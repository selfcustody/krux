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
from importlib import util
from unittest import mock
from kruxsim import devices

BOARD_CONFIG = None
BUTTON_A = None
BUTTON_B = None
BUTTON_C = None


# From: https://stackoverflow.com/a/59937532
def load_file_as_module(name, location):
    spec = util.spec_from_file_location(name, location)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def register_device(device):
    global BOARD_CONFIG
    global BUTTON_A
    global BUTTON_B
    global BUTTON_C
    project = devices.AMIGO_TFT if device == devices.PC else device
    BOARD_CONFIG = load_file_as_module(
        "board", "../firmware/MaixPy/projects/%s/builtin_py/board.py" % project
    ).config
    if "LED_W" in BOARD_CONFIG["krux"]["pins"]:
        del BOARD_CONFIG["krux"]["pins"]["LED_W"]
    if device == devices.PC:
        BOARD_CONFIG["type"] = "pc"
        BOARD_CONFIG["lcd"]["height"] = devices.WINDOW_SIZES[device][0]
        BOARD_CONFIG["lcd"]["width"] = devices.WINDOW_SIZES[device][1]

    sys.modules["board"] = mock.MagicMock(config=BOARD_CONFIG)

    BUTTON_A = BOARD_CONFIG["krux"]["pins"]["BUTTON_A"]
    if "ENCODER" in BOARD_CONFIG["krux"]["pins"]:
        # replace encoder with regular buttons in simulator
        del BOARD_CONFIG["krux"]["pins"]["ENCODER"]
        BOARD_CONFIG["krux"]["pins"]["BUTTON_B"] = 37
        BOARD_CONFIG["krux"]["pins"]["BUTTON_C"] = 38
    BUTTON_B = BOARD_CONFIG["krux"]["pins"]["BUTTON_B"]
    if "BUTTON_C" in BOARD_CONFIG["krux"]["pins"]:
        BUTTON_C = BOARD_CONFIG["krux"]["pins"]["BUTTON_C"]
