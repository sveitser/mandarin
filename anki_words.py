#!/usr/bin/env python
import collections
import itertools
import json
import re

import ankipandas
from pypinyin import pinyin, Style

max_words = 10

MAX_RANK = 30_000
freq = json.load(open("global_wordfreq.release_UTF-8.json"))
freq = {word: rank for word, rank in freq.items() if rank <= MAX_RANK}

COLS = {
    "1": "e30000",
    "2": "02b31c",
    "3": "1510f0",
    "4": "8900bf",
    "5": "777777",
}


def colorize_char(char, tone):
    col = COLS[tone]
    return f'<span style="color:#{col}">{char}</span>'


def colorize_word(word):
    pinyin_syllabels = pinyin(word, style=Style.TONE3, heteronym=False)
    tones = [syl[0][-1] for syl in pinyin_syllabels]
    tones = [tone if tone.isdigit() else "5" for tone in tones]
    #print(word, tones)
    return "".join(colorize_char(char, tone) for char, tone in zip(word, tones))


col = ankipandas.Collection()

han = col.notes[col.notes.nmodel == "Hanzi Writing"].copy()

han.fields_as_columns(inplace=True)

chars = list(han.nfld_Hanzi)
chars_in_col = set(chars)

words = collections.defaultdict(list)

for word, rank in sorted(freq.items(), key=lambda x: x[1]):
    print(word, rank)
    for char in word:
        if char in chars_in_col and len(words[char]) < max_words:
            try:
                colored = colorize_word(word)
            except KeyError as exc:
                print(f"unable to colorize {word}, {exc}")
                continue
            #words[char].append(f"{colored}: {rank}")
            words[char].append(colored)

words = {k: v[:max_words] for k, v in words.items()}
words = {k: "<br>".join(v) for k, v in words.items()}

# print(list(words.items())[:10])
char_words = [words.get(c, "") for c in chars]
han["nfld_Words"] = char_words

han.fields_as_list(inplace=True)

col.notes.update(han)
print(col.summarize_changes())
