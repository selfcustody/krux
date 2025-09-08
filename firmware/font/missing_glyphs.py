"""
By looking into:
* ../MaixPy/projects/ (which should have font_device.h files,
* ../../i18n/translations/*.json which contain all locale translations,

... compiles list of all needed characters across translations,

then prints lists of:
* all necessary characters which need a glyph entry for each project,
* missing glyphs from projects' font_device.h files

... which need attention.
"""

# The MIT License (MIT)

# Copyright (c) 2021-2025 Krux contributors

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


import os
import json
from hextokff import CHAR_LIST_EXCEPT_ASIAN

exec_folder = os.path.join("firmware", "font")
current_dir = os.getcwd()

if not current_dir.endswith(exec_folder):
    os.chdir(exec_folder)

# a list of projects
PROJECTS_DIR = "../MaixPy/projects"
projects = os.listdir(PROJECTS_DIR)

# a list of locale-translations
TRANSLATIONS_DIR = "../../i18n/translations"
translations = os.listdir(TRANSLATIONS_DIR)

# base list of chars uses data from firmware/font/hextokff.py
chars = list(CHAR_LIST_EXCEPT_ASIAN)

# add additional chars found in translations
for translation in translations:
    l10ndict = json.load(open("{}/{}".format(TRANSLATIONS_DIR, translation)))
    for translation in l10ndict.values():
        for char in [x for x in translation if x >= " "]:
            if char not in chars:
                chars.append(char)
chars.sort()

# report translations file checked, range of chars, and list of all chars that need glyphs
print(
    "\nTranslations files %s have %d unique symbols in translations"
    % (translations, len(chars))
)
print(
    "\nLowest unicode point: %s (decimal: %d); highest unicode point: %s (decimal: %d)"
    % (hex(ord(min(chars))), ord(min(chars)), hex(ord(max(chars))), ord(max(chars)))
)
print("".join(chars))


# check each projects font file and print missing glyphs that need attention
FMT_HFILE = "{}/{}/compile/overrides/components/micropython/port/src/omv/img/include/font_device.h"
for project in projects:
    font_file = FMT_HFILE.format(PROJECTS_DIR, project)
    print("\nChecking font file %s for existing/missing glyphs..." % font_file)
    try:
        contents = open(font_file, "r").readlines()
        existing, missing = [], []
        for char in chars:
            ord4hex = "{:04X}".format(ord(char))
            entry_header = "0x{:2s},0x{:2s},\n".format(ord4hex[:2], ord4hex[2:])
            if entry_header in contents:
                existing.append(char)
            else:
                missing.append(char)
        if len(missing) > 0:
            print("  missing: {}".format("".join(missing)))
            print(
                "  missing %d unicode points between: %s (or %d) and %s (or %d)"
                % (
                    len(missing),
                    hex(ord(min(missing))),
                    ord(min(missing)),
                    hex(ord(max(missing))),
                    ord(max(missing)),
                )
            )
    except Exception as e:
        print("Exception ocurred while opening %s:" % font_file, e)
