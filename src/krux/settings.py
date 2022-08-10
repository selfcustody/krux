# The MIT License (MIT)

# Copyright (c) 2021-2022 Krux contributors

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
try:
    import ujson as json
except ImportError:
    import json

SETTINGS_FILE = "/sd/settings.json"


class Store:
    """Acts as a simple JSON file store for settings, falling back to an in-memory dict if no SD"""

    def __init__(self):
        self.settings = {}
        try:
            self.settings = json.load(open(SETTINGS_FILE, "r"))
        except:
            pass

    def get(self, namespace, setting_name, default_value):
        """Loads a setting under the given namespace, returning the default value if not set"""
        s = self.settings
        for level in namespace.split("."):
            s[level] = s.get(level, {})
            s = s[level]
        if setting_name not in s:
            self.set(namespace, setting_name, default_value)
        return s[setting_name]

    def set(self, namespace, setting_name, setting_value):
        """Stores a setting value under the given namespace"""
        s = self.settings
        for level in namespace.split("."):
            s[level] = s.get(level, {})
            s = s[level]
        s[setting_name] = setting_value
        try:
            json.dump(self.settings, open(SETTINGS_FILE, "w"))
        except:
            pass


# Initialize singleton
store = Store()


class Setting:
    """Implements the descriptor protocol for reading and writing a single setting"""

    def __init__(self, attr, default_value):
        self.attr = attr
        self.default_value = default_value

    def __get__(self, obj, objtype=None):
        return store.get(obj.namespace, self.attr, self.default_value)

    def __set__(self, obj, value):
        store.set(obj.namespace, self.attr, value)


class Settings:
    """Stores configurable user settings"""

    namespace = "settings"
    networks = ["main", "test"]
    network = Setting("network", "main")

    def __init__(self):
        self.i18n = I18n()
        self.log = Log()
        self.printer = Printer()


class I18n:
    """I18n-specific settings"""

    namespace = "settings.i18n"
    locales = ["de-DE", "en-US", "es-MX", "fr-FR", "pt-BR", "vi-VN"]
    locale = Setting("locale", "en-US")


class Log:
    """Log-specific settings"""

    namespace = "settings.log"
    path = Setting("path", "/sd/.krux.log")
    level = Setting("level", 99)


class Printer:
    """Printer-specific settings"""

    namespace = "settings.printer"
    module = Setting("module", "thermal")
    cls = Setting("cls", "AdafruitPrinter")

    def __init__(self):
        self.thermal = Thermal()


class Thermal:
    """Thermal printer settings"""

    namespace = "settings.printer.thermal"
    baudrates = [9600, 19200]
    baudrate = Setting("baudrate", 9600)
    paper_width = Setting("paper_width", 384)


# Initialize singleton
settings = Settings()
