"""Generate the "Web Dev for Data People" talk deck as a .pptx.

Usage (from the repo root, with .venv active):

    python blog/web-dev-for-data-people/slides/generate_deck.py

Reads the slide content from content.py, renders it with theme.py's builders,
and writes web-dev-for-data-people-slides.pptx next to this script. To
fine-tune the deck, edit content.py (what it says) or theme.py (how it
looks), then rerun this script - there's nothing to hand-edit in PowerPoint.
"""

from __future__ import annotations

from pathlib import Path

import theme
from content import SECTIONS, total_minutes, total_slides

SLIDES_DIR = Path(__file__).resolve().parent
ASSETS_DIR = SLIDES_DIR / "assets" / "screenshots"
OUTPUT_PATH = SLIDES_DIR / "web-dev-for-data-people-slides.pptx"

TARGET_MINUTES = 90


def build() -> None:
    prs = theme.new_presentation()

    for section_index, section in enumerate(SECTIONS):
        accent = theme.accent_for_section(section_index)
        for slide_data in section.slides:
            builder = theme.BUILDERS[slide_data.kind]
            slide_accent = accent
            slide = builder(prs, slide_data, slide_accent, ASSETS_DIR)
            theme.add_notes(slide, slide_data.notes, slide_data.minutes)

    prs.save(OUTPUT_PATH)


def report() -> None:
    minutes = total_minutes()
    slides = total_slides()
    print(f"Generated {OUTPUT_PATH}")
    print(f"{slides} slides, {minutes:g} min planned (target {TARGET_MINUTES} min)")
    delta = minutes - TARGET_MINUTES
    if abs(delta) > 10:
        print(f"WARNING: {delta:+g} min off target - check content.py's minute budgets")

    missing = []
    for section in SECTIONS:
        for slide_data in section.slides:
            for field_name in ("image", "image_left", "image_right"):
                path_str = getattr(slide_data, field_name, None)
                if path_str and not (ASSETS_DIR / path_str).exists():
                    missing.append(path_str)
    if missing:
        print(f"NOTE: {len(missing)} referenced screenshot(s) not yet captured (rendered as placeholders):")
        for path_str in sorted(set(missing)):
            print(f"  - {path_str}")


if __name__ == "__main__":
    build()
    report()
