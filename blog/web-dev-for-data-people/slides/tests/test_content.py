"""Sanity checks on content.py - the file most likely to be hand-edited.

Not a check on the generated .pptx itself (python-pptx's own object model is
trustworthy); these guard the two things that are easy to break while
fine-tuning content.py: a typo'd image path, and a timing budget that's
drifted far from the talk's 90-minute slot. Also guards against the .pptx
and the HTML deck's *chrome* drifting apart again (they drifted once,
silently, until asked about it directly) - see
`test_html_tab_labels_match_pptx_tab_labels` below.
"""

import re
from pathlib import Path

import theme
from content import SECTIONS, total_minutes

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "screenshots"
TARGET_MINUTES = 90
ALLOWED_DRIFT_MINUTES = 10


def _referenced_image_paths():
    for section in SECTIONS:
        for slide in section.slides:
            for path_str in (slide.image, slide.image_left, slide.image_right):
                if path_str:
                    yield path_str


def test_every_referenced_screenshot_exists():
    missing = [p for p in _referenced_image_paths() if not (ASSETS_DIR / p).exists()]
    assert not missing, f"content.py references screenshots that don't exist yet: {missing}"


def test_total_minutes_within_budget():
    minutes = total_minutes()
    assert abs(minutes - TARGET_MINUTES) <= ALLOWED_DRIFT_MINUTES, (
        f"planned talk time is {minutes} min, more than {ALLOWED_DRIFT_MINUTES} min off "
        f"the {TARGET_MINUTES}-minute target - rebalance content.py's slide `minutes` values"
    )


def test_every_slide_kind_is_a_known_builder():
    # theme.py owns the builder registry; importing it here (rather than
    # hardcoding the kind list) keeps this test honest if a kind is renamed.
    import theme

    unknown = sorted({s.kind for sec in SECTIONS for s in sec.slides} - set(theme.BUILDERS))
    assert not unknown, f"content.py uses slide kind(s) theme.py has no builder for: {unknown}"


def test_every_slide_kind_is_a_known_html_renderer():
    # Same idea, for the web deck's renderer registry - the two themes must
    # stay in lockstep since both are built from the same content.py.
    import theme_html

    unknown = sorted({s.kind for sec in SECTIONS for s in sec.slides} - set(theme_html.RENDERERS))
    assert not unknown, f"content.py uses slide kind(s) theme_html.py has no renderer for: {unknown}"


def test_html_deck_generates_one_section_per_slide():
    # A light smoke test on generate_html_deck.py: it should run cleanly and
    # produce exactly one <section> per planned slide, with no unresolved
    # placeholders (every screenshot already exists, per the test above).
    import generate_html_deck

    generate_html_deck.build()
    html = generate_html_deck.OUTPUT_PATH.read_text(encoding="utf-8")
    assert html.count("<section") == generate_html_deck.total_slides()
    assert "screenshot pending" not in html


def test_html_tab_labels_match_pptx_tab_labels():
    # Both decks' tab bars must show the exact same "filename" per slide.
    # theme_html.py is supposed to call theme.tab_label_for() rather than
    # deriving its own label - this test is what actually enforces that,
    # not just the comment saying so. "quote" slides render no tab bar in
    # either deck, so they're skipped rather than expected to match "".
    import generate_html_deck

    generate_html_deck.build()
    html = generate_html_deck.OUTPUT_PATH.read_text(encoding="utf-8")
    rendered_labels = re.findall(r'<span class="tab-label">([^<]*)</span>', html)

    expected_labels = []
    for section in SECTIONS:
        for slide in section.slides:
            if slide.kind == "quote":
                continue
            if slide.kind == "title":
                expected_labels.append("talk.md")
            else:
                expected_labels.append(theme.tab_label_for(slide))

    assert rendered_labels == expected_labels, (
        "the HTML deck's tab-bar labels no longer match theme.tab_label_for() - "
        "the two decks' chrome has drifted apart again"
    )
