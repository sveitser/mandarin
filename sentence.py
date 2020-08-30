#!/usr/bin/env python
import fileinput
import json
import os
import sys

import jieba
import numpy as np
from tabulate import tabulate

jieba.setLogLevel(60)  # quiet

text = next(iter(fileinput.input())).strip()
# text = "blah"

tokenizer = jieba.Tokenizer()
tokens = tokenizer.cut(text)
tokens = list(set([tok for tok in tokens if tok in tokenizer.FREQ]))

with open("global_wordfreq.release_UTF-8.json") as f:
    ranks = json.load(f)

# words_ranked_high_to_low = sorted(tokenizer.FREQ, key=rank_dict.get)
# ranks = {word: rank for rank, word in enumerate(words_ranked_high_to_low)}

# max_occurence = np.max(list(tokenizer.FREQ.values()))
# min_difficulty = 1 / (max_occurence + 1)
#
# min_occurence = 1
# max_difficulty = 1 / (min_occurence + 1)

rank = [ranks.get(w, -1) for w in tokens]
tokens, rank = list(zip(*sorted(zip(tokens, rank), key=lambda item: item[1])))
# occurences = np.array([tokenizer.FREQ[w] for w in tokens])
# difficulties = 1 / (occurences + 1)
# difficulties -= min_difficulty
# difficulties /= max_difficulty - min_difficulty

print(tabulate({"词": tokens, "难度": rank}, headers="keys"))  # floatfmt=".6f",
