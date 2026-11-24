# The MIT License (MIT)

# Copyright (c) 2021-2024 Krux contributors

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

import ujson as json
import os

# Settings storage
SD_PATH = "sd"
FLASH_PATH = "flash"

# Specific storage filenames
SETTINGS_FILENAME = "settings.json"
MNEMONICS_FILE = "seeds.json"

# Namespaces that decide how the device protects itself and where secrets can
# be sent. They are always read from and written to internal flash, so a
# settings.json on an SD card can never supply them.
FLASH_ONLY_NAMESPACES = ("security", "encryption", "printer")

# Maximum accepted size of settings.json (bytes). Guards against malicious
# oversized files on SD that could exhaust RAM during load.
MAX_SETTINGS_FILE_SIZE = 8192

# Network settings
MAIN_TXT = "main"
TEST_TXT = "test"

THIN_SPACE = " "  # "\u2009"
ELLIPSIS = "…"  # "\u2026"


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

    def __get__(self, obj, _objtype=None):
        if obj is None:
            return self
        return store.get(obj.namespace, self.attr, self.default_value)

    def __set__(self, obj, value):
        if self.attr == "location":
            store.update_file_location(value)
        if value == self.default_value:
            store.delete(obj.namespace, self.attr)  # do not store defaults
        else:
            store.set(obj.namespace, self.attr, value)  # do store custom settings


class CategorySetting(Setting):
    """Setting that can be one of N categories"""

    def __init__(self, attr, default_value, categories):
        super().__init__(attr, default_value)
        self.categories = categories

    def __get__(self, obj, _objtype=None):
        if obj is None:
            return self

        stored_val = store.get(obj.namespace, self.attr, self.default_value)
        if stored_val not in self.categories:
            return self.default_value
        return stored_val


class LinkedCategorySetting(CategorySetting):
    """CategorySetting that can be linked to another CategorySetting to limit options"""

    def __init__(self, attr, default_value, categories, linked_setting, *args):
        super().__init__(attr, default_value, categories)
        self.linked_setting = linked_setting
        self.conditions = [fn for fn in args if callable(fn)]

    def __get__(self, obj, _objtype=None):
        if obj is None:
            return self

        stored_val = store.get(obj.namespace, self.attr, self.default_value)

        for condition in self.conditions:
            categories, default_value = condition(stored_val, self.linked_setting)
            self.linked_setting.categories = categories
            self.linked_setting.default_value = default_value

        if stored_val not in self.categories:
            return self.default_value
        return stored_val


class NumberSetting(Setting):
    """Setting that can be a number within a defined range"""

    def __init__(
        self, numtype, attr, default_value, value_range, unit=None, show_range=False
    ):
        super().__init__(attr, default_value)
        self.numtype = numtype
        self.value_range = value_range
        self.unit = unit
        self.show_range = show_range or unit is not None

    def __get__(self, obj, _objtype=None):
        if obj is None:
            return self

        stored_val = store.get(obj.namespace, self.attr, self.default_value)
        if (
            (self.numtype is int and isinstance(stored_val, self.numtype))
            or (self.numtype is float and isinstance(stored_val, (self.numtype, int)))
        ) and self.value_range[0] <= stored_val <= self.value_range[1]:
            return stored_val

        return self.default_value


class Store:
    """Acts as a simple JSON file store for settings, falling back to an in-memory dict if no SD"""

    def __init__(self):
        self.settings = {}
        self.dirty = False

        # Read both files up front; each read starts from an empty dict, so a
        # failed read can never leave another file's content in place
        self.file_location = Store.get_vfs_location(FLASH_PATH)
        self._load_settings()
        flash_settings = self.settings

        self.settings = {}
        self.file_location = Store.get_vfs_location(SD_PATH)
        self._load_settings()

        if self._persisted_location("undefined") == SD_PATH:
            # The card is the chosen persist location. The protected
            # namespaces still come from flash only.
            self._use_flash_only_namespaces(flash_settings)
        else:
            # Settings not found on SD, or 'persist.location' key not defined
            self.settings = flash_settings

        # Settings persist location will point to SD (if defined) else defaults to flash
        self.file_location = Store.get_vfs_location(
            self._persisted_location(FLASH_PATH)
        )

    def _persisted_location(self, default):
        """Reads persist.location defensively; returns a known path or default."""
        # A corrupted/hand-edited file may have a non-dict at any namespace level
        # or a bogus location value — walk defensively and validate before returning.
        node = self.settings
        for level in ("settings", "persist"):
            if not isinstance(node, dict):
                return default
            node = node.get(level)
        if not isinstance(node, dict):
            return default
        location = node.get("location", default)
        if location not in (SD_PATH, FLASH_PATH):
            return default
        return location

    def _use_flash_only_namespaces(self, flash_settings):
        """Replaces the protected namespaces with the ones stored in flash"""
        if not isinstance(self.settings.get("settings"), dict):
            self.settings["settings"] = {}
        node = self.settings["settings"]
        source = flash_settings.get("settings")
        if not isinstance(source, dict):
            source = {}
        for namespace in FLASH_ONLY_NAMESPACES:
            if isinstance(source.get(namespace), dict):
                node[namespace] = source[namespace]
            else:
                node.pop(namespace, None)

    def _split_flash_only(self):
        """Returns (settings without the protected namespaces, protected only)"""
        node = self.settings.get("settings")
        if not isinstance(node, dict):
            node = {}
        portable = dict(self.settings)
        portable["settings"] = {
            k: v for k, v in node.items() if k not in FLASH_ONLY_NAMESPACES
        }
        protected = {
            "settings": {k: v for k, v in node.items() if k in FLASH_ONLY_NAMESPACES}
        }
        return portable, protected

    @staticmethod
    def _write_if_changed(settings_filename, new_contents):
        """Writes new_contents unless the file already holds it"""
        old_contents = "{}"
        try:
            with open(settings_filename, "r") as f:
                old_contents = f.read()
        except:
            pass
        if new_contents == old_contents:
            return False
        try:
            with open(settings_filename, "w") as f:
                f.write(new_contents)
            return True
        except:
            return False

    @classmethod
    def get_vfs_location(cls, location):
        """Returns the formatted vfs location for SD/flash"""
        return "/" + location + "/"

    def _load_settings(self):
        """Loads settings based on the current file_location (SD/flash).

        Rejects files larger than MAX_SETTINGS_FILE_SIZE and any payload whose
        top-level value is not a JSON object. Per-setting type/range/category
        validation is enforced lazily by the Setting descriptors on read.
        """
        try:
            with open(self.file_location + SETTINGS_FILENAME, "r") as f:
                # Read one extra byte to detect oversized files
                contents = f.read(MAX_SETTINGS_FILE_SIZE + 1)
            if len(contents) > MAX_SETTINGS_FILE_SIZE:
                return
            loaded = json.loads(contents)
            if not isinstance(loaded, dict):
                return
            self.settings = loaded
        except:
            pass

    def get(self, namespace, setting_name, default_value):
        """Returns setting value under the given namespace, or default_value if not set."""
        s = self.settings
        for level in namespace.split("."):
            s = s.get(level)
            if not isinstance(s, dict):
                return default_value
        return s.get(setting_name, default_value)

    def set(self, namespace, setting_name, setting_value):
        """Stores a setting value under the given namespace if new/changed. Does not auto-save."""
        # A non-dict intermediate level is replaced with a fresh dict,
        # repairing malformed structure.
        s = self.settings
        for level in namespace.split("."):
            if not isinstance(s.get(level), dict):
                s[level] = {}
            s = s[level]
        old_value = s.get(setting_name, None)
        if old_value != setting_value:
            s[setting_name] = setting_value
            self.dirty = True

    def delete(self, namespace, setting_name):
        """Deletes dict storage in self.settings for namespace.setting_name,
        also deletes storage for setting_name's parent namespace nodes, if empty.
        """
        s = self.settings
        levels = []
        for level in namespace.split("."):
            if not isinstance(s.get(level), dict):
                s[level] = {}
            levels.append([s, level])
            s = s[level]
        if setting_name in s:
            del s[setting_name]
            self.dirty = True
        for s, level in reversed(levels):
            if not s[level]:
                del s[level]
                self.dirty = True

    def update_file_location(self, location):
        """Delete any unused persistent settings when set location"""
        self.file_location = Store.get_vfs_location(location)
        try:
            if FLASH_PATH in self.file_location:
                os.remove(Store.get_vfs_location(SD_PATH) + SETTINGS_FILENAME)
            else:
                os.remove(Store.get_vfs_location(FLASH_PATH) + SETTINGS_FILENAME)
        except:
            pass

    def save_settings(self):
        """Helper to persist SETTINGS_FILENAME where user selected"""
        persisted = False

        if self.dirty:
            settings_filename = self.file_location + SETTINGS_FILENAME
            if SD_PATH in self.file_location:
                # The card gets everything except the protected namespaces,
                # which stay in internal flash
                portable, protected = self._split_flash_only()
                persisted = self._write_if_changed(
                    settings_filename, json.dumps(portable)
                )
                if self._write_if_changed(
                    Store.get_vfs_location(FLASH_PATH) + SETTINGS_FILENAME,
                    json.dumps(protected),
                ):
                    persisted = True
            else:
                persisted = self._write_if_changed(
                    settings_filename, json.dumps(self.settings)
                )
            self.dirty = False

        return persisted


# Initialize singleton
store = Store()
