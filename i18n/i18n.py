import sys
import json
from os import listdir, walk
from os.path import isfile, join
import re
import shutil

SRC_DIR = '../src'
TRANSLATION_FILES_DIR = 'translations'

def find_translation_slugs():
	slugs = {}
	for (dirpath, _, filenames) in walk(SRC_DIR):
		for filename in filenames:
			if not filename.endswith('.py'):
				continue
			with open(join(dirpath, filename), 'r') as f:
				contents = f.read()
				for match in re.findall(r'\( \'(.+?)\' \)', contents):
					slugs[match] = True
	return slugs

def load_translations(f):
	translations = json.load(f)
	for slug, translation in list(translations.items()):
		del translations[slug]
		translations[slug.replace('\n', '\\n')] = translation.replace('\n', '\\n')
	return translations

slugs = find_translation_slugs()

if sys.argv[1] == 'validate':
	translation_files = [f for f in listdir(TRANSLATION_FILES_DIR) if isfile(join(TRANSLATION_FILES_DIR, f))]
	for translation_file in translation_files:
		print('Validating %s...' % translation_file)
		ok = True
		with open(join(TRANSLATION_FILES_DIR, translation_file), 'r') as f:
			translations = load_translations(f)
			for slug in slugs:
				if slug not in translations or translations[slug] == '':
					print('Missing translation for "%s"' % slug)
					ok = False
			for translation_slug in translations:
				if translation_slug not in slugs:
					print('Unnecessary translation for "%s"' % translation)
					ok = False
		if ok:
			print('OK')
elif sys.argv[1] == 'new':
	locale = sys.argv[2]
	translations = {}
	for slug in slugs:
		translations[slug.replace('\\n', '\n')] = ''
	with open(join(TRANSLATION_FILES_DIR, '%s.json' % locale), 'w') as f:
		f.write(json.dumps(translations, sort_keys=True, indent=4))
elif sys.argv[1] == 'translate':
	locale = sys.argv[2]
	output_dir = sys.argv[3]
	with open(join(TRANSLATION_FILES_DIR, '%s.json' % locale), 'r') as tf:
		translations = load_translations(tf)
		for (dirpath, _, filenames) in walk(output_dir):
			for filename in filenames:
				if not filename.endswith('.py'):
					continue
				
				with open(join(dirpath, filename), 'r') as f:
					contents = f.read()
					for slug, translation in translations.items():
						contents = contents.replace('( \'%s\' )' % slug, '\'%s\'' % translation)
					with open(join(dirpath, filename + '.tmp'), 'w') as nf:
						nf.write(contents)
				shutil.move(join(dirpath, filename + '.tmp'), join(dirpath, filename))