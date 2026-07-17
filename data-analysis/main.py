"""Entry point/demo for the data-analysis stage.

Reads data-process's cleaned dataset and saves four PNG charts into
charts/ - see README.md for what each one shows and why that chart type/
color was chosen.
"""

from __future__ import annotations

import json
from pathlib import Path

from charts import make_all_charts

STAGE_DIR = Path(__file__).parent
POKEDEX_JSON_PATH = STAGE_DIR.parent / "data-process" / "pokedex.json"
CHARTS_DIR = STAGE_DIR / "charts"


def main() -> None:
    if not POKEDEX_JSON_PATH.exists():
        raise FileNotFoundError(
            f"{POKEDEX_JSON_PATH} not found - run data-process/process_pokedex.py first"
        )

    with POKEDEX_JSON_PATH.open(encoding="utf-8") as json_file:
        pokedex = json.load(json_file)

    make_all_charts(pokedex, CHARTS_DIR)
    print(f"Saved 4 charts for {len(pokedex)} Pokemon into {CHARTS_DIR}")


if __name__ == "__main__":
    main()
