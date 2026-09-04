# data-analysis

Turns [`data-process`](../data-process/README.md)'s cleaned
`pokedex.json` into four saved PNG charts, exploring what's actually in
the compiled dataset: how Pokemon are distributed across types,
generations, common abilities, and the relationship between height and
weight.

## The idea

Every chart here is answering a "how many/how much" question about one
thing at a time (not comparing several named series against each other),
so - per this repo's `dataviz` design conventions - each is a single flat
color rather than a multi-color palette. Coloring bars by their own
value, or splitting them across many hues, would spend a color channel
re-encoding information the bar's length or position already shows.

- **`pokemon_by_type.png`** - a horizontal bar per type (18 types),
  sorted descending, with the count labeled at each bar's tip.
  Horizontal because type names plus 3-digit counts don't fit as x-axis
  labels on a column chart without overlapping.
- **`pokemon_by_generation.png`** - a column per generation (1-6), kept
  in generation order rather than sorted by count, since generation has
  a real, meaningful order that sorting by size would destroy.
- **`top_abilities.png`** - the 15 most common abilities across all 721
  Pokemon (out of 190 distinct abilities total), same horizontal-bar
  shape as the type chart, for the same label-length reason.
- **`height_vs_weight.png`** - a scatter of every Pokemon's height
  against its weight, **not** colored by type. With 18 types, a
  categorical palette would exceed the ~8-hue ceiling a reader can
  actually keep distinct (see "Chart design notes" below) - so this
  stays a single-hue scatter where the height/weight relationship is the
  point, not which type each dot belongs to. Both axes are log-scaled:
  height ranges from 0.1m to 14.5m and weight from 0.1kg to 950kg in this
  dataset, and a linear scale would crush nearly every ordinary-sized
  Pokemon into one corner to leave room for a few giants (Wailord,
  Groudon, ...).

## Files

- `charts.py`:
  - `count_by_type()`/`count_by_generation()`/`top_abilities()` - pure
    functions, a list of Pokemon dicts in, a `Counter`/list out. These
    hold the actual "how do you summarize this data" logic, which is why
    they're what `tests/test_charts.py` tests - no matplotlib involved.
  - `plot_horizontal_bar()`/`plot_generation_bar()`/`plot_height_vs_weight()` -
    take that summary and draw it. Nothing here is unit-tested (a saved
    PNG's pixels aren't a meaningful assertion) - running `main.py` and
    looking at the output is the real check, the same way this repo's
    other stages treat a demo script as the check for wiring rather than
    for logic.
  - `make_all_charts()` - builds all four into a given folder.
- `main.py` - entry point: loads `data-process/pokedex.json`, calls
  `make_all_charts()`, prints how many Pokemon/charts were produced.
- `tests/test_charts.py` - tests the three aggregation functions against
  a small synthetic dataset (4 Pokemon), not the real `pokedex.json` -
  fast, and independent of whether `data-process` has been run yet.
- `conftest.py` - empty; lets `tests/` import `charts` without a package
  (same reasoning as the other data stages' `conftest.py`).
- `charts/` - the four generated PNGs; not committed (see root
  `.gitignore`) since they're fully reproducible from `data-process`'s
  output.

## Chart design notes

- **One flat color, not a value gradient.** A nominal bar (a type name, an
  ability name) never gets colored by its own count - that would spend
  the identity/color channel re-showing what the bar's length already
  communicates. All four charts use the same single blue
  (`charts.SERIES_COLOR`).
- **Why not color the scatter by type?** The series-count rule of thumb:
  1-3 series reads fine by color alone, 4 is where a colorblind-safe
  palette gets hard, and past ~7-8 you're past what any palette can keep
  pairwise distinct - at that point the right move is folding categories
  into "Other", faceting into small multiples, or (as here) dropping
  color entirely and letting a single hue carry the one relationship
  that matters. 18 types is well past that ceiling.
- **Direct value labels on every bar** (not just the extremes) - the
  general rule is to label sparingly since flooding a chart with numbers
  stops being readable, but that rule is about *multi-series* charts
  where the reader's already tracking several colors. Here there's only
  one series and it *is* the whole story, so a label per bar (15-18 of
  them, not hundreds) stays readable and saves a reader from estimating
  bar length against gridlines.
- **Muted chrome.** Gridlines, axis ticks, and axis labels are all a soft
  gray - only the bars/points are full color, so the data stays the
  loudest thing in the figure.

## Testing

```bash
pytest data-analysis/tests
```

## Running

Needs [matplotlib](https://matplotlib.org/), added to this repo's
`requirements.in`/`.txt` for this stage - sync the venv first if you
haven't already:

```bash
.venv/Scripts/python.exe -m piptools sync requirements.txt
```

Then, from the repo root with `.venv` active:

```bash
python data-analysis/main.py
```

Requires `data-process/pokedex.json` to already exist (run
`data-process/process_pokedex.py` first, which in turn needs
`data-scrape/compile_pokedex.py` to have produced `data-scrape/pokedex.csv`
- see those stages' READMEs).
