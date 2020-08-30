#!/usr/bin/env python
"""Add example sentences to anki deck.

TODO:
    [X] Dedupe examples (appear if a chracter appears more than once in a sentence)
"""
import itertools
import json
import re
from collections import defaultdict

import click
import pkuseg
import numpy as np
from tqdm import tqdm
from joblib import Parallel, delayed

import ankipandas

from color import colorize_word

PUNCT = r"([！？｡。\.,…，；])"
MAX_RANK = 1_000_000

tokenizer = pkuseg.pkuseg()
with open("ranks.json") as f:
    ranks = json.load(f)


def geometric_mean(ranks):
    return np.exp(np.mean(np.log(ranks)))


def difficulty(words):
    word_ranks = [ranks.get(word, MAX_RANK) + 1 for word in words]
    return geometric_mean(word_ranks)


def tokenize(line):
    return tokenizer.cut(line)


def tokenized_line(words):
    return " ".join(words)


def read_lines(input):
    raw_lines = [line.strip() for line in input if len(line.strip()) >= 4]

    lines_with_punct = itertools.chain.from_iterable(
        re.split(PUNCT, line) for line in raw_lines
    )
    no_short = [line for line in lines_with_punct if line]

    # clean up punctuation
    lines = set()
    for first, second in zip(no_short[::-1], no_short[1::]):
        if first not in PUNCT and second in PUNCT:
            lines.add(f"{first}{second}")

    print(f"Number of deduped lines {len(lines)}.")

    return lines


def group_by_char(lines):
    by_char = defaultdict(set)
    for line in lines:
        for char in line:
            by_char[char].add(line)

    n_chars = len([v for v in by_char.values() if v])
    print(f"Number of chars with examples {n_chars}")

    n_examples = sum([len(v) for v in by_char.values()])
    print(f"Total number of examples {n_examples}")
    return by_char


def sort_char_example(char, examples):
    tokenized_examples = [tokenize(example) for example in examples]
    # presort to (hopefully) make ties deterministic
    return char, sorted(sorted(tokenized_examples), key=difficulty)


def sort_examples(by_char):
    sorted_examples = Parallel(n_jobs=-1, verbose=2, backend="multiprocessing")(
        delayed(sort_char_example)(char, examples) for char, examples in by_char.items()
    )
    return dict(sorted_examples)


def to_html(char, examples):
    examples_with_bold_word = [
        "".join(colorize_word(word) if char in word else word for word in example)
        for example in examples
    ]
    return "<br>".join(examples_with_bold_word)


def extract(by_char, char):
    return by_char.get(char, [])[:4]


def save_anki(by_char):
    col = ankipandas.Collection()

    han = col.notes[col.notes.nmodel == "Hanzi Writing"].copy()

    han.fields_as_columns(inplace=True)

    chars = list(han.nfld_Hanzi)
    examples = [to_html(char, extract(by_char, char)) for char in chars]
    print()
    print("\n".join(examples[:10]))
    print()
    han["nfld_Examples"] = examples

    han.fields_as_list(inplace=True)

    col.notes.update(han)
    print(col.summarize_changes())

    if click.confirm("Do you want to save? CAREFUL"):
        print("SAVING...")
        col.write(modify=True)
        print("SAVED.")


def main(input, write):
    lines = read_lines(input)
    by_char = group_by_char(lines)
    examples = sort_examples(by_char)

    if write:
        save_anki(examples)


@click.command()
@click.argument("input", type=click.File("r"))
@click.option("--write", is_flag=True)
def cli(input, write):

    main(input, write)
    # lines = [f"{text}{punct}" for text, punct in zip(no_short[::2], no_short[1::2])]


if __name__ == "__main__":
    col = cli()
