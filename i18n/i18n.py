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

import binascii
import sys
import json
from os import listdir, walk, mkdir, remove, rmdir, getcwd, chdir
from os.path import isfile, isdir, exists, join, basename
import re

EXEC_FOLDER = "i18n"
current_dir = getcwd()

# check if is executing in exec_folder, if not, try to change to EXEC_FOLDER
if not current_dir.endswith(EXEC_FOLDER):
    chdir(EXEC_FOLDER)

SRC_DIR = "../src"
TRANSLATION_FILES_DIR = "translations"

ELLIPSIS_UNICODE = "\u2026"
ELLIPSIS_ASCII = "..."

KRUX_LICENSE = """# The MIT License (MIT)

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
"""


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
    for translation_filename in sorted(translation_filenames):
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


def post_process_translation(slug, translation, verbose=False):
    """
    A place for post-translation fixes of poor translations per slug/translation
    returns original -- or corrected translation
    """
    err = None

    translation = translation.replace(ELLIPSIS_ASCII, ELLIPSIS_UNICODE)
    translation = translation.replace("（", "(")
    translation = translation.replace("）", ")")
    translation = translation.replace("。", ".")
    translation = translation.replace("，", ",")
    translation = translation.replace("：", ":")
    translation = translation.replace("？", "?")
    translation = translation.replace("！", "!")
    translation = translation.replace(" ", " ")  # non-breaking space to thin-space

    # fix poorly translated newlines
    if " \\ n" in translation:
        err = "Poor newline translation: {}, {}".format(repr(slug), repr(translation))
        translation = translation.replace(" \\ n", "\\n")

    # fix poorly translated unicode ellipsis
    ellipsis = ELLIPSIS_UNICODE
    if slug[-1] == ellipsis:
        err = "Poor ellipsis translation: {}, {}".format(repr(slug), repr(translation))
        if translation[-2:] == ellipsis * 2:
            translation = translation[:-1]
        elif translation[-4:] == "." * 4:
            translation = translation[:-4] + ellipsis
        elif translation[-3:] == "." * 3:
            translation = translation[:-3] + ellipsis
        elif translation[-1:] in (".", " "):
            translation = translation[:-1] + ellipsis
        elif translation[-1] != ellipsis:
            translation = translation + ellipsis
        else:
            err = None  # translation was fine

    if verbose and err:
        print(err, file=sys.stderr)

    return translation


def print_missing(save_to_file=False, merge_after=False):
    """
    Uses translate 3.6.1 to automatically print missing translations
    and optionally save them to files
    """
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

    filled_dir = join(TRANSLATION_FILES_DIR, "filled")
    if save_to_file and not exists(filled_dir):
        mkdir(filled_dir)

    for translation_filename in sorted(translation_filenames):
        target = translation_filename[:5]
        if force_target:
            if not force_target in translation_filename:
                continue
        translator = Translator(to_lang=target)
        print("Translating %s...\n" % translation_filename)
        complete = True
        new_translations = {}
        with open(
            join(TRANSLATION_FILES_DIR, translation_filename), "r", encoding="utf8"
        ) as translation_file:
            translations = load_translations(translation_file)
            for slug in slugs:
                if slug not in translations or translations[slug] == "":
                    try:
                        slug = slug.replace(ELLIPSIS_UNICODE, ELLIPSIS_ASCII)
                        translated = translator.translate(slug)
                        slug = slug.replace(ELLIPSIS_ASCII, ELLIPSIS_UNICODE)
                        translated = post_process_translation(
                            slug, translated, verbose=(save_to_file or merge_after)
                        )
                        print('"%s":' % slug, '"%s",' % translated)
                        new_translations[slug] = translated

                    except Exception as e:
                        print("Error:", e)
                        print("Failed to translate:", slug)
                        break
                    complete = False
        if complete:
            print("Nothing to add")
        else:
            print("\n -- Please review and copy items above -- ")
            if save_to_file:
                with open(
                    join(filled_dir, translation_filename),
                    "w",
                    encoding="utf8",
                    newline="\n",
                ) as filled_file:
                    json.dump(
                        new_translations, filled_file, ensure_ascii=False, indent=4
                    )
                print(f"Saved translations to {join(filled_dir, translation_filename)}")
                if merge_after:
                    translations.update(new_translations)
                    with open(
                        join(TRANSLATION_FILES_DIR, translation_filename),
                        "w",
                        encoding="utf8",
                        newline="\n",
                    ) as file:
                        json.dump(
                            translations,
                            file,
                            ensure_ascii=False,
                            indent=4,
                            sort_keys=True,
                        )
                    print(
                        f"Saved translations to {join(TRANSLATION_FILES_DIR, translation_filename)}"
                    )

                    remove(join(filled_dir, translation_filename))
                    print(
                        f"Removed translation {join(filled_dir, translation_filename)}"
                    )
        print("\n\n")

    if merge_after:
        rmdir(filled_dir)


def remove_unnecessary():
    """Remove unnecessary translations from files"""
    code_slugs = find_translation_slugs()
    translation_filenames = [
        f
        for f in listdir(TRANSLATION_FILES_DIR)
        if isfile(join(TRANSLATION_FILES_DIR, f))
    ]
    for translation_filename in sorted(translation_filenames):
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
                join(TRANSLATION_FILES_DIR, translation_filename),
                "w",
                encoding="utf8",
                newline="\n",
            ) as translation_file:
                json.dump(full_translations, translation_file, ensure_ascii=False)
                # run black after this


def bake_translations():
    """
    Bakes individual translation tables into separate files inside the krux namespace
    within a 'translations' subfolder.
    """
    translations_dir = join(SRC_DIR, "krux", "translations")

    # Create the translations subfolder if it doesn't exist
    if not isdir(translations_dir):
        mkdir(translations_dir)

    translation_filenames = [
        f
        for f in listdir(TRANSLATION_FILES_DIR)
        if isfile(join(TRANSLATION_FILES_DIR, f))
    ]
    translation_filenames.sort()
    code_slugs = find_translation_slugs()
    code_slugs = sorted(code_slugs)
    for translation_filename in sorted(translation_filenames):
        with open(
            join(TRANSLATION_FILES_DIR, translation_filename), "r", encoding="utf8"
        ) as translation_file:
            translations = json.load(translation_file)
            translations_array = []
            for slug in code_slugs:
                if slug not in translations:
                    translations_array.append(slug)
                else:
                    translations_array.append(translations[slug])
            language_code = basename(translation_filename).split(".")[0][:2]

            # Write the individual translation array to a separate Python file
            # in the 'translations' subfolder
            with open(
                join(translations_dir, f"{language_code}.py"),
                "w",
                encoding="utf8",
                newline="\n",
            ) as language_file:
                language_file.write(KRUX_LICENSE)
                language_file.write("# pylint: disable=C0301\n")
                language_file.write("translation_array = ")
                language_file.write(repr(translations_array))
                language_file.write("\n")
                print("Baked: " + translations_dir + f"/{language_code}.py")
    # Create an reference array for index lookup
    reference_array = []
    for slug in code_slugs:
        reference_array.append(binascii.crc32(slug.encode("utf-8")))
    # Create a file with a list of all available languages and index lookup array
    with open(join(translations_dir, "__init__.py"), "w", encoding="utf8") as init_file:
        init_file.write(KRUX_LICENSE)
        init_file.write("available_languages = [")
        init_file.write(
            ", ".join([f'"{basename(f).split(".")[0]}"' for f in translation_filenames])
        )
        init_file.write("]")
        init_file.write("\n")
        init_file.write("ref_array = ")
        init_file.write(repr(reference_array))
        init_file.write("\n")


def create_translation_file(locale):
    """Creates a new translation file for the given locale with stubbed-out translations"""
    translations = {}
    slugs = find_translation_slugs()
    for slug in slugs:
        translations[slug.replace("\\n", "\n")] = ""
    with open(
        join(TRANSLATION_FILES_DIR, "%s.json" % locale),
        "w",
        encoding="utf8",
        newline="\n",
    ) as translation_file:
        translation_file.write(
            json.dumps(translations, sort_keys=True, indent=4, ensure_ascii=False)
        )


def prettify_translation_files():
    """Sorts and pretty-prints all translation files (one per line)"""
    translation_filenames = [
        f
        for f in listdir(TRANSLATION_FILES_DIR)
        if isfile(join(TRANSLATION_FILES_DIR, f))
    ]
    translation_filenames.sort()
    for translation_filename in translation_filenames:
        translations = {}
        with open(
            join(TRANSLATION_FILES_DIR, translation_filename), "r", encoding="utf8"
        ) as translation_file:
            translations = json.load(translation_file)
        with open(
            join(TRANSLATION_FILES_DIR, translation_filename),
            "w",
            encoding="utf8",
            newline="\n",
        ) as translation_file:
            translation_file.write(
                json.dumps(translations, sort_keys=True, indent=4, ensure_ascii=False)
            )
            print("Prettified " + translation_filename)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError(
            "ERROR: Provide one action as argument"
            + " (validate, new, fill, fill_merge, clean, prettify, bake)"
        )

    if not exists(SRC_DIR):
        SRC_DIR = "src"
        if not exists(SRC_DIR):
            raise ValueError("ERROR: SRC_DIR 'src' not found!")

    if not exists(TRANSLATION_FILES_DIR):
        TRANSLATION_FILES_DIR = "i18n/translations"
        if not exists(TRANSLATION_FILES_DIR):
            raise ValueError("ERROR: TRANSLATION_FILES_DIR 'translations' not found!")

    if sys.argv[1] in ("new", "fill"):
        if sys.argv[1] == "new":
            if len(sys.argv) < 3:
                raise ValueError("ERROR: Provide the locale to fill")
            create_translation_file(sys.argv[2])
        else:
            print_missing()
    else:
        for arg in sys.argv[1:]:
            if arg == "validate":
                validate_translation_files()
            elif arg == "fill":
                print_missing()
            elif [
                True
                for text in (
                    "fill_to_files",
                    "fill-to-files",
                    "fill_files",
                    "fill-files",
                )
                if arg in text
            ]:
                print_missing(save_to_file=True)
            elif [
                True
                for text in (
                    "fill_and_merge",
                    "fill-and-merge",
                    "fill_merge",
                    "fill-merge",
                )
                if arg in text
            ]:
                print_missing(save_to_file=True, merge_after=True)
            elif arg == "clean":
                remove_unnecessary()
            elif arg == "prettify":
                prettify_translation_files()
            elif arg == "bake":
                bake_translations()
            else:
                print("\n\nWARNING: Unreconized argument: " + arg)
