#!/usr/bin/env python
import os
import re
import json
from collections import Counter

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

import jieba
import pkuseg
import click
import pandas as pd
import numpy as np

# fontFiles = fm.findSystemFonts(".")
# fontList = fm.createFontList(fontFiles)
# fm.fontManager.ttflist.extend(fontList)

MAX = 500_000

font = {"family": ["KaiTi"], "weight": "bold", "size": 22}

matplotlib.rc("font", **font)

# tokenizer = jieba.Tokenizer()
tokenizer = pkuseg.pkuseg()

with open("ranks.json") as f:
    ranks = json.load(f)


with open("cc-edict-words.txt") as f:
    all_words = set(line.strip() for line in f)


def keep_word(word):
    is_cjk = not re.search(r"[^\u4e00-\u9fff]", word)
    in_dict = word in all_words
    return is_cjk and in_dict and len(word) <= 2


def tokenize(text):
    tokens = tokenizer.cut(text)
    tokens = [word for word in tokens if keep_word(word)]
    return tokens


def load(fname):
    print(f"Loading {fname}")
    with open(fname) as f:
        text = f.read()
    return tokenize(text)


def to_cum_dist(tokens):

    counter = Counter(tokens)
    words = {}
    dist = np.zeros(MAX + 1, dtype=np.float64)
    total = 0
    for word, occurrence in sorted(
        counter.items(), key=lambda item: item[1], reverse=True
    ):

        if word in ranks:
            rank = ranks[word]
            occ = int(occurrence)
            if rank <= MAX:
                dist[rank] = occ
            total += occ

    return dist / total


def process(fname):
    tokens = load(fname)
    return to_cum_dist(tokens)


@click.command()
@click.argument("fnames", nargs=-1)
def main(fnames):
    df = pd.DataFrame()
    for fname in fnames:
        name = os.path.basename(os.path.splitext(fname)[0])
        df[name] = process(fname)

    print(df)

    cumulative = df.cumsum(axis=0)
    ax = cumulative.plot(linewidth=2)
    ax.grid()
    ax.set_ylim(0, 1)
    ax.set_xlim(100, None)
    ax.set_xscale("log")
    ax.set_ylabel("Fraction of text covered")
    ax.set_xlabel("Word rank")
    plt.show()


if __name__ == "__main__":
    main()
