import pickle
import os
from typing import Tuple

data_dir = os.path.join(os.getcwd(), "data")
pinyin_file = os.path.join(
    data_dir, "pinyin.pickle")

pinyin_map = {}


def split_initial_simple_tone(src: str) -> Tuple[str, str, str]:
    i = 0
    while i < len(src) and not "aeiouv".find(src[i]) >= 0:
        i += 1
    initial = src[0:i]
    if "1234".find(src[-1]) >= 0:
        simple = src[i:-1]
        tone = src[-1:]
    else:
        simple = src[i:]
        tone = ""

    if "jqxyw".find(initial) >= 0 and simple == "u":
        simple = "v"

    return (initial, simple, tone)


def reload_pinyin_from_vendor(vendor_file):
    import json5
    from tqdm import tqdm
    from pypinyin.contrib.tone_convert import to_tone3

    signature = "\\u0101:\"\\u5416\\u9515\\u9312\""
    text = ""
    with open(vendor_file, "r", encoding="utf-8") as fp:
        text = "".join(fp.readlines())

    i_sign = text.find(signature)

    if i_sign < 0:
        print("signature word not found!")
        exit(1)

    i_r_brace = text.find("}", i_sign)
    i_l_brace = text.rfind("{", 0, i_sign)

    #print(text[i_l_brace: i_r_brace + 1])

    _raw_map = json5.loads(text[i_l_brace: i_r_brace + 1])

    for k, v in tqdm(_raw_map.items()):
        seq_nk = split_initial_simple_tone(to_tone3(k.split(",")[0]))
        for c in v:
            if c not in pinyin_map:
                pinyin_map.setdefault(c, seq_nk)

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    with open(pinyin_file, "wb+") as fp:
        fp.write(pickle.dumps(pinyin_map))


def load_pinyin_file():
    global pinyin_map
    with open(pinyin_file, "rb") as fp:
        pinyin_map = pickle.loads(fp.read())
    return pinyin_map


def get_pinyin(hanji):
    return pinyin_map.get(hanji)


if __name__ == "__main__":
    reload_pinyin_from_vendor("./vendor.js")
    load_pinyin_file()
    print(get_pinyin("垯"))
