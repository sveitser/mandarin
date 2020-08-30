#!/usr/bin/env python
from collections import defaultdict
from pathlib import Path
import os
import re

import pypinyin

import random

random.seed(0)

# media_dir = Path("/home/lulu/.local/share/Anki2/User 1/collection.media")
media_dir = Path("/home/lulu/zh/dicts/audio/google-text-to-speech/")
sound_prefix = Path("google-text-to-speech")

SINGLE = r"[cjqz][a-z]{1,5}[1-4]?_[^\.]*\..*"
SINGLE_ALL = r"[a-z]{1,6}[1-4]?_[2-9]\.mp3"
DOUBLE = r"[a-z]{1,6}[1-4][a-z]{1,6}[1-4]?_?[1-9]?\."
INITIAL = r"^(q|j|zh|ch|z|c)"
DOUBLE_HANZI = r"..\."

SELECTION = set(
    [
        "jin1tian1",
        "zhong1guo2",
        "bing1shui3" "zhi1dao4",
        "zhen1de",
        "ming2tian1",
        "ming2nian2",
        "pi2jiu3",
        "rong2yi4",
        "shen2me",
        "xi3huan1",
        "qi3chuang2",
        "ni3hao3",
        "chao3fan4",
        "wo3de",
        "mian4bao1",
        "wen4ti2",
        "zhe4li3",
        "zai4jian4",
        "xie4xie",
    ]
)


REGEX = DOUBLE_HANZI

COLS = {
    "1": "e30000",
    "2": "02b31c",
    "3": "1510f0",
    "4": "8900bf",
    "-": "777777",
}


def colorize(tone=None):
    col = COLS[tone]
    return f'<span style="color:#{col}">■</span>'


def colorize_word(pinyin):
    split = re.split(r"[1-4]", pinyin)
    n = len(split)
    if n == 1 or n == 2 and split[-1] == "":
        n_syl = 1
    else:
        n_syl = 2

    tones = re.findall(r"[1-4]", pinyin)
    if len(tones) == 1 and n_syl == 2:
        tones.append("-")

    colors = "".join(colorize(t) for t in tones)
    return colors


def select(name):
    return re.match(REGEX, name) and "tmp" not in name


def to_pinyin(word):
    return "".join(x[0] for x in pypinyin.pinyin(word, style=pypinyin.Style.TONE3))


def pjoin(items):
    return "<br>".join(items)


files = sorted(list(media_dir.glob("*.mp3")))
# print("\n".join(p.name for p in files[:100]))

files = [p for p in files if select(p.name)]

# files = [p.name for p in files]
# files = [name for name in files if to_pinyin(name.split('.')[0]) in SELECTION]

by_pinyin = defaultdict(dict)

for i, path in enumerate(files):

    name = path.name
    # identifier = path.stem
    # pinyin = identifier.split("_")[0]
    pinyin = to_pinyin(path.stem)
    pinyin_no_tone = re.sub(r"[0-9]", "", pinyin)
    # print(pinyin_no_tone)
    by_pinyin[pinyin_no_tone][pinyin] = path

min_variants = 4
by_pinyin = {pinyin: paths for pinyin, paths in by_pinyin.items() if len(paths) >= min_variants}

for pinyin_no_tone, paths_dict in by_pinyin.items():

    paths = paths_dict.values()

    identifier = pinyin_no_tone
    sound_str = pjoin(f"[sound:{sound_prefix.joinpath(path.name)}]" for path in paths)
    hanzi_str = pjoin(p.stem for p in paths)
    pinyins = [to_pinyin(path.stem) for path in paths]
    pinyin_str = pjoin(pinyins)

    colors = [colorize_word(p) for p in pinyins]
    color_str = pjoin(colors)

    # initials = [re.findall(INITIAL, sound)[0] for sound in sounds]
    # final = pinyin[len(initials):-1]
    initials = ""
    finals = ""
    # print(identifier, pinyin, sound, initials, finals, tones_str, colors, sep="\t")
    # print(identifier, f'<img src="{identifier}.png">', sep="\t")
    print(identifier, hanzi_str, pinyin_str, color_str, sound_str, sep="\t")
