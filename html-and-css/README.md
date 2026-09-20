# html-and-css

Notes for working through *HTML & CSS: Design and Build Websites* (Jon
Duckett, 2011).

Follows this repo's default convention: one subfolder per stage/chapter,
each self-contained. See the root [README.md](../README.md) for the
full list of stages across all books.

Stages so far: none yet — this folder holds the book's concept notes
below; stage subfolders (each with its own `README.md`) get added as the
book's exercises and projects are built.

> These notes are written from general knowledge of the book, not copied
> from it. The chapter list was checked against online listings of the
> table of contents. Code samples are general HTML/CSS, so names and
> project details will differ from the book.

## Companion resources

- [htmlandcssbook.com](https://www.htmlandcssbook.com/) is the book's
  official site. It has the downloadable code for every example
  ([/code/](https://www.htmlandcssbook.com/code/)) and online samples you
  can try in the browser ([/code-samples/](https://www.htmlandcssbook.com/code-samples/)).
  Handy to compare against your own stage code.
- Duckett's follow-up book, *JavaScript & jQuery*, continues from where
  this one stops and shares its two-page-spread style.

## About the book

A visual, beginner-friendly introduction to writing web pages. It has no
prerequisites and no build tools: you write `.html` and `.css` files in
a text editor and open them in a browser. Its distinctive style is
**one topic per two-page spread** with a diagram on the left and a
code sample on the right, so it works well as a reference to dip into.

It's split into two halves that mirror how the web works:

- **HTML** is the *content and structure*: what each piece of the page
  *is* (a heading, a paragraph, a list, a link).
- **CSS** is the *presentation*: how those pieces look (color, fonts,
  spacing, position).

Keeping the two separate is the book's central idea. The HTML says what
something means; the CSS says how it looks; you can restyle a whole site
without touching its markup.

## Scope

The book runs roughly in this order, and so will these notes and stages:

**Part 1: HTML**

1. Structure: elements, tags, attributes, headings, paragraphs, bold/italic, line breaks
2. Text: semantic markup for quotes, abbreviations, citations, subscript/superscript, etc.
3. Lists: ordered, unordered, definition lists, nesting
4. Links: to other sites, other pages, page sections, email addresses
5. Images: `<img>`, sizing, alt text, formats (JPEG/GIF/PNG), image prep
6. Tables: rows, cells, headers, spanning, accessibility
7. Forms: inputs, text boxes, radio buttons, checkboxes, drop-downs, submit buttons
8. Extra markup: doctype, comments, `id`/`class`, block vs inline, `<iframe>`, `<meta>`, escape characters
9. Flash, video and audio: embedding media (dated by today's standards; modern pages use HTML5 `<video>`/`<audio>`)

**Part 2: CSS**

10. Introducing CSS: rules, selectors, properties, linking a stylesheet
11. Color: color names, hex, RGB, HSL, opacity, contrast
12. Text: typefaces, sizes, weights, spacing, alignment, `@font-face`
13. Boxes: the box model (width, height, border, margin, padding), block vs inline
14. Lists, tables and forms: styling those elements, pseudo-classes such as `:hover`
15. Layout: positioning schemes, floats, fixed-width vs. fluid layouts, media
16. Images: aligning, backgrounds, `background-*` properties
17. HTML5 layout: semantic elements (`<header>`, `<nav>`, `<article>`, `<section>`, `<aside>`, `<footer>`)

**Part 3: Design and practicalities**

18. Process and design: planning a site, wireframes, site maps, visual hierarchy, grids
19. Practical information: getting a domain name, hosting, promoting a site, analytics

The book has **19 chapters** plus an introduction and index (about 490
pages). It does **not** cover JavaScript; that's the sequel, Duckett's
separate *JavaScript & jQuery: Interactive Front-End Web Development*.
For JS in this repo see [docs/javascript.md](../docs/javascript.md).

Sections in these notes marked **(beyond the book)** are extra background
for later, not part of that list.

## Core ideas to remember

### HTML

- A page is a tree of **elements**. An element is an opening tag, content
  and a closing tag: `<p>Hello</p>`. Some (`<img>`, `<br>`) are empty and
  have no closing tag.
- **Attributes** go on the opening tag and add information:
  `<a href="page.html">link</a>`.
- Choose elements for their *meaning*, not their look: `<h1>`–`<h6>` for
  headings, `<em>`/`<strong>` for emphasis. If you only want it to *look*
  bold, that's CSS's job.
- Every page starts with `<!DOCTYPE html>` and has `<html>`, `<head>`
  (title, meta, stylesheet links) and `<body>` (what's visible).
- Every `<img>` needs an `alt` attribute (accessibility and fallback).
- **Block** elements start a new line and fill the width (`<p>`, `<h1>`,
  `<div>`); **inline** elements flow inside a line (`<a>`, `<em>`,
  `<span>`).

### CSS

- A **rule** is `selector { property: value; }`. Selectors can target an
  element (`p`), a class (`.note`), an id (`#top`), or a relationship
  (`nav a`).
- **Cascade and specificity:** when rules conflict, the more specific
  selector wins; when equal, the later one wins. Some properties are
  **inherited** from parent to child (such as `color` and `font-family`).
- **The box model:** every element is a box made of content, padding,
  border and margin (inside to outside). Sizing surprises are usually
  box-model surprises. (**beyond the book**: `box-sizing: border-box` makes
  `width` include padding and border, which most modern CSS resets set.)
- Layout in the book is done with `float` and positioning. **(beyond the
  book)** Modern layouts use **Flexbox** and **CSS Grid** instead, and
  responsive design uses media queries. The book's floats are still worth
  understanding for reading older code.

## Tooling

No build step. Preview a stage's static files with the repo's shared
`http-server` (see the root [README.md](../README.md)):

```
npm install
npm run serve -- html-and-css/<stage-folder>
```

or just open the `.html` file directly in a browser. Use the browser's
DevTools (Elements/Styles panel) to inspect and experiment with the
box model and computed styles, since it's the best way to learn CSS.

## Conventions for stages here

- One stage folder per chapter or small project, each with an
  `index.html`, a `css/` folder and an `images/` folder as needed, plus its
  own `README.md`.
- Heavy comments in both HTML and CSS explaining *why* an element or rule
  is used, as elsewhere in this repo (see [CLAUDE.md](../CLAUDE.md)).
- Prefer semantic HTML and keep all styling in external stylesheets, not
  inline `style` attributes, in keeping with the book's separation of
  structure and presentation.
