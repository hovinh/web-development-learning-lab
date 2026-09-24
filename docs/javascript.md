# JavaScript Implementation Guide

Best practices for implementing JavaScript stages in this repo. This is a learning lab (see the [repo root README](../README.md) and [CLAUDE.md](../CLAUDE.md)), so "best practice" here means *clear, idiomatic, well-explained* code — not the terse, comment-light style you'd write for a production team that already knows the domain.

## Environment & dependencies

- Unlike Python, JS stages manage their own dependencies locally — there is no shared root-level `node_modules` for stage code. Each JS stage that needs packages gets its own `package.json` inside the stage folder.
- Install stage dependencies from within the stage folder (`npm install <package>`), not from the repo root.
- Commit the stage's `package.json` and `package-lock.json`; do not commit `node_modules/` (already covered by the root `.gitignore`).
- **Exception**: the repo-root `package.json` holds dev tooling shared across stages rather than tied to any one of them — currently just [`http-server`](https://github.com/http-party/http-server) (`npm install` at the repo root, then `npm run serve -- <stage-folder>`), a lighter-weight alternative to `python -m http.server` for previewing a plain static page. It isn't a stage and gets no stage `README.md` — it's documented in the root `README.md`'s "JavaScript setup" section and [CLAUDE.md](../CLAUDE.md) instead. Add future genuinely repo-wide (not stage-specific) JS tooling here the same way; a stage's own dependencies still belong in that stage's own `package.json`.

## Preferred libraries

- Reach for **jQuery** actively wherever it fits, rather than defaulting to vanilla DOM APIs — this curriculum's browser-facing stages are built around it, so using it consistently keeps the code idiomatic to the material. Use it for DOM selection/traversal (`$(...)`), event binding (`.on(...)`), DOM mutation, and AJAX (`$.ajax`/`$.get`/`$.post`) in any stage that touches the DOM or makes HTTP requests from the browser.
- For collection/data work, prefer native **functional array methods** (`.map`, `.filter`, `.reduce`, `.forEach`, `.find`, etc.) over a utility library like Underscore/lodash — they're built in, well-documented, and closely match Underscore's own API, so there's nothing to gain from the extra dependency.
- Add jQuery as a dependency via the stage's `package.json` (`npm install jquery`), or load it from a `<script>` tag in `index.html` for stages that are plain browser pages without a build step — match whichever loading style the stage already uses.
- This preference doesn't override a stage that's explicitly *about* a different mechanism (e.g. the `javascript-prototype` stage is about the prototype chain itself, not DOM work, so it has no reason to reach for jQuery; `d3-interactive-web` is about D3's own selection/data-join model, so it uses D3 throughout instead of mixing in jQuery for the plain DOM bits). Use judgment: the point is idiomatic code for what the stage is teaching, not shoehorning a library in everywhere.
- A stage built around a specific charting/visualization library (D3, etc.) that the task says to load with no local install: import it as an ES module straight from a CDN (e.g. `import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";`) in whichever files need it, same spirit as jQuery's CDN `<script>` tag option above but keeping the module boundary — no bundler, no `node_modules` entry for that library, and the stage's own `package.json` (if it has one) lists no dependency for it.
- **Tailwind CSS: CDN browser build vs. a real build step** — the same "no Node" vs. "has a Node toolchain already" split as jQuery/D3 above, decided per stage. `demos/labeling-django/` has no Node toolchain (it's a Django project), so its `base.html` loads Tailwind 4 + daisyUI as browser builds straight from a CDN (`@tailwindcss/browser@4`) — simplest possible setup, but prototype-only: it recompiles the entire utility set on every page load with no purge step, and needs internet access. `demos/labeling-fastapi-react/web/` already has Vite for React, so it uses `@tailwindcss/vite` instead — Tailwind's official Vite plugin, which scans the source at dev/build time and ships only the utility classes actually used. Default to the CDN build for a stage with no other JS tooling, and to `@tailwindcss/vite` (or the standalone Tailwind CLI) for a stage that already has a Node build step for another reason.

## Project layout within a stage

- Prefer a flat layout for small stages: a handful of `.js` files at the top of the stage folder is fine — don't introduce a build step or bundler until the stage material actually calls for one.
- A typical stage shape:
  ```
  <stage>/
    README.md
    package.json
    index.js            # entry point / demo of the stage
    <topic>.js           # supporting modules
    tests/
      <topic>.test.js
  ```
- Keep one concept per file, same as the Python guide — a file's name should hint at its contents.
- **Exception: Angular CLI-scaffolded stages** (`angular-typescripts-beginner/`). A project created with `ng new` follows the Angular CLI's own generated layout (`angular.json`, `src/app/`, one component per `.ts`/`.html`/`.css`/`.spec.ts` file group, etc.) rather than this repo's flat default — don't restructure it to match. Document the exact `ng new`/`ng generate` command used (and why any non-default flag was chosen) in that stage's `README.md`, the same way `angular-typescripts-beginner/my-app/README.md` does, so the setup can be reproduced later without re-deriving the flag choices.
- **Exception: Vite-scaffolded React stages** (`demos/labeling-fastapi-react/web/`). Same reasoning as the Angular exception above, one level down: a project created with `npm create vite` follows Vite's own generated layout (`vite.config.js`, `index.html` at the project root, `src/main.jsx` as the entry point, one file per component under `src/components/`) rather than being flattened further. Document the exact scaffold command in that stage's `README.md` the same way, **including the Vite major version pinned** if the machine's Node version forced one (see `demos/labeling-fastapi-react/README.md`'s "Node/Vite constraint" section — Vite 7 requires Node `^20.19.0 || >=22.12.0`, so a machine on an older Node 20.x needs `npm create vite@6` instead of the unpinned `npm create vite`).

## Style & readability

- Use modern ES module syntax (`import`/`export`) rather than CommonJS (`require`), unless the specific stage/framework requires CommonJS (check the book's example first).
- Start plain (non-module) scripts with `'use strict';` as the first line to opt into strict mode — it catches common mistakes early (silent assignment to undeclared variables, duplicate parameter names, etc.), which is valuable while learning. ES modules are strict by default, so omit the directive there — it would be redundant.
- Use `const` by default, `let` only when a variable is genuinely reassigned; avoid `var`.
- Prefer `async`/`await` over raw `.then()` chains for asynchronous code — it reads closer to synchronous logic, which is easier to follow when learning.
- **Comment generously**, per the repo-wide convention: explain *why* a step is needed (e.g. why a particular event is awaited, why a library was chosen over a built-in browser/Node API), not just what the line does.
- Use JSDoc-style comments on non-trivial functions summarizing purpose, parameters, and return value.
- Prefer explicit, readable control flow over dense chained methods when it makes the logic easier to follow (e.g. a named intermediate variable over a long `.map().filter().reduce()` chain).
- Handle errors where the stage material expects it (e.g. a `fetch` call should handle a failed response) — don't add speculative error handling for cases the stage doesn't cover.

## Formatting & linting

- Format with [Prettier](https://prettier.io/) and lint with [ESLint](https://eslint.org/) once a stage's `package.json` exists — add both as dev dependencies the first time a stage needs them rather than pre-installing speculatively.

## Testing

- Use [Jest](https://jestjs.io/) (or `node --test` for very small stages that don't want an extra dependency). Put tests in a `tests/` folder inside the stage, named `<topic>.test.js`.
- Not every stage needs exhaustive tests — this is a learning lab, so tests are most valuable where they help verify understanding of the stage's core mechanic, not as blanket coverage.
- **`node --test`** is Node's own built-in test runner (stable since Node 18), and the default choice for a zero-dependency stage on Node 18+: no `package.json` dependency to add, `import { test } from "node:test"` plus `node:assert/strict`, and `"scripts": { "test": "node --test tests/" }` runs every `tests/*.test.js` file. `dataviz-python-js/d3-interactive-web/` hand-rolled its own tiny test runner instead only because the machine's Node at the time (v14) predated `node --test` — that workaround is no longer needed on a current Node install (verified on Node v20.18.1 in `demos/psa-terminal-map/`); don't copy the hand-rolled-runner pattern into a new stage without first checking whether `node --test` is simply available now.

## Vendoring a third-party data file

Occasionally a stage needs a static data file from an external package that has no CDN-importable
JS API of its own — e.g. a TopoJSON/GeoJSON basemap. Rather than fetching it from a CDN at page
load (adding a runtime dependency on that CDN staying up, and breaking offline use), download it
once and commit it into the stage's own `data/` folder ("vendoring"). Rules for this:

- Only for a file that is genuinely third-party and public domain or permissively licensed (e.g.
  Natural Earth-derived world topology, public domain) — never vendor something under a license
  that forbids redistribution.
- Attribute it in the stage's `README.md`: where it came from (the exact package/URL), its
  license, and the date it was fetched, so it can be re-fetched or updated later without
  re-deriving where it originally came from.
- Keep it as small as practical for the stage's purpose (e.g. a 110m-resolution world topology
  rather than a 10m one, when only a small illustrative map is needed) — see
  `demos/psa-terminal-map/data/world-110m.json` (vendored from `world-atlas`'s 110m land
  topology) for a worked example.
- The file is committed, not gitignored — unlike this repo's usual "generated output is
  gitignored and reproducible by re-running a script" convention, a vendored file isn't
  reproducible from anything else already in the repo, so it has to be committed to make the
  stage self-contained.

## Running stage code

- Each stage's `README.md` should document how to run its code (e.g. `node index.js` or `npm start`) — keep that instruction accurate as the stage evolves.
