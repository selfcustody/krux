# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import time as _time
from unittest.mock import MagicMock

"""
`sphinx-*` tools used on `pyproject.toml` (specificaly, on `readthedocs` poe
task) will execute the to bedocumented code before document it. But some of
them are hardware specific (micropython selfcustody fork) and cannot be loaded.

A way to "skip" them is to mock the libraries that we do not want to execute
(hardware specific, embit, thirdparty, etc). After that we can configure 
so `sphinx` could translate them to html.
"""


# -- Mock hacks----- ---------------------------------------------------------
class MockDisplay:
    """Mock display with proper return types."""

    def height(self):
        return 320

    def width(self):
        return 480

    def draw_centered_text(self, *args, **kwargs):
        pass

    def clear(self):
        pass

    def fill_rectangle(self, *args, **kwargs):
        pass

    def draw_hcentered_text(self, *args, **kwargs):
        pass

    def draw_qr_code(self, *args, **kwargs):
        pass

    def to_landscape(self):
        pass

    def to_portrait(self):
        pass

    def __getattr__(self, name):
        return MagicMock()


class HashableMock:
    """A simple hashable mock that can be used as dictionary keys."""

    _counter = 0

    def __init__(self, name="mock"):
        HashableMock._counter += 1
        self._name = name
        self._id = HashableMock._counter

    def __hash__(self):
        return self._id

    def __eq__(self, other):
        if isinstance(other, HashableMock):
            return self._id == other._id
        return False

    def __repr__(self):
        return f"<HashableMock {self._name}>"

    def __call__(self, *args, **kwargs):
        return HashableMock(self._name)

    def __getattr__(self, name):
        return HashableMock(f"{self._name}.{name}")

    def __int__(self):
        return 0

    def __bool__(self):
        return False


class MockModule(MagicMock):
    """Mock module that returns HashableMock for attributes that might be used as dict keys."""

    # Attributes known to be used as dict keys
    HASHABLE_ATTRS = {
        "MODE_AES",
        "MODE_CTR",
        "MODE_CBC",
        "MODE_ECB",
        "AES",
        "CTR",
        "CBC",
        "ECB",
    }

    def __getattr__(self, name):
        if name in self.HASHABLE_ATTRS or name.startswith("MODE_"):
            return HashableMock(name)
        return MagicMock()


class MockWordlist:
    """Mock for embit.wordlists.bip39.WORDLIST - returns list of strings."""

    WORDLIST = ["abandon"] * 2048  # Dummy wordlist


class MockTime:
    """Mock time module with MicroPython-specific functions."""

    def __getattr__(self, name):
        if hasattr(_time, name):
            return getattr(_time, name)
        return MagicMock()

    @staticmethod
    def ticks_ms():
        return 0

    @staticmethod
    def ticks_us():
        return 0

    @staticmethod
    def ticks_diff(a, b):
        return 0

    @staticmethod
    def ticks_add(a, b):
        return 0

    @staticmethod
    def sleep_ms(ms):
        pass

    @staticmethod
    def sleep_us(us):
        pass


# Create mock for board with required config structure
class MockBoardConfig(dict):
    """Mock board. config as a real dict."""

    def __init__(self):
        super().__init__(
            {
                "type": "rtd",
                "lcd": {
                    "height": 320,
                    "width": 480,
                    "invert": 0,
                    "dir": 40,
                    "lcd_type": 1,
                },
                "sdcard": {"sclk": 11, "mosi": 10, "miso": 6, "cs": 26},
                "board_info": {
                    "BOOT_KEY": 23,
                    "CONNEXT_A": 7,
                    "CONNEXT_B": 9,
                    "LED_R": 14,
                    "LED_G": 15,
                    "LED_B": 17,
                    "LED_W": 32,
                    "BACK": 23,
                    "ENTER": 16,
                    "NEXT": 20,
                    "WIFI_TX": 6,
                    "WIFI_RX": 7,
                    "WIFI_EN": 8,
                    "I2S0_MCLK": 13,
                    "I2S0_SCLK": 21,
                    "I2S0_WS": 18,
                    "I2S0_IN_D0": 35,
                    "I2S0_OUT_D2": 34,
                    "I2C_SDA": 27,
                    "I2C_SCL": 24,
                    "SPI_SCLK": 11,
                    "SPI_MOSI": 10,
                    "SPI_MISO": 6,
                    "SPI_CS": 12,
                },
                "krux": {
                    "pins": {
                        "BUTTON_A": 16,
                        "BUTTON_B": 20,
                        "BUTTON_C": 23,
                        "TOUCH_IRQ": 33,
                        "LED_W": 32,
                        "BACK": 23,
                        "ENTER": 16,
                        "NEXT": 20,
                        "WIFI_TX": 6,
                        "WIFI_RX": 7,
                        "WIFI_EN": 8,
                        "I2C_SDA": 27,
                        "I2C_SCL": 24,
                        "ENCODER": [10, 11],
                    },
                    "display": {"touch": True, "font": [12, 24], "font_wide": [24, 24]},
                },
            }
        )


class MockBoard:
    """Mock board module."""

    config = MockBoardConfig()

    def __getattr__(self, name):
        return MagicMock()


# Create mock instances
MOCK_TIME = MockTime()
MOCK_UCRYPTOLIB = MockModule()
MOCK_UCRYPTOLIB.aes = MockModule()

# Mock for embit.wordlists.bip39
MOCK_BIP39 = type("MockBip39", (), {"WORDLIST": ["abandon"] * 2048})()


def setup_mocks():
    """Setup all mocked modules."""

    mock_display_module = MagicMock()
    mock_display_module.display = MockDisplay()
    mock_display_module.SPLASH = "Krux"
    mock_display_module.FONT_HEIGHT = 24
    mock_display_module.FONT_WIDTH = 12

    mocks = {
        # MicroPython built-ins
        "machine": MagicMock(),
        "board": MockBoard(),
        "pmu": MagicMock(),
        "time": MockTime(),
        "lcd": MagicMock(),
        "ujson": MagicMock(),
        "urandom": MagicMock(),
        "ucryptolib": MockModule(),
        "uhashlib": MagicMock(),
        "uhashlib_hw": MagicMock(),
        "uctypes": MagicMock(),
        "uos": MagicMock(),
        "usys": MagicMock(),
        "gc": MagicMock(),
        # K210/Maix specific
        "Maix": MagicMock(),
        "fpioa_manager": MagicMock(),
        "sensor": MagicMock(),
        "image": MagicMock(),
        "flash": MagicMock(),
        # Crypto/QR
        "secp256k1": MagicMock(),
        "qrcode": MagicMock(),
        # Embit (Bitcoin library)
        "embit": MagicMock(),
        "embit.wordlists": MagicMock(),
        "embit.wordlists.bip39": MockWordlist(),
        "embit.psbt": MagicMock(),
        "embit.networks": MagicMock(),
        "embit.descriptor": MagicMock(),
        "embit.descriptor.descriptor": MagicMock(),
        "embit.descriptor.arguments": MagicMock(),
        # Scientific (if needed)
        "numpy": MagicMock(),
        "scipy": MagicMock(),
        "scipy.linalg": MagicMock(),
        "scipy.signal": MagicMock(),
        # Krux specific
        "krux.display": mock_display_module,
    }

    for mod_name, mock_obj in mocks.items():
        sys.modules[mod_name] = mock_obj


setup_mocks()

# Add source path
sys.path.insert(0, os.path.abspath("../"))
sys.path.insert(0, os.path.abspath("../src/"))

# -- Project information -----------------------------------------------------
project = "Krux"
copyright = "2022, MIT"
author = "Selfcustody"
release = "2022"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
napoleon_google_docstring = False
napoleon_use_param = False
napoleon_use_ivar = True
templates_path = ["_templates"]
exclude_patterns = ["snippets", "_static", "Thumbs.db", ".DS_Store"]

# Suppress warnings
suppress_warnings = ["autodoc", "autodoc.import_object"]

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = []


def skip_mock_members(app, what, name, obj, skip, options):
    """Skip mock objects that can't be documented."""
    if "Mock" in str(type(obj)):
        return True
    return skip


def setup(app):
    app.connect("autodoc-skip-member", skip_mock_members)
