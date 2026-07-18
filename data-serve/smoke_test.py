"""Manual smoke test: hits a *running* data-serve server over real HTTP.

Unlike tests/test_app.py (which uses Flask's in-process test_client() and
never opens a real socket), this script is meant to be run by hand
against a server you've actually started - the check that the whole
thing works end-to-end as an HTTP API, not just that the Flask routing
logic is correct. Start a server first (either backend):

    python data-serve/app.py
    # or: DATA_SERVE_BACKEND=sqlite python data-serve/app.py

then, in another terminal:

    python data-serve/smoke_test.py
    python data-serve/smoke_test.py --base-url http://localhost:5000

Exits with a non-zero status if any check fails, so it's usable as a
quick pass/fail gate, not just eyeballed output.
"""

from __future__ import annotations

import argparse
import sys

import requests


def check(description: str, condition: bool) -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {description}")
    return condition


def run(base_url: str) -> bool:
    all_passed = True

    meta = requests.get(f"{base_url}/api/meta", timeout=5)
    all_passed &= check("GET /api/meta -> 200", meta.status_code == 200)
    backend = meta.json().get("backend")
    count = meta.json().get("count")
    print(f"       backend={backend!r}, count={count}")
    all_passed &= check("meta.count is a positive number", isinstance(count, int) and count > 0)

    listing = requests.get(f"{base_url}/api/pokemon", params={"limit": 5}, timeout=5)
    all_passed &= check("GET /api/pokemon?limit=5 -> 200", listing.status_code == 200)
    entries = listing.json()
    all_passed &= check("...returns exactly 5 entries", len(entries) == 5)
    all_passed &= check(
        "...sorted by national_number",
        [e["national_number"] for e in entries] == sorted(e["national_number"] for e in entries),
    )

    filtered = requests.get(
        f"{base_url}/api/pokemon", params={"type": "fire", "generation": 1}, timeout=5
    )
    all_passed &= check("GET /api/pokemon?type=fire&generation=1 -> 200", filtered.status_code == 200)
    fire_gen1 = filtered.json()
    all_passed &= check(
        "...every result is actually Fire-type and Generation 1",
        all(e["generation"] == 1 and "Fire" in e["types"] for e in fire_gen1),
    )

    detail = requests.get(f"{base_url}/api/pokemon/pikachu", timeout=5)
    all_passed &= check("GET /api/pokemon/pikachu -> 200", detail.status_code == 200)
    pikachu = detail.json()
    all_passed &= check("...name is 'pikachu'", pikachu.get("name") == "pikachu")
    all_passed &= check(
        "...artwork_url points back at this API, not a local path",
        pikachu.get("artwork_url") == "/api/pokemon/pikachu/artwork",
    )

    missing = requests.get(f"{base_url}/api/pokemon/missingno", timeout=5)
    all_passed &= check("GET /api/pokemon/missingno -> 404", missing.status_code == 404)

    artwork = requests.get(f"{base_url}/api/pokemon/pikachu/artwork", timeout=5)
    all_passed &= check("GET /api/pokemon/pikachu/artwork -> 200", artwork.status_code == 200)
    all_passed &= check(
        "...Content-Type is image/jpeg",
        artwork.headers.get("Content-Type", "").startswith("image/jpeg"),
    )
    all_passed &= check(
        "...body actually starts with a JPEG magic number",
        artwork.content[:3] == b"\xff\xd8\xff",
    )

    return all_passed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default="http://localhost:5000",
        help="Where the running data-serve server is listening (default: %(default)s)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"Smoke-testing {args.base_url} ...\n")
    try:
        passed = run(args.base_url)
    except requests.exceptions.ConnectionError:
        print(f"\nSmoke test errored out: could not connect to {args.base_url}")
        print('Is a server actually running? See README.md\'s "Running" section.')
        sys.exit(1)
    print("\nAll checks passed." if passed else "\nSome checks FAILED.")
    sys.exit(0 if passed else 1)
