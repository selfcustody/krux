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

from .settings import (
    SettingsNamespace,
    CategorySetting,
    NumberSetting,
    SD_PATH,
    FLASH_PATH,
)
import board
import binascii
from .translations import translation_table

BAUDRATES = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]


DEFAULT_TX_PIN = (
    board.config["board_info"]["CONNEXT_A"]
    if "CONNEXT_A" in board.config["board_info"]
    else 35
)
DEFAULT_RX_PIN = (
    board.config["board_info"]["CONNEXT_B"]
    if "CONNEXT_B" in board.config["board_info"]
    else 34
)

# Encription Versions
PBKDF2_HMAC_ECB = 0
PBKDF2_HMAC_CBC = 1
AES_BLOCK_SIZE = 16

THERMAL_ADAFRUIT_TXT = "thermal/adafruit"


def translations(locale):
    """Returns the translations map for the given locale"""
    if locale in translation_table:
        return translation_table[locale]
    return None


def t(slug):
    """Translates a slug according to the current locale"""
    slug_id = binascii.crc32(slug.encode("utf-8"))
    lookup = translations(Settings().i18n.locale)
    if not lookup or slug_id not in lookup:
        return slug
    return lookup[slug_id]


class BitcoinSettings(SettingsNamespace):
    """Bitcoin-specific settings"""

    MAIN_TXT = "main"
    TEST_TXT = "test"

    namespace = "settings.bitcoin"
    network = CategorySetting("network", MAIN_TXT, [MAIN_TXT, TEST_TXT])

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""
        return {
            "network": t("Network"),
        }[attr]


class LoggingSettings(SettingsNamespace):
    """Log-specific settings"""

    NONE = 99
    ERROR = 40
    WARN = 30
    INFO = 20
    DEBUG = 10
    NONE_TXT = "NONE"
    ERROR_TXT = "ERROR"
    WARN_TXT = "WARN"
    INFO_TXT = "INFO"
    DEBUG_TXT = "DEBUG"
    LEVEL_NAMES = {
        NONE: NONE_TXT,
        ERROR: ERROR_TXT,
        WARN: WARN_TXT,
        INFO: INFO_TXT,
        DEBUG: DEBUG_TXT,
    }

    namespace = "settings.logging"
    level = CategorySetting("level", NONE_TXT, list(LEVEL_NAMES.values()))

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""
        return {
            "level": t("Log Level"),
        }[attr]


class I18nSettings(SettingsNamespace):
    """I18n-specific settings"""

    namespace = "settings.i18n"
    DEFAULT_LOCALE = "en-US"
    locale = CategorySetting(
        "locale", DEFAULT_LOCALE, list(translation_table.keys()) + [DEFAULT_LOCALE]
    )

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""
        return {
            "locale": t("Locale"),
        }[attr]


class ThermalSettings(SettingsNamespace):
    """Thermal printer settings"""

    namespace = "settings.printer.thermal"

    def __init__(self):
        self.adafruit = AdafruitPrinterSettings()

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""
        return {
            "adafruit": t("Adafruit"),
        }[attr]


class AdafruitPrinterSettings(SettingsNamespace):
    """Adafruit thermal printer settings"""

    namespace = "settings.printer.thermal.adafruit"
    baudrate = CategorySetting("baudrate", 9600, BAUDRATES)
    paper_width = NumberSetting(int, "paper_width", 384, [100, 1000])
    tx_pin = NumberSetting(int, "tx_pin", DEFAULT_TX_PIN, [0, 10000])
    rx_pin = NumberSetting(int, "rx_pin", DEFAULT_RX_PIN, [0, 10000])
    line_delay = NumberSetting(int, "line_delay", 20, [0, 255])
    scale = NumberSetting(int, "scale", 75, [25, 100])

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""
        return {
            "baudrate": t("Baudrate"),
            "paper_width": t("Paper Width"),
            "tx_pin": t("TX Pin"),
            "rx_pin": t("RX Pin"),
            "line_delay": t("Line Delay"),
            "scale": t("Scale"),
        }[attr]


class CNCSettings(SettingsNamespace):
    """CNC "printer" settings"""

    namespace = "settings.printer.cnc"
    invert = CategorySetting("invert", False, [False, True])
    cut_method = CategorySetting("cut_method", "spiral", ["spiral", "row"])
    unit = CategorySetting("unit", "in", ["in", "mm"])
    flute_diameter = NumberSetting(float, "flute_diameter", 0.02, [0.0001, 10000])
    plunge_rate = NumberSetting(float, "plunge_rate", 30, [0.0001, 10000])
    feed_rate = NumberSetting(float, "feed_rate", 65, [0.0001, 10000])
    cut_depth = NumberSetting(float, "cut_depth", 0.0625, [0.0001, 10000])
    depth_per_pass = NumberSetting(float, "depth_per_pass", 0.03125, [0.0001, 10000])
    part_size = NumberSetting(float, "part_size", 3.5, [0.0001, 10000])
    border_padding = NumberSetting(float, "border_padding", 0.0625, [0.0001, 10000])

    def __init__(self):
        self.grbl = GRBLSettings()

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""
        return {
            "invert": t("Invert"),
            "cut_method": t("Cut Method"),
            "unit": t("Unit"),
            "flute_diameter": t("Flute Diameter"),
            "plunge_rate": t("Plunge Rate"),
            "feed_rate": t("Feed Rate"),
            "cut_depth": t("Cut Depth"),
            "depth_per_pass": t("Depth Per Pass"),
            "part_size": t("Part Size"),
            "border_padding": t("Border Padding"),
            "grbl": t("GRBL"),
        }[attr]


class GRBLSettings(SettingsNamespace):
    """GRBL settings"""

    namespace = "settings.printer.cnc.grbl"
    baudrate = CategorySetting("baudrate", 115200, BAUDRATES)
    tx_pin = NumberSetting(int, "tx_pin", DEFAULT_TX_PIN, [0, 10000])
    rx_pin = NumberSetting(int, "rx_pin", DEFAULT_RX_PIN, [0, 10000])

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""
        return {
            "baudrate": t("Baudrate"),
            "tx_pin": t("TX Pin"),
            "rx_pin": t("RX Pin"),
        }[attr]


class PrinterSettings(SettingsNamespace):
    """Printer-specific settings"""

    PRINTERS = {
        "none": ("none", None),
        THERMAL_ADAFRUIT_TXT: ("thermal", "AdafruitPrinter"),
        "cnc/file": ("cnc", "FilePrinter"),
    }
    namespace = "settings.printer"
    driver = CategorySetting("driver", "none", list(PRINTERS.keys()))

    def __init__(self):
        self.thermal = ThermalSettings()
        self.cnc = CNCSettings()

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""
        return {
            "thermal": t("Thermal"),
            "driver": t("Driver"),
            "cnc": t("CNC"),
        }[attr]


class EncoderSettings(SettingsNamespace):
    """Encoder debounce settings"""

    namespace = "settings.encoder"
    debounce = NumberSetting(int, "debounce", 100, [100, 250])

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""
        return {
            "debounce": t("Encoder Debounce"),
        }[attr]


class TouchSettings(SettingsNamespace):
    """Touch sensitivity settings"""

    namespace = "settings.touchscreen"
    threshold = NumberSetting(int, "threshold", 22, [10, 200])

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""
        return {
            "threshold": t("Touch Threshold"),
        }[attr]


class HardwareSettings(SettingsNamespace):
    """Hardware Related Settings"""

    namespace = "settings.hardware"

    def __init__(self):
        self.printer = PrinterSettings()
        if (
            board.config["type"].startswith("amigo")
            or board.config["type"] == "yahboom"
        ):
            self.touch = TouchSettings()
        if board.config["type"] == "dock":
            self.encoder = EncoderSettings()

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""

        hardware_menu = {
            "printer": t("Printer"),
        }
        if (
            board.config["type"].startswith("amigo")
            or board.config["type"] == "yahboom"
        ):
            hardware_menu["touchscreen"] = t("Touchscreen")
        if board.config["type"] == "dock":
            hardware_menu["encoder"] = t("Encoder")

        return hardware_menu[attr]


class PersistSettings(SettingsNamespace):
    """Persistent settings"""

    namespace = "settings.persist"
    location = CategorySetting("location", FLASH_PATH, [FLASH_PATH, SD_PATH])

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""
        return {
            "location": t("Location"),
        }[attr]


class EncryptionSettings(SettingsNamespace):
    """Encryption settings"""

    AES_ECB_NAME = "AES-ECB"
    AES_CBC_NAME = "AES-CBC"
    VERSION_NAMES = {
        PBKDF2_HMAC_ECB: AES_ECB_NAME,
        PBKDF2_HMAC_CBC: AES_CBC_NAME,
    }
    namespace = "settings.encryption"
    version = CategorySetting("version", AES_ECB_NAME, list(VERSION_NAMES.values()))
    pbkdf2_iterations = NumberSetting(int, "pbkdf2_iterations", 100000, [1, 500000])

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""
        return {
            "version": t("Encryption Mode"),
            "pbkdf2_iterations": t("PBKDF2 Iter."),
        }[attr]


class ThemeSettings(SettingsNamespace):
    """Theme settings"""

    DARK_THEME = 0
    LIGHT_THEME = 1
    ORANGE_THEME = 3
    GREEN_THEME = 4
    PINK_THEME = 5
    DARK_THEME_NAME = "Dark"
    LIGHT_THEME_NAME = "Light"
    ORANGE_THEME_NAME = "Orange"
    GREEN_THEME_NAME = "CypherPunk"
    PINK_THEME_NAME = "CypherPink"
    THEME_NAMES = {
        DARK_THEME: DARK_THEME_NAME,
        LIGHT_THEME: LIGHT_THEME_NAME,
        ORANGE_THEME: ORANGE_THEME_NAME,
        GREEN_THEME: GREEN_THEME_NAME,
        PINK_THEME: PINK_THEME_NAME,
    }
    namespace = "settings.appearance"
    theme = CategorySetting("theme", DARK_THEME_NAME, list(THEME_NAMES.values()))
    screensaver_time = NumberSetting(int, "screensaver_time", 5, [0, 30])

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""
        return {
            "theme": t("Theme"),
            "screensaver_time": t("Screensaver time"),
        }[attr]


class Settings(SettingsNamespace):
    """The top-level settings namespace under which other namespaces reside"""

    namespace = "settings"

    def __init__(self):
        self.bitcoin = BitcoinSettings()
        self.hardware = HardwareSettings()
        self.i18n = I18nSettings()
        self.logging = LoggingSettings()
        self.encryption = EncryptionSettings()
        self.persist = PersistSettings()
        self.appearance = ThemeSettings()

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""
        main_menu = {
            "bitcoin": t("Bitcoin"),
            "hardware": t("Hardware"),
            "i18n": t("Language"),
            "logging": t("Logging"),
            "encryption": t("Encryption"),
            "persist": t("Persist"),
            "appearance": t("Appearance"),
        }

        return main_menu[attr]
