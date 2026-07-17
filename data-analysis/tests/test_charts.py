"""Tests for charts.py's aggregation functions.

Only the pure `count_*`/`top_abilities` functions are tested here - a
saved chart PNG's pixels aren't a meaningful thing to assert on, so the
`plot_*` functions are instead verified by actually running main.py and
looking at the output (see README.md). A small synthetic dataset (4
entries) is used rather than the real pokedex.json, so these tests don't
depend on data-process having been run.
"""

from charts import count_by_generation, count_by_type, top_abilities

SAMPLE_POKEDEX = [
    {
        "name": "bulbasaur",
        "generation": 1,
        "types": ["Grass", "Poison"],
        "abilities": ["Overgrow", "Chlorophyll"],
    },
    {
        "name": "charmander",
        "generation": 1,
        "types": ["Fire"],
        "abilities": ["Blaze", "Solar Power"],
    },
    {
        "name": "squirtle",
        "generation": 1,
        "types": ["Water"],
        "abilities": ["Torrent", "Rain Dish"],
    },
    {
        "name": "chikorita",
        "generation": 2,
        "types": ["Grass"],
        "abilities": ["Overgrow"],
    },
]


def test_count_by_type_counts_dual_types_toward_both() -> None:
    counts = count_by_type(SAMPLE_POKEDEX)
    # bulbasaur contributes to both Grass and Poison, not just one.
    assert counts["Grass"] == 2
    assert counts["Poison"] == 1
    assert counts["Fire"] == 1
    assert counts["Water"] == 1


def test_count_by_generation() -> None:
    counts = count_by_generation(SAMPLE_POKEDEX)
    assert counts[1] == 3
    assert counts[2] == 1


def test_top_abilities_orders_by_frequency_and_respects_top_n() -> None:
    # "Overgrow" appears twice (bulbasaur, chikorita); every other
    # ability appears once - so it must be first regardless of
    # dict/insertion order.
    result = top_abilities(SAMPLE_POKEDEX, top_n=3)
    assert result[0] == ("Overgrow", 2)
    assert len(result) == 3
