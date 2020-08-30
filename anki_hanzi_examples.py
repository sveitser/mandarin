#!/usr/bin/env python
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

PUNCT = r"([！？｡。\.,…，；])"
MAX_RANK = 1_000_000

tokenizer = pkuseg.pkuseg()
with open("ranks.json") as f:
    ranks = json.load(f)
# TODO: should add to existing examples, not overwrite


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
    lines = []
    for first, second in zip(no_short[::-1], no_short[1::]):
        if first not in PUNCT and second in PUNCT:
            lines.append(f"{first}{second}")

    print(f"Number of selected lines {len(lines)}.")

    # dedupe
    seen = set()
    selected = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            selected.append(line)

    print(f"Number of deduped lines {len(selected)}.")

    return selected


def group_by_char(lines):
    by_char = defaultdict(list)
    for _, line in enumerate(lines):
        for char in line:
            by_char[char].append(line)

    n_chars = len([v for v in by_char.values() if v])
    n_examples = sum([len(v) for v in by_char.values()])
    print(f"Number of chars with examples {n_chars}")
    print(f"Total number of examples {n_examples}")
    return by_char


def sort_char_example(char, examples):
    tokenized_examples = [tokenize(example) for example in examples]
    return char, sorted(tokenized_examples, key=difficulty)


def sort_examples(by_char):
    sorted_examples = {}
    # for char, examples in tqdm(by_char.items(), "sorting"):
    #     tokenized_examples = [tokenize(example) for example in examples]
    #     sorted_examples[char] = sorted(tokenized_examples, key=difficulty)
    sorted_examples = Parallel(n_jobs=-1, verbose=2, backend="multiprocessing")(
        delayed(sort_char_example)(char, examples) for char, examples in by_char.items()
    )
    return dict(sorted_examples)


def render(char, examples):
    examples_with_bold_word = [
        "".join(f" <b>{word}</b> " if char in word else word for word in example)
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
    examples = [render(char, extract(by_char, char)) for char in chars]
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
