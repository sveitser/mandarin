# Mandarin tools

A variety of utilities to help with studying Mandarin.

In its current state this repo only serves as backup purpose.

Code may not work or make sense.

## Installation

Install `nix` package manager and activate with `nix-shell`.

    pip install ankipandas
   
[TODO] Dictionary and word frequency list.

## Usage

Visualize difficulty of texts based on word frequencies
    
    python plot-freq.py texts/*.*

Add example sentences to anki character cards

    python anki_hanzi_examples.py (cat texts/*.*|psub) --write
    
Make anki decks for tones
    
    TODO
