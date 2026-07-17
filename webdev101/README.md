# webdev101

A single-page tour of the core building blocks of a web page: HTML
structure/text, CSS styling, SVG vector graphics, and Canvas drawing —
themed as a small Pokedex home page. It's a plain browser page with no
build step, so it can be opened directly or served with any static
file server.

## What's here

- `index.html` — the page markup: header, an intro section, and four
  demo sections (Pokemon list, SVG, 2D canvas, pseudo-3D canvas).
- `style.css` — all visual styling (layout, colors, type badges,
  canvas/button styling).
- `script.js` — all behavior, split into three independent pieces
  (see below).

## The four demo sections

1. **Text content from data** — `POKEMON_DATA` in `script.js` is a
   plain array of `{ name, type, description }` objects. `script.js`
   renders one `<li class="pokemon-card">` per entry into
   `#pokemon-list` using jQuery, rather than hand-typing each card in
   `index.html`. This is the basic "data drives markup" pattern used
   everywhere in real front-end code (Pokemon data here stands in for
   what would normally come from an API).

2. **SVG graphics** — the header's small Pokeball and the larger one
   in `#svg-demo` are both inline `<svg>` markup (not `<img>` tags),
   built from basic shapes (`circle`, `path`, `rect`). Because inline
   SVG becomes real DOM elements, the big Pokeball can animate itself
   with SVG's built-in `<animateTransform>` — no JavaScript needed for
   that spin.

3. **2D canvas animation** — `#canvas-2d` in `script.js`
   (`setupCanvas2dDemo`) draws a circle, a square, and a triangle that
   bounce off the canvas walls. Canvas is a raster surface: nothing
   drawn is remembered as a DOM element, so every frame clears the
   canvas and redraws all shapes from scratch via
   `requestAnimationFrame`. Pause/Resume and Reset buttons are wired
   with jQuery event handlers.

4. **Pseudo-3D canvas animation** — `#canvas-3d`
   (`setupCanvas3dDemo`) hand-rolls the classic "rotating wireframe
   cube" technique instead of pulling in WebGL or a 3D library: the
   cube's 8 corners are kept as `(x, y, z)` points, rotated each frame
   with basic trigonometric rotation matrices, then perspective-projected
   down to flat 2D canvas coordinates before drawing lines between
   connected corners. This is the same manual approach used before
   WebGL existed, and it's a good way to see *why* 3D math is needed —
   the canvas API itself only ever draws in 2D.

## Why jQuery here

Per [docs/javascript.md](../docs/javascript.md), stages that touch the
DOM lean on jQuery for selection and event binding rather than raw
`document.querySelector`/`addEventListener`. It's loaded from a CDN
`<script>` tag in `index.html` (no `package.json`/bundler) since this
is a plain, buildless browser page.

## Running the page

From inside `webdev101/`, serve it with Python's built-in static
server (same approach as the `sandpit` stage):

```bash
python -m http.server
```

Then open http://localhost:8000 in a browser.
