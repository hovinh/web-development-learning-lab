"""Aggregation + plotting functions for the data-analysis stage.

Split into two halves on purpose:
  - the `count_*`/`top_abilities` functions are pure - a list of dicts in,
    a plain Counter/list out, no matplotlib involved. These hold the
    actual "how do you summarize this data" logic, so they're what
    tests/test_charts.py tests.
  - the `plot_*` functions take that summary and draw it. There's nothing
    to unit-test there (a saved PNG's *pixels* aren't a meaningful
    assertion) - `main.py` running end-to-end and eyeballing the output
    is the real check for those, same as this repo's other stages treat
    a demo script as the check for wiring rather than for logic.

Chart/color choices follow a "magnitude comparison, one series" recipe:
every chart here answers "how many/how much", not "which of several
named series is bigger", so each one is a single flat hue rather than a
multi-color palette - see the module-level color constants below and
data-analysis/README.md's "Chart design notes" for the reasoning.
"""

from __future__ import annotations

import collections
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # no display available/needed - only ever saving to a file
import matplotlib.pyplot as plt

# A single flat hue for every chart: none of these charts compare named
# series against each other (that's what a multi-color categorical
# palette is for) - each one is "how many Pokemon per X", a single-series
# magnitude comparison, so one color is not just enough but *correct*:
# shading bars by their own value would spend the color channel
# re-encoding what the bar length already shows.
SERIES_COLOR = "#2a78d6"  # categorical slot 1 ("blue")

# Chrome/ink - kept muted and out of the data's way, per the same
# "text never wears the data color" rule.
PRIMARY_INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
MUTED_INK = "#898781"
GRIDLINE = "#e1e0d9"
SURFACE = "#fcfcfb"


def count_by_type(pokedex: list[dict[str, Any]]) -> collections.Counter:
    """How many Pokemon have each type - a Pokemon with two types (e.g.
    Bulbasaur: Grass, Poison) counts toward both, so counts don't sum to
    len(pokedex)."""
    return collections.Counter(
        type_name for entry in pokedex for type_name in entry["types"]
    )


def count_by_generation(pokedex: list[dict[str, Any]]) -> collections.Counter:
    """How many Pokemon belong to each generation (1-6)."""
    return collections.Counter(entry["generation"] for entry in pokedex)


def top_abilities(pokedex: list[dict[str, Any]], top_n: int = 15) -> list[tuple[str, int]]:
    """The `top_n` most common abilities across the whole Pokedex, most
    common first. Like count_by_type(), a Pokemon with two abilities
    counts toward both."""
    counts = collections.Counter(
        ability for entry in pokedex for ability in entry["abilities"]
    )
    return counts.most_common(top_n)


def _style_axes(ax: plt.Axes) -> None:
    """Shared, minimal chart chrome: hairline gridlines, muted ticks, no
    heavy border - so bars/points stay the loudest thing in the figure."""
    ax.set_facecolor(SURFACE)
    ax.grid(color=GRIDLINE, linewidth=1, zorder=0)
    ax.set_axisbelow(True)  # gridlines behind the data, not on top of it
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(colors=MUTED_INK, labelcolor=SECONDARY_INK)


def plot_horizontal_bar(
    counts: dict[str, int],
    title: str,
    output_path: Path,
) -> None:
    """A sorted, descending horizontal bar chart for one series of
    counts, with the value labeled at each bar's tip - the shared shape
    behind pokemon_by_type.png and top_abilities.png (both are "how many
    Pokemon have X", just for a different X, and horizontal because both
    have longer category names that would collide as a column chart's
    x-axis labels).
    """
    # Sort ascending so the *largest* bar ends up at the top of the
    # chart once matplotlib's barh() draws bottom-to-top.
    labels_and_counts = sorted(counts.items(), key=lambda pair: pair[1])
    labels = [label for label, _ in labels_and_counts]
    values = [value for _, value in labels_and_counts]

    fig, ax = plt.subplots(figsize=(8, max(4, len(labels) * 0.35)))
    _style_axes(ax)

    bars = ax.barh(labels, values, color=SERIES_COLOR, zorder=2)

    # Direct value labels at each bar's tip - the one series here *is*
    # the story, so labeling every bar (rather than just the extremes)
    # is the readable choice, not the "never a number on every point"
    # anti-pattern that applies to a busy multi-series chart.
    ax.bar_label(bars, padding=4, color=SECONDARY_INK)

    ax.set_title(title, color=PRIMARY_INK, fontsize=14, loc="left")
    ax.set_xlabel("Number of Pokemon", color=SECONDARY_INK)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def plot_generation_bar(counts: dict[int, int], output_path: Path) -> None:
    """A column chart of Pokemon count per generation, in generation
    order (1-6) rather than sorted by count - unlike types/abilities,
    generation has a natural, meaningful order that sorting would
    destroy."""
    generations = sorted(counts.keys())
    values = [counts[generation] for generation in generations]

    fig, ax = plt.subplots(figsize=(7, 5))
    _style_axes(ax)

    bars = ax.bar(generations, values, color=SERIES_COLOR, zorder=2)
    ax.bar_label(bars, padding=4, color=SECONDARY_INK)

    ax.set_title("Pokemon per Generation", color=PRIMARY_INK, fontsize=14, loc="left")
    ax.set_xlabel("Generation", color=SECONDARY_INK)
    ax.set_ylabel("Number of Pokemon", color=SECONDARY_INK)
    ax.set_xticks(generations)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def plot_height_vs_weight(pokedex: list[dict[str, Any]], output_path: Path) -> None:
    """A scatter of every Pokemon's height against its weight.

    Not colored by type: with 18 types, a categorical palette would
    exceed the ~8-hue ceiling a reader can actually tell apart (see
    README's "Chart design notes"), so this stays a single-hue scatter -
    the relationship between the two axes is the point, not which type
    each dot belongs to.

    Both axes are log-scaled: height ranges from 0.1m to 14.5m and
    weight from 0.1kg to 950kg in this dataset - a linear scale would
    crush nearly every Pokemon into the bottom-left corner to leave room
    for a handful of giants (Wailord, Groudon, ...).
    """
    heights = [entry["height_m"] for entry in pokedex]
    weights = [entry["weight_kg"] for entry in pokedex]

    fig, ax = plt.subplots(figsize=(7, 6))
    _style_axes(ax)

    # alpha < 1 so overlapping points (many Pokemon share similar
    # height/weight) show up as a darker cluster instead of hiding each
    # other completely.
    ax.scatter(heights, weights, color=SERIES_COLOR, alpha=0.5, s=28, zorder=2)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title("Height vs. Weight", color=PRIMARY_INK, fontsize=14, loc="left")
    ax.set_xlabel("Height (m, log scale)", color=SECONDARY_INK)
    ax.set_ylabel("Weight (kg, log scale)", color=SECONDARY_INK)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def make_all_charts(pokedex: list[dict[str, Any]], charts_dir: Path) -> None:
    """Build every chart this stage produces into `charts_dir`."""
    charts_dir.mkdir(exist_ok=True)

    plot_horizontal_bar(
        count_by_type(pokedex),
        title="Pokemon per Type",
        output_path=charts_dir / "pokemon_by_type.png",
    )
    plot_generation_bar(
        count_by_generation(pokedex),
        output_path=charts_dir / "pokemon_by_generation.png",
    )
    plot_horizontal_bar(
        dict(top_abilities(pokedex, top_n=15)),
        title="Top 15 Most Common Abilities",
        output_path=charts_dir / "top_abilities.png",
    )
    plot_height_vs_weight(pokedex, output_path=charts_dir / "height_vs_weight.png")
