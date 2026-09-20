# javascript-and-jquery

Notes for working through *JavaScript & jQuery: Interactive Front-End Web
Development* (Jon Duckett, 2014).

Follows this repo's default convention: one subfolder per stage/chapter,
each self-contained. See the root [README.md](../README.md) for the
full list of stages across all books.

Stages so far: none yet — this folder holds the book's concept notes
below; stage subfolders (each with its own `README.md`) get added as the
book's exercises and projects are built.

> These notes are written from general knowledge of the book, not copied
> from it. The chapter list was checked against online listings of the
> table of contents. Code samples are general JavaScript/jQuery, so names
> and project details will differ from the book.

## Companion resources

- [javascriptbook.com](https://javascriptbook.com/) is the book's
  official site. Its downloadable code
  ([/code/](https://javascriptbook.com/code/)) is organised by chapter
  folder (`c01`, `c02`, ..., e.g. `c05/get-element-by-id.html`), and the
  filenames match the ones printed beside each snippet in the book. Handy to
  compare against your own stage code.

## About the book

The sequel to *HTML & CSS* (see [`html-and-css/`](../html-and-css/README.md))
and written in the same style: **one topic per two-page spread**, diagram
on one side and code on the other. It assumes you can already write HTML
and CSS, and teaches programming from scratch. It needs no build tools:
you write `.js` files, link them from an HTML page and open it in a
browser.

The book's approach, which the notes here follow:

- **Programming concepts first, syntax second.** It starts with how
  scripts think (tasks, steps, variables, decisions) before any language
  detail.
- **JavaScript before jQuery.** You learn the raw DOM and events, then see
  how jQuery wraps the same ideas in shorter code. So you understand what
  the library is doing for you.
- **Worked examples at the end.** The last chapters (content panels,
  filtering/sorting, form validation) combine everything into the kinds of
  widgets real sites use.

## Scope

The book has an introduction and **13 chapters**, in this order:

**Part 1: Language fundamentals**

1. The ABC of programming: what a script is, how to break a task into steps, flowcharts, how browsers run JS
2. Basic JavaScript instructions: statements, variables, data types, expressions, operators, arrays
3. Functions, methods and objects: declaring and calling functions, scope, object literals, built-in objects (`Math`, `Date`, `Number`, `String`), the browser's `window` and `document` objects
4. Decisions and loops: comparisons, `if`/`else`, `switch`, logical operators, `for`/`while`/`do while`

**Part 2: Working with the page**

5. Document Object Model (DOM): the tree of nodes, selecting elements, reading and changing content, attributes, creating and removing nodes, cookies and local storage
6. Events: event types, event handlers vs. listeners, the event object, delegation, keyboard and mouse events, page-load events
7. jQuery: selecting and changing elements, effects and animation, event handling, traversing, sizes/positions, plugins

**Part 3: Talking to the outside world**

8. Ajax and JSON: loading data without a page refresh, JSON syntax, working with the response
9. APIs: what an API is, the HTML5 APIs (geolocation, history, canvas, etc.), and third-party APIs
10. Error handling and debugging: reading error messages, browser DevTools, `try`/`catch`, common mistakes

**Part 4: Putting it together**

11. Content panels: accordions, tabs, modal windows, galleries, sliders
12. Filtering, searching and sorting: showing/hiding items by criteria, live search, sortable tables
13. Form enhancement and validation: hooking into form events, checking input, showing helpful errors

Sections in these notes marked **(beyond the book)** are extra background
for later, not part of that list.

## Core ideas to remember

### JavaScript

- A script is a **series of instructions** run top to bottom. Break a task
  into small steps before writing code; the book uses flowcharts for that.
- **Variables** hold values (`let`, `const`). **Data types** are strings,
  numbers, booleans, arrays, objects, `null`/`undefined`.
- **Functions** package reusable steps. An **object** groups related data
  (properties) and functions (methods). Methods like `document.querySelector`
  are just functions attached to an object.
- **Truthiness and comparisons:** `===` compares value *and* type, and is
  almost always what you want over `==`.
- **(beyond the book)** The book predates ES6 (2015), so it uses `var`,
  function expressions and string concatenation. Modern code uses `let`/
  `const`, arrow functions, template literals, `fetch` and `async`/`await`.
  When you see old-style code in the book, use the modern equivalent in your
  stage code and note the difference in comments.

### The DOM and events

- The browser turns HTML into a **DOM tree**, and JavaScript reads and
  changes that tree. Changing the tree changes what's on screen.
- Typical flow: **select** an element, then **change** it (text, attribute,
  class, style), in response to an **event**.
- **Events** are things that happen (click, submit, keypress, load). You
  attach a **handler** function to react. **Delegation** puts one listener
  on a parent instead of many on children.
- Scripts that touch the DOM must run *after* the elements exist: put the
  `<script>` at the end of `<body>`, or use `defer` / `DOMContentLoaded`.

### jQuery

- [jQuery](https://jquery.com/) is a library that makes selecting elements
  and handling events shorter and smooths over old-browser differences.
  Everything starts with `$("selector")` and chains methods:
  `$("p").addClass("note").fadeIn();`.
- **(beyond the book)** jQuery's original job (browser inconsistencies) is
  largely gone: modern browsers do the same things natively with
  `querySelector`, `classList`, `fetch` and CSS transitions. You'll still
  meet jQuery in older codebases and plugins, so it's worth knowing how to
  read it, but it's rarely the right pick for a new project. Learn it here
  as a reading skill.

### Ajax, APIs and debugging

- **Ajax** loads data in the background and updates part of the page, with
  no full reload. **JSON** is the text format that data usually arrives in.
- Ajax needs a real **HTTP server**: `fetch`/XHR generally won't work from
  a `file://` page. Use the repo's `http-server` (see Tooling).
- **Debug** with the browser DevTools: the Console for errors and
  `console.log`, the Sources panel for breakpoints, the Network panel for
  Ajax calls.

## Tooling

No build step. Preview a stage's static files with the repo's shared
`http-server` (see the root [README.md](../README.md)):

```
npm install
npm run serve -- javascript-and-jquery/<stage-folder>
```

Opening the `.html` file directly works for early chapters, but use the
server from the Ajax chapter onward. jQuery can be loaded from a CDN
`<script>` tag, so no `package.json` is needed unless a stage adds tooling.
Follow [docs/javascript.md](../docs/javascript.md) for JS style, linting
and testing conventions.

## Conventions for stages here

- One stage folder per chapter or small project, each with an
  `index.html`, a `js/` folder, and `css/`/`images/`/data folders as
  needed, plus its own `README.md`.
- Heavy comments in the JS explaining *why* each step exists, as elsewhere
  in this repo (see [CLAUDE.md](../CLAUDE.md)).
- Keep JavaScript in external files, not inline `<script>` blocks or
  `onclick` attributes, keeping behaviour separate from structure and
  presentation like the book advises.
- For the jQuery chapters, prefer a plain-JavaScript equivalent alongside
  where it helps show what jQuery is doing.
