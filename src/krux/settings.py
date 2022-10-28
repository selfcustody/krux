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
