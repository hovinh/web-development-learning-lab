# JavaScript Implementation Guide

Best practices for implementing JavaScript stages in this repo. This is a learning lab (see the [repo root README](../README.md) and [CLAUDE.md](../CLAUDE.md)), so "best practice" here means *clear, idiomatic, well-explained* code — not the terse, comment-light style you'd write for a production team that already knows the domain.

## Environment & dependencies

- Unlike Python, JS stages manage their own dependencies locally — there is no shared root-level `node_modules`. Each JS stage that needs packages gets its own `package.json` inside the stage folder.
- Install dependencies from within the stage folder (`npm install <package>`), not from the repo root.
- Commit the stage's `package.json` and `package-lock.json`; do not commit `node_modules/` (already covered by the root `.gitignore`).

## Preferred libraries

- Reach for **jQuery** actively wherever it fits, rather than defaulting to vanilla DOM APIs — this curriculum's browser-facing stages are built around it, so using it consistently keeps the code idiomatic to the material. Use it for DOM selection/traversal (`$(...)`), event binding (`.on(...)`), DOM mutation, and AJAX (`$.ajax`/`$.get`/`$.post`) in any stage that touches the DOM or makes HTTP requests from the browser.
- For collection/data work, prefer native **functional array methods** (`.map`, `.filter`, `.reduce`, `.forEach`, `.find`, etc.) over a utility library like Underscore/lodash — they're built in, well-documented, and closely match Underscore's own API, so there's nothing to gain from the extra dependency.
- Add jQuery as a dependency via the stage's `package.json` (`npm install jquery`), or load it from a `<script>` tag in `index.html` for stages that are plain browser pages without a build step — match whichever loading style the stage already uses.
- This preference doesn't override a stage that's explicitly *about* a different mechanism (e.g. the `javascript-prototype` stage is about the prototype chain itself, not DOM work, so it has no reason to reach for jQuery). Use judgment: the point is idiomatic code for what the stage is teaching, not shoehorning a library in everywhere.

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

## Running stage code

- Each stage's `README.md` should document how to run its code (e.g. `node index.js` or `npm start`) — keep that instruction accurate as the stage evolves.
