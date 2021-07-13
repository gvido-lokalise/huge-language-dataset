from bs4 import BeautifulSoup as bs
from collections import defaultdict
from translate import Translator
from progress.bar import Bar

import traceback
import json
import time
import yaml

html = 'index.html'
tag_list = ['a', 'div', 'p', 'i', 'b', 'span', 'li'] + [f'h{x}' for x in range(1,7)]


def load_html(file=html):
    with open(file, 'r') as f:
        return f.read().strip()


def find(el, *attrs):
    try:
        return el.find(*attrs).text
    except TypeError:
        return None


def find_all(el, *attrs):
    try:
        return el.find_all(*attrs)
    except TypeError:
        return None


def get_tags(s):
    dict_ = defaultdict(list)

    for tag in tag_list:
        try:
            el = find_all(s, tag)

            for e in el:
                if e.text.strip():
                    text = e.text.strip()
                    dict_[tag].append(text)
                    # print(text)

        except TypeError:
            print('NoneType')
        except Exception:
            traceback.print_exc()

    return dict_


def generate_keys(d):
    new_dict = {}

    for key, value in d.items():
        for v in value:
            new_dict[key + str(time.time())] = v

    return new_dict


def translate_keys(d, lang):
    bar = Bar(f'Translating: {lang} keys', max=len(d))

    new_dict = {}
    translator = Translator(to_lang=lang)

    for key, value in d.items():
        translation = translator.translate(value)

        """
        'QUERY LENGTH LIMIT EXCEDEED. MAX ALLOWED QUERY : 500 CHARS QUERY LENGTH LIMIT EXCEDEED. MAX ALLOWED QUERY : 500 CHARS QUERY LENGTH LIMIT EXCEDEED. MAX ALLOWED QUERY : 500 CHARS QUERY LENGTH LIMIT EXCEDEED. MAX ALLOWED QUERY : 500 CHARS'
        """

        if 'MYMEMORY WARNING' in translation or 'IS AN INVALID TARGET LANGUAGE' in translation:
            translation = 'Untranslated.'

        new_dict[key] = translation
        bar.next()

    bar.finish()

    return new_dict


def create_yml(d, locale='en'):
    filename = locale + '.yml'
    data = {locale: d}

    with open(filename, 'w') as f:
        s = yaml.dump(data, f)

    print(f"YAML created. {s}")


def get_codes(file='lang_codes.txt'):
    with open(file, 'r') as f:
        return f.read().strip().split('\n')


def main():

    page = load_html()
    soup = bs(page, 'html.parser').find("body")

    tags = get_tags(soup)
    key_values = generate_keys(tags)

    e = json.dumps(key_values, indent=2)
    print(e)

    create_yml(key_values)
    lang_codes = get_codes()

    bar = Bar(f'Starting translation for all {len(lang_codes)} lang_codes', max=len(lang_codes))

    for lang in lang_codes:
        bar.next()
        print(lang)
        translated_data = translate_keys(key_values, lang)
        create_yml(translated_data, locale=lang)

    bar.finish()


if __name__ == '__main__':
    main()
