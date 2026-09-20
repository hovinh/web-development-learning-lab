# Tailwind CSS

**Status: written from documentation and general knowledge; not run in the user's repo.**

## What it is for

A styling approach: instead of writing CSS files you compose small utility classes in
the HTML (`class="px-4 py-2 rounded bg-blue-600 text-white"`). It is only styling, so it
works with static HTML, Django templates, React or Angular. It does not give you
finished components; pair it with a kit (daisyUI, Flowbite, shadcn/ui). See
`../ui-kits.md`.

## Getting it without Node

Tailwind scans your files for class names and generates a CSS file containing only what
you used. That compile step has two Node-free routes:

1. **Standalone CLI:** a single executable from the Tailwind GitHub releases (or
   `pip install pytailwindcss`, which fetches it).
2. **Browser build via CDN** (prototype only, needs internet):
   `<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>`

Tailwind v4 style (v3 used a `tailwind.config.js` and different directives):

```css
/* input.css */
@import "tailwindcss";
```

```bash
# Compile once, or watch while you edit
tailwindcss -i input.css -o static/output.css --watch
```

Then link `static/output.css` from your HTML or Django base template.

## Gotchas

- Do not build class names dynamically (`"bg-" + color`); the scanner only sees whole
  literal strings, so those styles would never be generated.
- daisyUI 5 targets Tailwind 4 and is enabled in CSS with `@plugin "daisyui";`. Using it
  with the standalone CLI (no npm) was not verified; check its docs or use its CDN build.
- Version mismatch is the usual failure: v3 tutorials do not work on v4 and vice versa.
