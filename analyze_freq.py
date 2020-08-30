#!/usr/bin/env python
# import os
import re

# import sys
from collections import Counter

import click
import pkuseg

# import jieba
# import numpy as np

# jieba.setLogLevel(60)  # quiet
# jieba.enable_paddle()

# fname = sys.argv[1]
# ofname = sys.argv[2]


def clean(text):
    # return "".join(re.replace(r"[\u4e00-\u9fff]+", text))
    return "".join(re.sub(r"([^\u4e00-\u9fff]+)", " ", text))


@click.command()
@click.argument("input", type=click.File("r"))
@click.argument("output", type=click.File("w"))
@click.option("--char-level", "-c", is_flag=True)
def cli(input, output, char_level):

    text = clean(input.read())

    # tokenizer = jieba.Tokenizer()
    if char_level:
        tokens = list(text.replace(" ", ""))
    else:
        tokenizer = pkuseg.pkuseg()
        tokens = tokenizer.cut(text)
    counter = Counter(tokens)
    for word, freq in sorted(counter.items(), key=lambda item: item[1], reverse=True):
        print(f"{word},{freq}", file=output)


if __name__ == "__main__":
    cli()
