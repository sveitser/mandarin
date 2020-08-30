#!/usr/bin/env python
import os
import sys

import jieba
import numpy as np

jieba.setLogLevel(60)  # quiet

fname = sys.argv[1]

with open(fname) as f:
    text = f.read()

tokenizer = jieba.Tokenizer()
tokens = list(tokenizer.cut(text))
occurences = np.array([tokenizer.FREQ[w] for w in tokens if w in tokenizer.FREQ])
difficulties = 1 / (occurences + 1)

max_occurence = np.max(list(tokenizer.FREQ.values()))
min_score = 1 / (max_occurence + 1)
max_score = 1


perc = 75
mean = np.mean(difficulties)
median = np.percentile(difficulties, perc)


def norm(x):
    return (x - min_score) / (max_score - min_score)


normalized_mean = norm(mean)
normalized_median = norm(median)

print(
    f"{os.path.basename(fname)}: "
    f"mean: {normalized_mean:.6f}, {perc}th percentile: {normalized_median:.6f} "
    f"in [0: trivial, 1: hardest]"
)


import matplotlib.pyplot as plt

clipped = difficulties[(difficulties <= 0.01) & (difficulties >= 0.0001)]
plt.hist(clipped, bins=20, density=True)
ax = plt.gca()
ax.set_title(fname)
plt.show()
