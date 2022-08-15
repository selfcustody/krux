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
import binascii
from .settings import CategorySetting, SettingsNamespace, Settings
from .translations import translation_table


class I18nSettings(SettingsNamespace):
    """I18n-specific settings"""

    namespace = "settings.i18n"
    locale = CategorySetting("locale", "en-US", list(translation_table.keys()))

    def label(self, attr):
        """Returns a label for UI when given a setting name or namespace"""
        return {
            "locale": t("Locale"),
        }[attr]


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
