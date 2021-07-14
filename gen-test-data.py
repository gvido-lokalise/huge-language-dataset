from bs4 import BeautifulSoup as bs
from collections import defaultdict
from translate import Translator
from progress.bar import Bar

import traceback
import json
import time
import yaml

import httpx
import asyncio

html = 'index.html'
tag_list = ['a', 'div', 'p', 'i', 'b', 'span', 'li'] + [f'h{x}' for x in range(1,7)]


def create_yml(d, locale='en'):
    filename = locale + '.yml'
    data = {locale: d}

    with open(filename, 'w') as f:
        s = yaml.dump(data, f)

    print(f"YAML created. {s}")


def get_codes(file='lang_codes.txt'):
    with open(file, 'r') as f:
        return f.read().strip().split('\n')


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


def translate_keys(d, lang, engine='translate'):
    if engine == 'pypitranslate':
        return pypi_translate(d, lang)
    elif engine == 'libretranslate':
        return libre_translate(d, lang)
    else:
        print("Unknown Translate engine")


def fetch_translations(d):
    pass


def libre_translate(d, lang):

    new_dict = {}
    values = []

    url = 'http://0.0.0.0:5000/translate'

    for key, value in d.items():
        if len(value) > 499:
            value = value[:499]

        translation = value
        new_dict[key] = translation

    for key, value in d.items():
        values.append(value)

    data_list = [build_libre_query(lang, x) for x in values]

    r = asyncio.run(req(url, data_list))

    for i, key in enumerate(d.keys()):
        try:
            new_dict[key] = r[i]['translatedText']
        except:
            new_dict[key] = ''

    return new_dict

def build_libre_query(lang, value):
    return {'q': value,
            'source': 'en',
            'target': lang, }


def get_libretranslate_codes():
    file = 'libretranslate/supported_lang_codes.txt'
    return get_codes(file=file)


def choose_engine(code, libretranslate_codes):
    if code in libretranslate_codes:
        return 'libretranslate'
    return 'pypitranslate'


def pypi_translate(d, lang):
    bar = Bar(f'Translating: {lang} keys with PyPi translate', max=len(d))

    quota_errors = ['MYMEMORY WARNING', 'QUOTA', 'IS AN INVALID TARGET LANGUAGE']
    length_errors = ['500 CHARS', 'QUERY_LENGTH']
    new_dict = {}
    translator = Translator(to_lang=lang)
    quota_exceeded = False

    for key, value in d.items():
        if len(value) > 499:
            value = value[:499]

        if not quota_exceeded:
            translation = translator.translate(value)
        else:
            translation = ''

        for e in quota_errors:
            if e in translation:
                quota_exceeded = True
                print('[X] Quota exceeded [X]')
                translation = ''

        new_dict[key] = translation
        bar.next()

    bar.finish()
    return new_dict


async def req(url, data_list):
    async with httpx.AsyncClient(timeout=None) as client:
        tasks = (client.post(url, data=data) for data in data_list[:])
        reqs = await asyncio.gather(*tasks)

    return [json.json() for json in reqs]

def main():

    page = load_html()
    soup = bs(page, 'html.parser').find("body")

    tags = get_tags(soup)
    key_values = generate_keys(tags)

    e = json.dumps(key_values, indent=2)
    print(e)

    create_yml(key_values)
    lang_codes = get_codes()
    libretranslate_codes = get_libretranslate_codes()
    print(f"{libretranslate_codes=}")

    # lang_codes = ['es']
    bar = Bar(f'Starting translation for all {len(lang_codes)} lang_codes', max=len(lang_codes))

    for lang in lang_codes:
        engine = choose_engine(lang, libretranslate_codes)
        bar.next()
        print(lang)
        translated_data = translate_keys(key_values, lang, engine=engine)
        create_yml(translated_data, locale=lang)

    bar.finish()


if __name__ == '__main__':
    main()
