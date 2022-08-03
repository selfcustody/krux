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
    BUTTON_B = BOARD_CONFIG["krux"]["pins"]["BUTTON_B"]
    if "BUTTON_C" in BOARD_CONFIG["krux"]["pins"]:
        BUTTON_C = BOARD_CONFIG["krux"]["pins"]["BUTTON_C"]
