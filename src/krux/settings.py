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
#
# Removed SDHandler dependency, we check for SD remount, just before entering
# the settings view
# from .sd_card import SDHandler

try:
    import ujson as json
except ImportError:
    import json

import os

SETTINGS_FILENAME = "settings.json"
SD_PATH = "sd"
FLASH_PATH = "flash"

# KRUX CUSTOM COLORS
SLATEGRAY = 0x2E5B
DARKGREEN = 0x2005


class SettingsNamespace:
    """Represents a settings namespace containing settings and child namespaces"""

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""
        raise NotImplementedError()

    def namespace_list(self):
        """Returns the list of child SettingsNamespace objects"""
        namespaces = [
            ns for ns in self.__dict__.values() if isinstance(ns, SettingsNamespace)
        ]
        namespaces.sort(key=lambda ns: str(ns.__class__.__name__))
        return namespaces

    def setting_list(self):
        """Returns the list of child Setting objects"""
        settings = [
            getattr(self.__class__, setting)
            for setting in dir(self.__class__)
            if isinstance(getattr(self.__class__, setting), Setting)
        ]
        settings.sort(key=lambda s: s.attr)
        return settings


class Setting:
    """Implements the descriptor protocol for reading and writing a single setting"""

    def __init__(self, attr, default_value):
        self.attr = attr
        self.default_value = default_value

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return store.get(obj.namespace, self.attr, self.default_value)

    def __set__(self, obj, value):
        store.set(obj.namespace, self.attr, value)


class CategorySetting(Setting):
    """Setting that can be one of N categories"""

    def __init__(self, attr, default_value, categories):
        super().__init__(attr, default_value)
        self.categories = categories


class NumberSetting(Setting):
    """Setting that can be a number within a defined range"""

    def __init__(self, numtype, attr, default_value, value_range):
        super().__init__(attr, default_value)
        self.numtype = numtype
        self.value_range = value_range


class Store:
    """Acts as a simple JSON file store for settings, falling back to an in-memory dict if no SD"""

    def __init__(self):
        self.settings = {}
        self.file_location = "/" + FLASH_PATH + "/"

        # Check for the correct settings persist location
        try:
            with open(self.file_location + SETTINGS_FILENAME, "r") as f:
                self.settings = json.loads(f.read())
        except:
            pass

        self.file_location = (
            self.settings.get("settings", {})
            .get("persist", {})
            .get("location", "undefined")
        )

        # Settings file not found on flash, or key is missing
        if self.file_location != FLASH_PATH:
            self.file_location = "/" + SD_PATH + "/"
            try:
                with open(self.file_location + SETTINGS_FILENAME, "r") as f:
                    self.settings = json.loads(f.read())
            except:
                pass

        # Settings file location points to what is defined in SETTINGS_FILENAME or defaults to flash
        self.file_location = (
            "/"
            + self.settings.get("settings", {})
            .get("persist", {})
            .get("location", FLASH_PATH)
            + "/"
        )

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
        """Stores a setting value under the given namespace. We don't use SDHandler
        here because set is called too many times every time the user changes a setting
        and SDHandler remount causes a small delay
        """
        s = self.settings
        for level in namespace.split("."):
            s[level] = s.get(level, {})
            s = s[level]
        old_value = s.get(setting_name, None)
        s[setting_name] = setting_value

        # if is a change in settings persist location, delete file from old location,
        # and later it will save on the new location
        if setting_name == "location" and old_value:
            # update the file location
            self.file_location = "/" + setting_value + "/"
            try:
                # remove old SETTINGS_FILENAME
                os.remove("/" + old_value + "/" + SETTINGS_FILENAME)
            except:
                pass

        Store.save_settings()

    @staticmethod
    def save_settings():
        """Helper to persist SETTINGS_FILENAME where user selected"""
        try:
            # save the new SETTINGS_FILENAME
            with open(store.file_location + SETTINGS_FILENAME, "w") as f:
                f.write(json.dumps(store.settings))
        except:
            pass


# Initialize singleton
store = Store()
