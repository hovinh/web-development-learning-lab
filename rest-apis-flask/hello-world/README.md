# hello-world

First stage of *Building REST APIs with Flask* — the smallest possible
Flask app, to confirm the environment works before building anything
REST-shaped.

## What's here

- [`main.py`](main.py) — a single `/` route that returns the plain-text
  string `"Hello, World!"`. See the [book's README](../README.md#what-flask-actually-is)
  for what Werkzeug and Jinja2 each contribute to Flask; this stage only
  exercises Werkzeug's routing/response side (there's no template here).

## Running it

From the repo root, with the shared venv active:

```bash
.venv\Scripts\Activate.ps1   # PowerShell
python rest-apis-flask/hello-world/main.py
```

Then open http://127.0.0.1:5000/ — it should show `Hello, World!`.

`debug=True` in `main.py` enables Werkzeug's auto-reload (edits to the
file are picked up without restarting the server) and its interactive
in-browser debugger on unhandled exceptions.
