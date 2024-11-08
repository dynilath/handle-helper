from fileinput import filename
import os
import math
import json5
import pickle
import hashlib
from typing import Tuple

import pinyin
import pattern

data_dir = os.path.join(os.getcwd(), "data")

if not os.path.exists(data_dir) and os.path.isdir(data_dir):
    os.makedirs(data_dir)

words_with_entropy_file = os.path.join(
    data_dir, "words_with_entropy.pickle")

words_file = os.path.join(
    data_dir, "words.pickle")


def get_words_from_source(file, signature):
    text = ""
    with open(file, "r", encoding="utf-8") as fp:
        text = "".join(fp.readlines())
    i_sign = text.find(signature)
    if i_sign < 0:
        raise "signature word not found! file:" + file + " signature:" + signature

    level = 1
    i_l_bracket = i_sign - 1
    while i_l_bracket > 0:

        if text[i_l_bracket] == ']':
            level += 1
        elif text[i_l_bracket] == '[':
            level -= 1

        if level == 0:
            break
        else:
            i_l_bracket -= 1

    level = 1
    i_r_bracket = i_sign + len(signature)
    while i_r_bracket < len(text):

        if text[i_r_bracket] == '[':
            level += 1
        elif text[i_r_bracket] == ']':
            level -= 1

        if level == 0:
            break
        else:
            i_r_bracket += 1

    word_list_str = text[i_l_bracket:i_r_bracket+1]
    return json5.loads(word_list_str)


def set_word_list(word_list):
    with open(words_file, "wb+") as fp:
        fp.write(pickle.dumps(word_list))


def get_word_list():
    with open(words_file, "rb") as fp:
        return pickle.loads(fp.read())


def guess_vs_possibles(guess, word_list):
    ret = {}
    for w in word_list:
        pat = pattern.match_han_word_pattern(guess, w)
        if pat not in ret:
            ret.setdefault(pat, 1)
        else:
            ret[pat] = ret[pat] + 1
    return ret


def average_info_entropy(guess, word_list, origin_word):
    guess_result_pat = guess_vs_possibles(guess, word_list)
    aver_ent = 0
    cnt = len(guess_result_pat)
    for k, v in guess_result_pat.items():
        aver_ent += -math.log2(v/len(word_list))
    return [origin_word, aver_ent/cnt]


def set_words_with_entropy_file(file, possible_with_entropy):
    with open(file, "wb+") as fp:
        fp.write(pickle.dumps(possible_with_entropy))


def generate_word_list_with_entropy(word_list, alter_pinyin_list=None):
    ret = []
    from concurrent.futures import ProcessPoolExecutor, as_completed
    from tqdm import tqdm

    composite_word_list = word_list
    if not alter_pinyin_list is None:
        composite_word_list = [[word_list[i][0], alter_pinyin_list[i]]
                               for i in range(len(word_list))]

    with tqdm(total=len(word_list)) as pbar:
        with ProcessPoolExecutor(max_workers=4) as exec:
            future_list = [exec.submit(
                average_info_entropy, composite_word_list[i], composite_word_list, word_list[i]) for i in range(len(word_list))]

            for f in as_completed(future_list):
                ret.append(f.result())
                pbar.update(1)
    ret.sort(key=lambda x: x[1], reverse=True)
    return ret


def read_word_list_from_index(index_file):
    raw_wordlist = get_words_from_source(
        index_file, "[\"\\u963F\\u9F3B\\u5730\\u72F1\"]")
    ret = []
    for w in raw_wordlist:
        if len(w) == 1:
            ret.append([w[0], [pinyin.get_pinyin(c) for c in w[0]]])
        elif len(w) == 2:
            ret.append(
                [w[0], [pinyin.split_initial_simple_tone(pi) for pi in w[1].split(" ")]])
    return ret


def create_serialized_pinyin_list(word_list):
    initials = set()
    simples = set()
    tones = set()

    for w in word_list:
        for p in w[1]:
            initials.add(p[0])
            simples.add(p[1])
            tones.add(p[2])

    def cmap(pset: set) -> dict:
        plist = [w for w in pset]
        plist.sort()
        ret = {}
        for i in range(len(pset)):
            ret.setdefault(plist[i], i)
        return ret

    initial_map = cmap(initials)
    simple_map = cmap(simples)
    tone_map = cmap(tones)

    serial_pinyin_list = []
    for w in word_list:
        pinyin = w[1]
        serial_pinyin = []
        for r in pinyin:
            seq = [initial_map[r[0]],
                   simple_map[r[1]],
                   tone_map[r[2]]]
            serial_pinyin.append(seq)
        serial_pinyin_list.append(serial_pinyin)
    return serial_pinyin_list


def reload_words_entropy_from_index(index_file):
    wlist = read_word_list_from_index(index_file)
    serial_pinyin = create_serialized_pinyin_list(wlist)
    wordlist_with_ent = generate_word_list_with_entropy(
        wlist, serial_pinyin)

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    with open(words_with_entropy_file, "wb+") as fp:
        fp.write(pickle.dumps(wordlist_with_ent))
    return wordlist_with_ent


def reload_words_entropy_from_word_list(word_list):
    serial_pinyin = create_serialized_pinyin_list(word_list)
    wordlist_with_ent = generate_word_list_with_entropy(
        word_list, serial_pinyin)

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    with open(words_with_entropy_file, "wb+") as fp:
        fp.write(pickle.dumps(wordlist_with_ent))
    return wordlist_with_ent


def read_words_with_entropy(file: str):
    with open(file, "rb") as fp:
        return pickle.loads(fp.read())


def get_words_with_entropy():
    return read_words_with_entropy(
        words_with_entropy_file)


def default_pinyin(word):
    return [pinyin.get_pinyin(w) for w in word]


if __name__ == "__main__":

    from pypac import PACSession
    import re
    import glob

    url = "https://handle.antfu.me/"

    session = PACSession()
    r = session.get(url)

    re_idioms = re.compile(
        r'="(\/assets\/(idioms.[0-9a-f]+\.js))"')

    re_vendor = re.compile(
        r'="(\/assets\/(vendor.[0-9a-f]+\.js))"')

    re_polyphone = re.compile(
        r'="(\/assets\/(polyphones.[0-9a-f]+\.js))"')

    def update_source(url, filepath, expect_name) -> Tuple[bool, str]:
        expected_file = glob.glob(os.path.join(data_dir, expect_name))

        founded = False

        if len(expected_file) > 0:
            for f in expected_file:
                if os.path.basename(f) == os.path.basename(filepath):
                    founded = True
                else:
                    os.remove(f)

        if founded:
            return (not founded), filepath

        r = session.get(url)
        with open(filepath, "w+", encoding="utf-8") as fp:
            fp.write(r.text)
        return (not founded), filepath

    def update_with_regex_filter(regex, url, text, expect):
        _matches = regex.search(text)
        _url = url + _matches[1]
        _filepath = os.path.join(data_dir, _matches[2])
        return update_source(_url, _filepath, expect)

    idioms_updated, idioms_file = update_with_regex_filter(
        re_idioms, url, r.text, "idioms.*.js")

    polyphones_updated, polyphones_file = update_with_regex_filter(
        re_polyphone, url, r.text, "polyphones.*.js")

    vendor_updated, vendor_file = update_with_regex_filter(
        re_vendor, url, r.text, "vendor.*.js")

    if vendor_updated or not os.path.exists(pinyin.pinyin_file):
        print("更新拼音数据...")
        pinyin.reload_pinyin_from_vendor(vendor_file)

    pinyin.load_pinyin_file()

    word_list_updated = False

    if idioms_updated or polyphones_updated or not os.path.exists(words_file):
        print("更新词库数据...")
        with open(idioms_file, "r", encoding="utf-8") as fp:
            text = "".join(fp.readlines())
            l_backquote = text.find("`")
            r_backquote = text.find("`", l_backquote+1)
            idiom_list = json5.loads(
                "[\"" + "\",\"".join(text[l_backquote+1:r_backquote].split()) + "\"]")

        with open(polyphones_file, "r", encoding="utf-8") as fp:
            text = "".join(fp.readlines())
            l_backquote = text.find("`")
            l_brace = text.find("{")
            r_brace = text.find("}", l_brace)
            polyphones_map = json5.loads(text[l_brace: r_brace+1])

        word_list = []
        for w in polyphones_map:
            k = polyphones_map[w]
            word_list.append([w, [pinyin.split_initial_simple_tone(
                cp) for cp in k.split()]])

        for w in idiom_list:
            word_list.append([w, [pinyin.get_pinyin(c) for c in w]])

        set_word_list(word_list)

        word_list_updated = True

    if word_list_updated or not os.path.exists(words_with_entropy_file):
        word_list = get_word_list()

        print("更新词语筛选缓存...")
        reload_words_entropy_from_word_list(word_list)
