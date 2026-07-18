"""The Flask app: REST endpoints, backend-agnostic.

Every route here calls a `repository` object rather than touching
data-process's files or the sqlite database directly - `create_app()`
below decides *which* repository (file or sqlite) based on
`DATA_SERVE_BACKEND`, but from a route's point of view it's just "the
thing with get_all()/get_one()/get_artwork_response()/count()". This is
what makes both backends serve byte-identical JSON shapes from the same
routes, and what tests/test_app.py's parametrized tests are checking.

## Endpoints

- `GET /api/meta` - which backend is active, and how many Pokemon it has.
- `GET /api/pokemon` - a page of Pokemon (structured data), optionally
  filtered with `?type=fire`, `?generation=1`, and paginated with
  `?limit=`/`?offset=` (defaults: 50, 0).
- `GET /api/pokemon/<name>` - one Pokemon's structured data.
- `GET /api/pokemon/<name>/artwork` - that Pokemon's artwork image
  (unstructured data) as raw JPEG bytes, not JSON.
"""

from __future__ import annotations

import os

from flask import Flask, abort, jsonify, request
from flask_cors import CORS

from config import IMAGES_DIR, POKEDEX_JSON_PATH, SQLITE_DATABASE_URI
from file_repository import FileRepository
from models import db
from sqlite_repository import SQLiteRepository


def create_app(
    backend_name: str | None = None,
    *,
    json_path=None,
    images_dir=None,
    sqlite_uri: str | None = None,
) -> Flask:
    """Build the Flask app for one backend.

    `backend_name` defaults to the DATA_SERVE_BACKEND environment
    variable (see README.md), falling back to "file" if that's unset -
    so `python app.py` with no setup at all still works.

    The `json_path`/`images_dir`/`sqlite_uri` overrides exist for
    tests/test_app.py, which points each backend at a small synthetic
    dataset under `tmp_path` instead of the real data-process output.
    """
    backend_name = backend_name or os.environ.get("DATA_SERVE_BACKEND", "file")

    app = Flask(__name__)
    app.config["BACKEND_NAME"] = backend_name

    # d3-interactive-web is served by http-server on its own port (e.g.
    # localhost:8080), so its browser-side fetch()/d3.json() calls to this
    # API (localhost:5000) are cross-origin - without this, the browser
    # blocks the response before JS ever sees it. Only /api/* needs it;
    # this app has no other routes to protect.
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    if backend_name == "file":
        repository = FileRepository(
            json_path or POKEDEX_JSON_PATH, images_dir or IMAGES_DIR
        )
    elif backend_name == "sqlite":
        app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_uri or SQLITE_DATABASE_URI
        db.init_app(app)
        repository = SQLiteRepository()
    else:
        raise ValueError(f"Unknown DATA_SERVE_BACKEND {backend_name!r} - expected 'file' or 'sqlite'")

    @app.get("/api/meta")
    def get_meta():
        return jsonify({"backend": backend_name, "count": repository.count()})

    @app.get("/api/pokemon")
    def list_pokemon():
        type_filter = request.args.get("type")
        generation_filter = request.args.get("generation", type=int)
        limit = request.args.get("limit", default=50, type=int)
        offset = request.args.get("offset", default=0, type=int)

        results = repository.get_all(
            type_filter=type_filter,
            generation_filter=generation_filter,
            limit=limit,
            offset=offset,
        )
        return jsonify(results)

    @app.get("/api/pokemon/<name>")
    def get_pokemon(name: str):
        result = repository.get_one(name)
        if result is None:
            abort(404, description=f"No Pokemon named {name!r}")
        return jsonify(result)

    @app.get("/api/pokemon/<name>/artwork")
    def get_artwork(name: str):
        response = repository.get_artwork_response(name)
        if response is None:
            abort(404, description=f"No artwork for {name!r}")
        return response

    return app


if __name__ == "__main__":
    app = create_app()
    print(f"Starting data-serve with the {app.config['BACKEND_NAME']!r} backend")
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
