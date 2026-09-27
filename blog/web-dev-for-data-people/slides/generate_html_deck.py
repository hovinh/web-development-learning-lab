"""Generate the "Web Dev for Data People" talk deck as a browser-based deck.

Usage (from the repo root, with .venv active):

    python blog/web-dev-for-data-people/slides/generate_html_deck.py

Reads the exact same content.py the .pptx is built from, renders it with
theme_html.py, and writes html/index.html. Built on reveal.js (CDN, no npm
install) - arrow keys or click to advance, "S" for speaker notes/timing,
"F" for fullscreen, "Esc" for the slide overview.

This is the deliberate second output from one source of content: the talk's
own argument is that a web page beats a screenshot for making a point to an
audience, so the deck about that argument is also presentable as a web page,
not only as a file you hand someone.
"""

from __future__ import annotations

from pathlib import Path

import theme
import theme_html
from content import SECTIONS, total_minutes, total_slides

SLIDES_DIR = Path(__file__).resolve().parent
ASSETS_DIR = SLIDES_DIR / "assets" / "screenshots"
HTML_DIR = SLIDES_DIR / "html"
OUTPUT_PATH = HTML_DIR / "index.html"

REVEAL_VERSION = "5.1.0"
REVEAL_CDN = f"https://cdn.jsdelivr.net/npm/reveal.js@{REVEAL_VERSION}"

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Web Dev for Data People</title>
<link rel="stylesheet" href="{reveal_cdn}/dist/reveal.css">
<link rel="stylesheet" href="{reveal_cdn}/dist/theme/simple.css">
<style>{css}</style>
</head>
<body>
<div class="reveal">
  <div class="slides">
{slides}
  </div>
</div>
<script src="{reveal_cdn}/dist/reveal.js"></script>
<script src="{reveal_cdn}/plugin/notes/notes.js"></script>
<script>
  Reveal.initialize({{
    width: 1280,
    height: 720,
    margin: 0.03,
    center: false,
    hash: true,
    controls: true,
    progress: true,
    slideNumber: 'c/t',
    transition: 'fade',
    plugins: [ RevealNotes ]
  }});
</script>
</body>
</html>
"""

TITLE_FOOTNOTE = "Presented as a web page, not a screenshot - see why in the next few minutes."


def build() -> None:
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    slide_html = []
    first_title_seen = False

    for section_index, section in enumerate(SECTIONS):
        accent = theme.accent_for_section(section_index)
        for slide_data in section.slides:
            renderer = theme_html.RENDERERS[slide_data.kind]
            if slide_data.kind == "title" and not first_title_seen:
                slide_html.append(renderer(slide_data, accent, ASSETS_DIR, footnote=TITLE_FOOTNOTE))
                first_title_seen = True
            else:
                slide_html.append(renderer(slide_data, accent, ASSETS_DIR))

    page = PAGE_TEMPLATE.format(
        reveal_cdn=REVEAL_CDN,
        css=theme_html.CSS,
        slides="\n".join(slide_html),
    )
    OUTPUT_PATH.write_text(page, encoding="utf-8")


def report() -> None:
    print(f"Generated {OUTPUT_PATH}")
    print(f"{total_slides()} slides, {total_minutes():g} min planned (same content.py as the .pptx)")
    print("Open directly (double-click / file://) or serve via: npm run serve -- blog/web-dev-for-data-people/slides/html")


if __name__ == "__main__":
    build()
    report()
