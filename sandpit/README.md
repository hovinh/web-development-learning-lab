# sandpit

A scratch area for quick, throwaway experiments that don't belong to a specific
curriculum stage — not part of the book's topic sequence.

## What's here

- `index.html` — loads `script.js`.
- `script.js` — sums a small array via a plain `for` loop and prints the
  result with `console.log`. Open the page and check the browser's dev tools
  console to see the output.

## Running the dev server

Requested command was `python -m SimpleHTTPServer`, but that module is
Python 2 only and this repo standardizes on Python 3.11 (see root
`CLAUDE.md`). The Python 3 equivalent was used instead:

```bash
python -m http.server
```

Run it from inside `sandpit/`, then open http://localhost:8000 in a browser.
