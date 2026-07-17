# Python Implementation Guide

Best practices for implementing Python stages in this repo. This is a learning lab (see the [repo root README](../README.md) and [CLAUDE.md](../CLAUDE.md)), so "best practice" here means *clear, idiomatic, well-explained* code — not the terse, comment-light style you'd write for a production team that already knows the domain.

## Environment & dependencies

- All Python stages share the one virtual environment at the repo root (`.venv`) — don't create a per-stage venv. Activate it before running anything.
- Add any new direct dependency to the root `requirements.in`, then recompile `requirements.txt` with pip-tools. Full commands are in the root [README.md](../README.md#python-setup).
- Never `pip install` ad hoc without also updating `requirements.in` — the lockfile must stay authoritative.

## Project layout within a stage

- Prefer a flat, obvious layout for small stages: a handful of `.py` files at the top of the stage folder is fine — don't force a `src/` package layout until the stage genuinely has enough modules to need it.
- If a stage grows into a real package, use the standard shape:
  ```
  <stage>/
    README.md
    main.py            # entry point / demo of the stage
    <topic>.py          # supporting modules
    tests/
      test_<topic>.py
  ```
- Keep one concept per file. Beginners (future-you) should be able to guess a file's contents from its name.

## Style & readability

- Follow [PEP 8](https://peps.python.org/pep-0008/) naming and layout (`snake_case` for functions/variables, `PascalCase` for classes, 4-space indents).
- Use type hints on function signatures (`def fetch(url: str) -> dict:`) — they're free documentation and most beginner-facing errors surface earlier with them.
- **Comment generously**, per the repo-wide convention: explain *why* a step is needed (e.g. why a retry/backoff exists, why a particular library was chosen over the stdlib alternative), not just what the line does.
- Use docstrings on modules and non-trivial functions summarizing purpose, inputs, and outputs — short is fine, but don't skip them.
- Prefer explicit control flow over clever one-liners (e.g. a small loop over a dense nested comprehension) when it makes the logic easier to follow.
- Handle errors where the book/stage material expects it (e.g. a network call in a scraping stage should handle request failures) — don't add speculative error handling for cases the stage doesn't cover.

## Formatting & linting

- Format with [`black`](https://black.readthedocs.io/) and lint with [`ruff`](https://docs.astral.sh/ruff/) if/when a stage's dependencies are set up — add both to `requirements.in` the first time they're needed rather than pre-installing them speculatively.
- Default line length: 88 characters (black's default).

## Testing

- Use [`pytest`](https://docs.pytest.org/). Put tests in a `tests/` folder inside the stage, named `test_*.py`.
- Not every stage needs exhaustive tests — this is a learning lab, so tests are most valuable where they help verify understanding of the stage's core mechanic (e.g. a parsing function in a scraping stage), not as blanket coverage.
- Run a single stage's tests from the repo root with the venv active: `pytest <stage>/tests`.

## Running stage code

- Each stage's `README.md` should document how to run its code (e.g. `python <stage>/main.py`) — keep that instruction accurate as the stage evolves.
