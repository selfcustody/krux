# The MIT License (MIT)

# Copyright (c) 2021 Tom J. Sun

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
import sys
import json
from os import listdir, walk
from os.path import isfile, join
import re
import shutil

SRC_DIR = '../src'
TRANSLATION_FILES_DIR = 'translations'

def find_translation_slugs():
    """Searches the src directory for all 'slugs' that should be translated
       by looking for matches of the pattern ( 'string' )
    """
    slugs = {}
    for (dirpath, _, filenames) in walk(SRC_DIR):
        for filename in filenames:
            if not filename.endswith('.py'):
                continue
            with open(join(dirpath, filename), 'r') as src_file:
                contents = src_file.read()
                for match in re.findall(r'\( \'(.+?)\' \)', contents):
                    slugs[match] = True
    return slugs

def load_translations(translation_file):
    """Loads translations from the given file and returns them as a map"""
    translations = json.load(translation_file)
    for slug, translation in list(translations.items()):
        del translations[slug]
        translations[slug.replace('\n', '\\n')] = translation.replace('\n', '\\n')
    return translations

def main():
    """Main handler"""
    slugs = find_translation_slugs()

    if sys.argv[1] == 'validate':
        passed = True
        translation_filenames = [
            f for f in listdir(TRANSLATION_FILES_DIR)
            if isfile(join(TRANSLATION_FILES_DIR, f))
        ]
        for translation_filename in translation_filenames:
            print('Validating %s...' % translation_filename)
            valid = True
            with open(join(TRANSLATION_FILES_DIR, translation_filename), 'r') as translation_file:
                translations = load_translations(translation_file)
                for slug in slugs:
                    if slug not in translations or translations[slug] == '':
                        print('Missing translation for "%s"' % slug)
                        valid = False
                for translation_slug in translations:
                    if translation_slug not in slugs:
                        print('Unnecessary translation for "%s"' % translation_slug)
                        valid = False
            if valid:
                print('OK')
            passed = passed and valid
        if not passed:
            sys.exit(1)
    elif sys.argv[1] == 'new':
        locale = sys.argv[2]
        translations = {}
        for slug in slugs:
            translations[slug.replace('\\n', '\n')] = ''
        with open(join(TRANSLATION_FILES_DIR, '%s.json' % locale), 'w') as translation_file:
            translation_file.write(json.dumps(translations, sort_keys=True, indent=4))
    elif sys.argv[1] == 'translate':
        locale = sys.argv[2]
        output_dir = sys.argv[3]
        with open(join(TRANSLATION_FILES_DIR, '%s.json' % locale), 'r') as translation_file:
            translations = load_translations(translation_file)
            for (dirpath, _, filenames) in walk(output_dir):
                for filename in filenames:
                    if not filename.endswith('.py'):
                        continue

                    with open(join(dirpath, filename), 'r') as src_file:
                        contents = src_file.read()
                        for slug, translation in translations.items():
                            contents = contents.replace(
                                '( \'%s\' )' % slug,
                                '"""%s"""' % translation
                            )
                        with open(join(dirpath, filename + '.tmp'), 'w') as tmp_src_file:
                            tmp_src_file.write(contents)
                    shutil.move(join(dirpath, filename + '.tmp'), join(dirpath, filename))

if __name__ == '__main__':
    main()
