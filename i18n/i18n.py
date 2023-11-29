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
import binascii
import sys
import json
from os import listdir, walk
from os.path import isfile, join, basename
import re

SRC_DIR = "../src"
TRANSLATION_FILES_DIR = "translations"


def find_translation_slugs():
    """Searches the src directory for all 'slugs' that should be translated
    by looking for matches of the pattern t("string")
    """
    slugs = {}
    for dirpath, _, filenames in walk(SRC_DIR):
        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            with open(join(dirpath, filename), "r", encoding="utf8") as src_file:
                contents = src_file.read()
                for match in re.findall(r"[^A-Za-z0-9]t\(\s*\"(.+?)\"\s*\)", contents):
                    slugs[match] = True
    return slugs


def load_translations(translation_file):
    """Loads translations from the given file and returns them as a map"""
    translations = json.load(translation_file)
    for slug, translation in list(translations.items()):
        del translations[slug]
        translations[slug.replace("\n", "\\n")] = translation.replace("\n", "\\n")
    return translations


def validate_translation_files():
    """Validates all translation files, checking for missing and unnecessary translations"""
    passed = True
    slugs = find_translation_slugs()
    translation_filenames = [
        f
        for f in listdir(TRANSLATION_FILES_DIR)
        if isfile(join(TRANSLATION_FILES_DIR, f))
    ]
    for translation_filename in translation_filenames:
        print("Validating %s..." % translation_filename)
        valid = True
        with open(
            join(TRANSLATION_FILES_DIR, translation_filename), "r", encoding="utf8"
        ) as translation_file:
            translations = load_translations(translation_file)
            for slug in slugs:
                if slug not in translations or translations[slug] == "":
                    print('Missing translation for "%s"' % slug)
                    valid = False
            for translation_slug in translations:
                if translation_slug not in slugs:
                    print('Unnecessary translation for "%s"' % translation_slug)
                    valid = False
        if valid:
            print("OK")
        passed = passed and valid
    if not passed:
        sys.exit(1)


def fill_missing():
    """Uses translate 3.6.1 to automaticalyy fill missing translations"""
    if len(sys.argv) > 2:
        force_target = sys.argv[2]
    else:
        force_target = None
    from translate import Translator

    slugs = find_translation_slugs()
    translation_filenames = [
        f
        for f in listdir(TRANSLATION_FILES_DIR)
        if isfile(join(TRANSLATION_FILES_DIR, f))
    ]
    for translation_filename in translation_filenames:
        target = translation_filename[:5]
        if force_target:
            if force_target != translation_filename:
                continue
        translator = Translator(to_lang=target)
        print("Translating %s...\n" % translation_filename)
        complete = True
        with open(
            join(TRANSLATION_FILES_DIR, translation_filename), "r", encoding="utf8"
        ) as translation_file:
            translations = load_translations(translation_file)
            for slug in slugs:
                if slug not in translations or translations[slug] == "":
                    try:
                        translated = '"%s",' % translator.translate(slug).replace(
                            " \ n", "\\n"
                        )
                        print('"%s":' % slug, translated)
                    except Exception as e:
                        print("Error:", e)
                        print("Failed to translate:", slug)
                        break
                    complete = False
        if complete:
            print("Nothing to add")
        else:
            print("Please review and copy items above")
        print("\n\n")


def remove_unnecessary():
    """Remove unnecessary translations from files"""
    code_slugs = find_translation_slugs()
    translation_filenames = [
        f
        for f in listdir(TRANSLATION_FILES_DIR)
        if isfile(join(TRANSLATION_FILES_DIR, f))
    ]
    for translation_filename in translation_filenames:
        print("Cleaning %s..." % translation_filename)
        clean = True
        with open(
            join(TRANSLATION_FILES_DIR, translation_filename), "r", encoding="utf8"
        ) as translation_file:
            full_translations = json.load(translation_file)
            translation_file.seek(0)
            translations = load_translations(translation_file)
            for translation_slug in translations:
                if translation_slug not in code_slugs:
                    print('Removing: "%s"' % translation_slug)
                    clean = False
                    del full_translations[translation_slug.replace("\\n", "\n")]
        if clean:
            print("Nothing removed")
        else:
            with open(
                join(TRANSLATION_FILES_DIR, translation_filename), "w", encoding="utf8"
            ) as translation_file:
                json.dump(full_translations, translation_file, ensure_ascii=False)
                # run black after this


def bake_translations():
    """Bakes all translations into a translations.py file inside the krux namespace"""
    translation_table = {}
    translation_filenames = [
        f
        for f in listdir(TRANSLATION_FILES_DIR)
        if isfile(join(TRANSLATION_FILES_DIR, f))
    ]
    for translation_filename in translation_filenames:
        with open(
            join(TRANSLATION_FILES_DIR, translation_filename), "r", encoding="utf8"
        ) as translation_file:
            translations = json.load(translation_file)
            lookup = {}
            for slug, translation in list(translations.items()):
                lookup[binascii.crc32(slug.encode("utf-8"))] = translation
            translation_table[basename(translation_filename).split(".")[0]] = lookup

    with open(
        join(SRC_DIR, "krux", "translations.py"), "w", encoding="utf8"
    ) as translations:
        translations.write(
            """# The MIT License (MIT)

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
# THE SOFTWARE.\n"""
        )
        translations.write("# pylint: disable=C0301\n")
        translations.write("translation_table = ")
        translations.write(repr(translation_table))
        translations.write("\n")


def create_translation_file(locale):
    """Creates a new translation file for the given locale with stubbed-out translations"""
    translations = {}
    slugs = find_translation_slugs()
    for slug in slugs:
        translations[slug.replace("\\n", "\n")] = ""
    with open(
        join(TRANSLATION_FILES_DIR, "%s.json" % locale), "w", encoding="utf8"
    ) as translation_file:
        translation_file.write(
            json.dumps(translations, sort_keys=True, indent=4, ensure_ascii=False)
        )


def prettify_translation_files():
    """Sorts and pretty-prints all translation files"""
    translation_filenames = [
        f
        for f in listdir(TRANSLATION_FILES_DIR)
        if isfile(join(TRANSLATION_FILES_DIR, f))
    ]
    for translation_filename in translation_filenames:
        translations = {}
        with open(
            join(TRANSLATION_FILES_DIR, translation_filename), "r", encoding="utf8"
        ) as translation_file:
            translations = json.load(translation_file)
        with open(
            join(TRANSLATION_FILES_DIR, translation_filename), "w", encoding="utf8"
        ) as translation_file:
            translation_file.write(
                json.dumps(translations, sort_keys=True, indent=4, ensure_ascii=False)
            )


def main():
    """Main handler"""

    if sys.argv[1] == "validate":
        validate_translation_files()
    elif sys.argv[1] == "new":
        create_translation_file(sys.argv[2])
    elif sys.argv[1] == "fill":
        fill_missing()
    elif sys.argv[1] == "clean":
        remove_unnecessary()
    elif sys.argv[1] == "prettify":
        prettify_translation_files()
    elif sys.argv[1] == "bake":
        bake_translations()


if __name__ == "__main__":
    main()
