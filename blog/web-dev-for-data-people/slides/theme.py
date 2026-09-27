"""Visual theme and slide-layout builders for the "Web Dev for Data People" deck.

Keeping every visual decision (colors, fonts, spacing, how a "bullets slide" or
a "comparison slide" is drawn) in this one module is what makes content.py
easy to fine-tune: content.py only ever says *what* a slide contains, never
*how* it's drawn. To restyle the whole deck, edit here; to change what a
slide says, edit content.py.

Design language: "editor tabs" - every slide is framed like a code editor.
A dark tab bar runs across the top with the classic red/yellow/green
window-control dots and a monospace "filename" naming what the slide holds
(e.g. `compare.py`, `functions.json`), auto-derived from the slide's title
and kind by `tab_label_for()` - content.py never has to name it. Below the
bar, a thin accent gutter (like an editor's line-number rail) runs down the
left edge. The title slide and the closing "quote" slide go further and use
the tab-bar/terminal motif full-slide (a typed `$ command`, a block comment)
since they're meant to be a moment, not a document. No icon badges anywhere -
the tab-bar/terminal chrome itself is the personality, so a floating emoji
badge would be redundant decoration on top of it.

This replaced an earlier "white canvas, thin accent rule" consulting-deck
look after a round of side-by-side style samples - the editor/terminal chrome
tests better for a room of engineers than a plain rule ever could, and reads
as *of* the material (a coding talk) rather than decoration on top of it.

The color palette is not invented for this deck - it's the same validated
categorical palette `demos/psa-terminal-map/css/style.css` uses for its D3
charts (itself checked against the `dataviz` skill's accessibility rules).
Reusing it here means the deck and the demo it screenshots look like one
visual system, not two. `_shade()` darkens it slightly for on-slide use
(titles, rules, table headers), which reads calmer than the raw, brighter
chart colors. The macOS-style traffic-light dot colors (`MAC_RED` etc.) are
a separate, deliberate exception - they're decorative chrome referencing a
real OS window, not part of the chart palette, so they stay the universally
recognized hex values rather than being run through `_shade()`.
"""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

# ---------------------------------------------------------------------------
# Palette - copied from demos/psa-terminal-map/css/style.css's light-mode
# custom properties (`--series-1` .. `--series-6`, `--text-primary`, etc.).
# Kept as plain hex strings here; converted to RGBColor by hex_to_rgb() below.
# ---------------------------------------------------------------------------

SURFACE = "#ffffff"
PANEL = "#f7f7f5"  # subtle panel/alt-row tint, not a full background color
TEXT_PRIMARY = "#1a1a1a"
TEXT_SECONDARY = "#54524c"
TEXT_MUTED = "#8b887f"
GRIDLINE = "#e3e1d9"

# Dark side of the theme - the tab bar, and the title/quote "moment" slides
# that go full-terminal. Not from the chart palette (that's the SERIES
# below); these are just a dark UI surface and its text colors.
DARK_BG = "#12141c"
DARK_PANEL = "#1c1f2b"
DARK_TEXT = "#f2f2f0"
DARK_TEXT_SECONDARY = "#b7b9c4"
DARK_GRIDLINE = "#33374a"

# macOS-style traffic-light window-control dots - see module docstring for
# why these stay their real-world hex values instead of going through
# _shade() with the rest of the palette. Public (no leading underscore):
# theme_html.py reuses these exact values for its own tab-bar dots, so the
# two decks' chrome can't drift apart the way the rest of the look once did.
MAC_RED = "#ff5f56"
MAC_YELLOW = "#febc2e"
MAC_GREEN = "#28c840"

# A flat neutral used only for the "static/notebook" side of the
# concept_pair illustration - deliberately duller than any chart color, to
# read as "not live" next to the accent-colored bars on the "web app" side.
# Public for the same reason as the MAC_* colors above.
MUTED_BAR = "#c9c7bb"

# The six-color categorical series, straight from the demo's own CSS.
SERIES = [
    "#2a78d6",  # blue
    "#008300",  # green
    "#e87ba4",  # magenta
    "#eda100",  # yellow
    "#1baf7a",  # aqua
    "#eb6834",  # orange
]

FONT_TITLE = "Segoe UI Semibold"
FONT_BODY = "Segoe UI"
FONT_MONO = "Consolas"

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

MARGIN = Inches(0.6)
# Text content sits 0.2in further in than MARGIN so it lines up under the
# chrome's title, which is itself indented past the accent gutter.
CONTENT_LEFT = MARGIN + Inches(0.2)
TAB_BAR_H = Inches(0.5)


def hex_to_rgb(value: str) -> RGBColor:
    value = value.lstrip("#")
    return RGBColor(int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def _shade(value: str, factor: float = 0.82) -> str:
    """Darken a hex color toward black by `factor` (1.0 = unchanged).

    Used everywhere an accent color sits behind white text (table headers)
    or carries body text (rules, badges) - the raw chart colors read a shade
    too bright/candy-like at slide scale; this keeps the same hue, calmer.
    """
    value = value.lstrip("#")
    r, g, b = (int(value[i : i + 2], 16) for i in (0, 2, 4))
    return "#{:02x}{:02x}{:02x}".format(
        int(r * factor), int(g * factor), int(b * factor)
    )


def accent_for_section(index: int) -> str:
    """Cycle the six-color series so section N always gets the same accent."""
    return _shade(SERIES[index % len(SERIES)])


# ---------------------------------------------------------------------------
# Presentation scaffolding
# ---------------------------------------------------------------------------


def new_presentation() -> Presentation:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def _blank_slide(prs: Presentation, bg_hex: str = SURFACE):
    # Layout 6 is the built-in "Blank" layout in python-pptx's default
    # template - no placeholders to fight with, full manual control over
    # every shape.
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = hex_to_rgb(bg_hex)
    return slide


def _add_rect(slide, left, top, width, height, fill_hex, *, rounded=False, line_hex=None):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(fill_hex)
    if line_hex:
        shape.line.color.rgb = hex_to_rgb(line_hex)
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def _add_dot(slide, left, top, size, fill_hex):
    """A plain filled circle, no text - the tab bar's traffic-light dots."""
    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, size, size)
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(fill_hex)
    shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def _set_run(run, text, *, size=18, bold=False, color=TEXT_PRIMARY, font=FONT_BODY, italic=False):
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = font
    run.font.color.rgb = hex_to_rgb(color)
    return run


def add_notes(slide, notes: str, minutes: float | None = None) -> None:
    text = notes or ""
    if minutes:
        text = f"[~{minutes:g} min]\n{text}" if text else f"[~{minutes:g} min]"
    if text:
        slide.notes_slide.notes_text_frame.text = text


# ---------------------------------------------------------------------------
# Tab-bar chrome
# ---------------------------------------------------------------------------

# kind -> the fake file extension its tab label gets. Cosmetic only, but
# chosen to match what that slide *is* (a table reads as data, a comparison
# reads as a diff, everything else reads as notes).
_TAB_EXTENSIONS = {
    "bullets": "md",
    "image": "png",
    "image_pair": "png",
    "image_bullets": "md",
    "table": "json",
    "comparison": "py",
    "ladder": "md",
    "quote": "md",
}


def _slugify(text: str, max_words: int = 3) -> str:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())[:max_words]
    return "-".join(words) or "slide"


def tab_label_for(s) -> str:
    """Auto-derive the tab bar's "filename" from a slide's kind and title.

    Keeps content.py free of a presentation-only field - the same reason
    theme.py owns color and layout instead of content.py.
    """
    ext = _TAB_EXTENSIONS.get(s.kind, "md")
    return f"{_slugify(s.title)}.{ext}"


def _tab_bar(slide, tab_label: str, bar_h=TAB_BAR_H):
    _add_rect(slide, 0, 0, SLIDE_W, bar_h, DARK_PANEL)
    dot_size = Inches(0.14)
    dot_top = (bar_h - dot_size) / 2
    for i, color in enumerate((MAC_RED, MAC_YELLOW, MAC_GREEN)):
        _add_dot(slide, MARGIN + i * Inches(0.24), dot_top, dot_size, color)
    label_left = MARGIN + Inches(0.95)
    label_box = slide.shapes.add_textbox(label_left, 0, SLIDE_W - label_left - MARGIN, bar_h)
    tf = label_box.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    _set_run(p.add_run(), tab_label, size=12.5, color=DARK_TEXT_SECONDARY, font=FONT_MONO)
    return bar_h


def _chrome(slide, accent_hex, title, tab_label):
    """Shared header for every non-title/quote slide: the tab bar, an accent
    gutter down the left edge below it, then the slide's title in the
    accent color. Returns the y-coordinate where body content should start.
    """
    bar_h = _tab_bar(slide, tab_label)
    _add_rect(slide, 0, bar_h, Inches(0.1), SLIDE_H - bar_h, accent_hex)

    title_box = slide.shapes.add_textbox(
        CONTENT_LEFT, bar_h + Inches(0.22), SLIDE_W - CONTENT_LEFT - MARGIN, Inches(0.8)
    )
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    _set_run(p.add_run(), title, size=25, bold=True, color=accent_hex, font=FONT_TITLE)

    return bar_h + Inches(1.0)


def _fit_picture(slide, image_path: Path, left, top, max_w, max_h):
    """Add a picture scaled to fit inside a box, centered, aspect preserved."""
    with Image.open(image_path) as im:
        img_w, img_h = im.size
    scale = min(max_w / img_w, max_h / img_h)
    w = Emu(int(img_w * scale))
    h = Emu(int(img_h * scale))
    x = Emu(int(left + (max_w - w) / 2))
    y = Emu(int(top + (max_h - h) / 2))
    pic = slide.shapes.add_picture(str(image_path), x, y, width=w, height=h)
    pic.line.color.rgb = hex_to_rgb(GRIDLINE)
    pic.line.width = Pt(0.75)
    return pic


def _placeholder_box(slide, left, top, width, height, label):
    box = _add_rect(slide, left, top, width, height, PANEL, rounded=True, line_hex=GRIDLINE)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    _set_run(p.add_run(), f"screenshot pending:\n{label}", size=12, italic=True, color=TEXT_MUTED)


def _bulleted_paragraph(tf, text, *, accent_hex, size, first):
    """One bullet: a monospace accent "prompt" marker, then body text."""
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.space_after = Pt(14)
    _set_run(p.add_run(), "›  ", size=size, bold=True, color=accent_hex, font=FONT_MONO)
    _set_run(p.add_run(), text, size=size, color=TEXT_PRIMARY)
    return p


def _add_footer(slide, text, accent_hex, top):
    """A one-line conclusion under a table/comparison - a bold accent-colored
    callout, not another table row, so it reads as the takeaway.
    """
    box = slide.shapes.add_textbox(CONTENT_LEFT, top, SLIDE_W - CONTENT_LEFT - MARGIN, Inches(0.45))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    _set_run(p.add_run(), text, size=14.5, bold=True, color=accent_hex)


# ---------------------------------------------------------------------------
# Slide-kind builders. Each takes (prs, slide_data, accent_hex, assets_dir)
# and returns the created slide. slide_data is a content.Slide instance.
# ---------------------------------------------------------------------------


def build_title(prs, s, accent_hex, assets_dir):
    """The opening moment: a full-slide dark terminal, title typed after a
    `# talk.md` comment line, a trailing `$ _` prompt with a static cursor.
    """
    slide = _blank_slide(prs, DARK_BG)
    bar_h = _tab_bar(slide, "talk.md")

    left = Inches(1.1)
    width = SLIDE_W - left - Inches(1.0)

    comment = slide.shapes.add_textbox(left, bar_h + Inches(1.0), width, Inches(0.5))
    p = comment.text_frame.paragraphs[0]
    _set_run(p.add_run(), "# ", size=18, bold=True, color=accent_hex, font=FONT_MONO)
    _set_run(p.add_run(), "talk.md", size=18, color=DARK_TEXT_SECONDARY, font=FONT_MONO)

    title_box = slide.shapes.add_textbox(left, bar_h + Inches(1.55), width, Inches(1.6))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    _set_run(p.add_run(), s.title, size=40, bold=True, color="#ffffff", font=FONT_TITLE)

    if s.subtitle:
        sub = slide.shapes.add_textbox(left, bar_h + Inches(2.75), width, Inches(0.8))
        sub.text_frame.word_wrap = True
        p = sub.text_frame.paragraphs[0]
        _set_run(p.add_run(), "> ", size=16, bold=True, color=accent_hex, font=FONT_MONO)
        _set_run(p.add_run(), s.subtitle, size=16, color=DARK_TEXT_SECONDARY, font=FONT_MONO)

    prompt = slide.shapes.add_textbox(left, bar_h + Inches(3.4), Inches(1.0), Inches(0.5))
    p = prompt.text_frame.paragraphs[0]
    _set_run(p.add_run(), "$", size=18, bold=True, color=accent_hex, font=FONT_MONO)
    _add_rect(slide, left + Inches(0.32), bar_h + Inches(3.48), Inches(0.13), Inches(0.32), accent_hex)

    return slide


def build_bullets(prs, s, accent_hex, assets_dir):
    slide = _blank_slide(prs)
    content_top = _chrome(slide, accent_hex, s.title, tab_label_for(s))

    box = slide.shapes.add_textbox(CONTENT_LEFT, content_top, SLIDE_W - CONTENT_LEFT - MARGIN,
                                     SLIDE_H - content_top - Inches(0.3))
    tf = box.text_frame
    tf.word_wrap = True
    for i, bullet in enumerate(s.bullets):
        _bulleted_paragraph(tf, bullet, accent_hex=accent_hex, size=17, first=(i == 0))
    return slide


def build_image(prs, s, accent_hex, assets_dir):
    slide = _blank_slide(prs)
    content_top = _chrome(slide, accent_hex, s.title, tab_label_for(s))

    box_top = content_top
    box_h = SLIDE_H - box_top - Inches(0.9 if s.caption else 0.3)
    box_left = CONTENT_LEFT
    box_w = SLIDE_W - box_left - MARGIN

    path = assets_dir / s.image if s.image else None
    if path and path.exists():
        _fit_picture(slide, path, box_left, box_top, box_w, box_h)
    else:
        _placeholder_box(slide, box_left, box_top, box_w, box_h, s.image or "(no image set)")

    if s.caption:
        cap_box = slide.shapes.add_textbox(box_left, SLIDE_H - Inches(0.75), box_w, Inches(0.5))
        tf = cap_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        _set_run(p.add_run(), s.caption, size=14, italic=True, color=TEXT_SECONDARY)
    return slide


def build_image_pair(prs, s, accent_hex, assets_dir):
    slide = _blank_slide(prs)
    content_top = _chrome(slide, accent_hex, s.title, tab_label_for(s))

    gap = Inches(0.3)
    col_w = (SLIDE_W - CONTENT_LEFT - MARGIN - gap) / 2
    img_h = SLIDE_H - content_top - Inches(0.9)

    pairs = [
        (CONTENT_LEFT, s.image_left, s.caption_left),
        (CONTENT_LEFT + col_w + gap, s.image_right, s.caption_right),
    ]
    for left, image, caption in pairs:
        path = assets_dir / image if image else None
        if path and path.exists():
            _fit_picture(slide, path, left, content_top, col_w, img_h)
        else:
            _placeholder_box(slide, left, content_top, col_w, img_h, image or "(no image set)")
        if caption:
            cap_box = slide.shapes.add_textbox(left, SLIDE_H - Inches(0.75), col_w, Inches(0.5))
            tf = cap_box.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            _set_run(p.add_run(), caption, size=13, italic=True, color=TEXT_SECONDARY)
    return slide


def build_image_bullets(prs, s, accent_hex, assets_dir):
    slide = _blank_slide(prs)
    content_top = _chrome(slide, accent_hex, s.title, tab_label_for(s))

    img_w = Inches(5.3)
    text_left = CONTENT_LEFT + img_w + Inches(0.4)
    img_h = SLIDE_H - content_top - Inches(0.3)

    path = assets_dir / s.image if s.image else None
    if path and path.exists():
        _fit_picture(slide, path, CONTENT_LEFT, content_top, img_w, img_h)
    else:
        _placeholder_box(slide, CONTENT_LEFT, content_top, img_w, img_h, s.image or "(no image set)")

    box = slide.shapes.add_textbox(text_left, content_top, SLIDE_W - text_left - MARGIN, img_h)
    tf = box.text_frame
    tf.word_wrap = True
    for i, bullet in enumerate(s.bullets):
        _bulleted_paragraph(tf, bullet, accent_hex=accent_hex, size=16, first=(i == 0))
    return slide


def _style_table(table, accent_hex, headers, rows):
    n_cols = len(headers)
    for c, header in enumerate(headers):
        cell = table.cell(0, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = hex_to_rgb(accent_hex)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        _set_run(p.add_run(), header, size=13, bold=True, color="#ffffff")

    for r, row in enumerate(rows, start=1):
        for c in range(n_cols):
            cell = table.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = hex_to_rgb(SURFACE if r % 2 else PANEL)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            value = row[c] if c < len(row) else ""
            _set_run(p.add_run(), value, size=12.5, bold=(c == 0), color=TEXT_PRIMARY)


def build_table(prs, s, accent_hex, assets_dir):
    slide = _blank_slide(prs)
    content_top = _chrome(slide, accent_hex, s.title, tab_label_for(s))

    footer_h = Inches(0.5) if s.footer else Inches(0)
    n_rows = len(s.table_rows) + 1
    n_cols = len(s.table_headers)
    width = SLIDE_W - CONTENT_LEFT - MARGIN
    height = SLIDE_H - content_top - Inches(0.3) - footer_h

    gshape = slide.shapes.add_table(n_rows, n_cols, CONTENT_LEFT, content_top, width, height)
    table = gshape.table
    _style_table(table, accent_hex, s.table_headers, s.table_rows)
    if s.footer:
        _add_footer(slide, s.footer, accent_hex, content_top + height + Inches(0.1))
    return slide


def build_comparison(prs, s, accent_hex, assets_dir):
    slide = _blank_slide(prs)
    content_top = _chrome(slide, accent_hex, s.title, tab_label_for(s))

    footer_h = Inches(0.5) if s.footer else Inches(0)
    headers = ["", s.comp_left_header, s.comp_right_header]
    n_rows = len(s.comp_rows) + 1
    width = SLIDE_W - CONTENT_LEFT - MARGIN
    height = SLIDE_H - content_top - Inches(0.3) - footer_h

    gshape = slide.shapes.add_table(n_rows, 3, CONTENT_LEFT, content_top, width, height)
    table = gshape.table
    table.columns[0].width = Inches(2.3)
    table.columns[1].width = Emu(int((width - Inches(2.3)) / 2))
    table.columns[2].width = Emu(int((width - Inches(2.3)) / 2))
    rows = [[label, left_val, right_val] for label, left_val, right_val in s.comp_rows]
    _style_table(table, accent_hex, headers, rows)
    if s.footer:
        _add_footer(slide, s.footer, accent_hex, content_top + height + Inches(0.1))
    return slide


def build_ladder(prs, s, accent_hex, assets_dir):
    slide = _blank_slide(prs)
    content_top = _chrome(slide, accent_hex, s.title, tab_label_for(s))

    n = len(s.ladder_rungs)
    total_h = SLIDE_H - content_top - Inches(0.3)
    row_h = total_h / n

    for i, (num, name, desc, setup) in enumerate(s.ladder_rungs):
        row_top = content_top + i * row_h

        tag_box = slide.shapes.add_textbox(CONTENT_LEFT, row_top, Inches(0.65), row_h)
        tf = tag_box.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        _set_run(p.add_run(), f"[{num}]", size=15, bold=True, color=accent_hex, font=FONT_MONO)

        text_left = CONTENT_LEFT + Inches(0.68)
        box = slide.shapes.add_textbox(text_left, row_top, SLIDE_W - text_left - MARGIN, row_h)
        tf2 = box.text_frame
        tf2.word_wrap = True
        tf2.vertical_anchor = MSO_ANCHOR.MIDDLE
        p2 = tf2.paragraphs[0]
        _set_run(p2.add_run(), f"{name}  ", size=16, bold=True, color=TEXT_PRIMARY)
        _set_run(p2.add_run(), desc, size=14, color=TEXT_SECONDARY)
        if setup:
            p3 = tf2.add_paragraph()
            _set_run(p3.add_run(), setup, size=11.5, color=accent_hex, font=FONT_MONO)

        if i < n - 1:
            _add_rect(slide, CONTENT_LEFT, row_top + row_h - Pt(0.5), SLIDE_W - CONTENT_LEFT - MARGIN, Pt(0.5), GRIDLINE)
    return slide


def _draw_notebook_mock(slide, left, top, w, h, accent_hex):
    """A static chart in a notebook cell - a muted, unmoving mockup."""
    _add_rect(slide, left, top, w, h, PANEL, rounded=True, line_hex=GRIDLINE)
    tag = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.1), Inches(1.2), Inches(0.3))
    p = tag.text_frame.paragraphs[0]
    _set_run(p.add_run(), "In [1]:", size=10.5, color=TEXT_MUTED, font=FONT_MONO)

    bar_heights = [0.35, 0.6, 0.45, 0.75, 0.5]
    n = len(bar_heights)
    chart_left = left + Inches(0.5)
    chart_w = w - Inches(1.0)
    chart_bottom = top + h - Inches(0.45)
    bar_w = chart_w / (n * 1.6)
    gap = bar_w * 0.6
    for i, frac in enumerate(bar_heights):
        bar_h = int(Inches(1.6) * frac)
        bx = int(chart_left + i * (bar_w + gap))
        by = int(chart_bottom - bar_h)
        _add_rect(slide, bx, by, int(bar_w), bar_h, MUTED_BAR)


def _draw_browser_mock(slide, left, top, w, h, accent_hex):
    """A small web app - a mini editor/browser strip, a slider, live bars."""
    _add_rect(slide, left, top, w, h, SURFACE, rounded=True, line_hex=GRIDLINE)
    bar_h = Inches(0.32)
    _add_rect(slide, left, top, w, bar_h, DARK_PANEL)
    dot_size = Inches(0.09)
    dot_top = top + (bar_h - dot_size) / 2
    for i, color in enumerate((MAC_RED, MAC_YELLOW, MAC_GREEN)):
        _add_dot(slide, left + Inches(0.15) + i * Inches(0.16), dot_top, dot_size, color)

    slider_top = top + bar_h + Inches(0.35)
    slider_left = left + Inches(0.4)
    slider_w = w - Inches(0.8)
    _add_rect(slide, slider_left, slider_top + Inches(0.06), slider_w, Pt(2.5), GRIDLINE)
    thumb_size = Inches(0.16)
    thumb_x = int(slider_left + slider_w * 0.62 - thumb_size / 2)
    _add_dot(slide, thumb_x, slider_top, thumb_size, accent_hex)

    bar_heights = [0.3, 0.75, 0.5, 0.85, 0.4]
    n = len(bar_heights)
    chart_left = left + Inches(0.5)
    chart_w = w - Inches(1.0)
    chart_bottom = top + h - Inches(0.35)
    bar_w = chart_w / (n * 1.6)
    gap = bar_w * 0.6
    for i, frac in enumerate(bar_heights):
        bh = int(Inches(1.4) * frac)
        bx = int(chart_left + i * (bar_w + gap))
        by = int(chart_bottom - bh)
        _add_rect(slide, bx, by, int(bar_w), bh, accent_hex)


def build_concept_pair(prs, s, accent_hex, assets_dir):
    """A small illustrated two-box contrast (e.g. a static notebook chart vs.
    a live web app), plus a one-line insight underneath both boxes.
    """
    slide = _blank_slide(prs)
    content_top = _chrome(slide, accent_hex, s.title, tab_label_for(s))

    gap = Inches(0.4)
    total_w = SLIDE_W - CONTENT_LEFT - MARGIN
    box_w = (total_w - gap) / 2
    box_h = Inches(3.0)
    box_top = content_top + Inches(0.1)
    right_left = CONTENT_LEFT + box_w + gap

    _draw_notebook_mock(slide, CONTENT_LEFT, box_top, box_w, box_h, accent_hex)
    _draw_browser_mock(slide, right_left, box_top, box_w, box_h, accent_hex)

    label_top = box_top + box_h + Inches(0.15)
    for left, label, note in (
        (CONTENT_LEFT, s.concept_left_label, s.concept_left_note),
        (right_left, s.concept_right_label, s.concept_right_note),
    ):
        box = slide.shapes.add_textbox(left, label_top, box_w, Inches(1.1))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        _set_run(p.add_run(), label, size=17, bold=True, color=TEXT_PRIMARY, font=FONT_TITLE)
        p2 = tf.add_paragraph()
        p2.space_before = Pt(4)
        _set_run(p2.add_run(), note, size=13, color=TEXT_SECONDARY)

    if s.insight:
        insight_box = slide.shapes.add_textbox(CONTENT_LEFT, SLIDE_H - Inches(0.65), total_w, Inches(0.5))
        tf = insight_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        _set_run(p.add_run(), "›  ", size=16, bold=True, color=accent_hex, font=FONT_MONO)
        _set_run(p.add_run(), s.insight, size=16, bold=True, italic=True, color=TEXT_PRIMARY)
    return slide


def build_cards(prs, s, accent_hex, assets_dir):
    """A row of labeled cards, plus an optional closing "hook" line that
    reads as connected prose underneath, not another card.
    """
    slide = _blank_slide(prs)
    content_top = _chrome(slide, accent_hex, s.title, tab_label_for(s))

    n = max(len(s.cards), 1)
    gap = Inches(0.35)
    total_w = SLIDE_W - CONTENT_LEFT - MARGIN
    card_w = (total_w - gap * (n - 1)) / n
    card_h = Inches(2.7)
    card_top = content_top + Inches(0.15)

    for i, (card_title, card_desc) in enumerate(s.cards):
        left = CONTENT_LEFT + i * (card_w + gap)
        _add_rect(slide, left, card_top, card_w, card_h, SURFACE, rounded=True, line_hex=GRIDLINE)
        _add_rect(slide, left + Inches(0.06), card_top, card_w - Inches(0.12), Pt(4), accent_hex)
        box = slide.shapes.add_textbox(left + Inches(0.25), card_top + Inches(0.3), card_w - Inches(0.5), card_h - Inches(0.6))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        _set_run(p.add_run(), card_title, size=17, bold=True, color=accent_hex, font=FONT_TITLE)
        p2 = tf.add_paragraph()
        p2.space_before = Pt(8)
        _set_run(p2.add_run(), card_desc, size=13.5, color=TEXT_PRIMARY)

    if s.hook:
        hook_top = card_top + card_h + Inches(0.35)
        hook_box = slide.shapes.add_textbox(CONTENT_LEFT, hook_top, total_w, SLIDE_H - hook_top - Inches(0.3))
        tf = hook_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        _set_run(p.add_run(), s.hook, size=15, italic=True, color=TEXT_SECONDARY)
    return slide


def build_bullets_meter(prs, s, accent_hex, assets_dir):
    """Each item gets a 12-dot tick meter (out of the 12 functionalities)
    instead of asking the audience to recall a number by heart; a plain
    `bullets` line still renders below as an ordinary closing sentence.
    """
    slide = _blank_slide(prs)
    content_top = _chrome(slide, accent_hex, s.title, tab_label_for(s))

    row_h = Inches(1.05)
    text_w = SLIDE_W - CONTENT_LEFT - MARGIN - Inches(2.3)
    meter_left = SLIDE_W - MARGIN - Inches(2.0)
    dot_size = Inches(0.12)
    dot_gap = Inches(0.045)

    top = content_top
    for text, n in s.meter_items:
        box = slide.shapes.add_textbox(CONTENT_LEFT, top, text_w, row_h)
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        _set_run(p.add_run(), text, size=15.5, color=TEXT_PRIMARY)

        dots_top = top + row_h / 2 - dot_size / 2
        for d in range(12):
            dx = int(meter_left + d * (dot_size + dot_gap))
            color = accent_hex if d < n else GRIDLINE
            _add_dot(slide, dx, int(dots_top), dot_size, color)
        count_box = slide.shapes.add_textbox(meter_left, dots_top + dot_size + Inches(0.04), Inches(2.0), Inches(0.25))
        p2 = count_box.text_frame.paragraphs[0]
        _set_run(p2.add_run(), f"{n} of 12", size=10.5, color=TEXT_MUTED, font=FONT_MONO)

        top += row_h

    if s.bullets:
        box = slide.shapes.add_textbox(CONTENT_LEFT, top + Inches(0.15), SLIDE_W - CONTENT_LEFT - MARGIN,
                                         SLIDE_H - top - Inches(0.5))
        tf = box.text_frame
        tf.word_wrap = True
        for i, bullet in enumerate(s.bullets):
            _bulleted_paragraph(tf, bullet, accent_hex=accent_hex, size=15, first=(i == 0))
    return slide


def build_quote(prs, s, accent_hex, assets_dir):
    """The thesis slide: styled as a block comment (`/* ... */`) on the same
    dark terminal surface as the title slide, so the two "moment" slides
    bookend the deck visually.
    """
    slide = _blank_slide(prs, DARK_BG)
    _add_rect(slide, 0, 0, Inches(0.18), SLIDE_H, accent_hex)

    left = Inches(1.2)
    width = SLIDE_W - left - Inches(1.2)

    if s.title:
        kicker_box = slide.shapes.add_textbox(left, Inches(1.5), width, Inches(0.5))
        p = kicker_box.text_frame.paragraphs[0]
        _set_run(p.add_run(), "# ", size=16, bold=True, color=accent_hex, font=FONT_MONO)
        _set_run(p.add_run(), s.title, size=16, color=DARK_TEXT_SECONDARY, font=FONT_MONO)

    mark_box = slide.shapes.add_textbox(left - Inches(0.1), Inches(2.05), width, Inches(0.8))
    p = mark_box.text_frame.paragraphs[0]
    _set_run(p.add_run(), "/*", size=30, bold=True, color=accent_hex, font=FONT_MONO)

    quote_box = slide.shapes.add_textbox(left, Inches(2.75), width, Inches(2.6))
    tf = quote_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    _set_run(p.add_run(), s.quote_text, size=27, bold=True, color="#ffffff", font=FONT_TITLE)

    end_box = slide.shapes.add_textbox(left, Inches(5.55), width, Inches(0.6))
    p = end_box.text_frame.paragraphs[0]
    _set_run(p.add_run(), "*/", size=30, bold=True, color=accent_hex, font=FONT_MONO)

    return slide


BUILDERS = {
    "title": build_title,
    "bullets": build_bullets,
    "image": build_image,
    "image_pair": build_image_pair,
    "image_bullets": build_image_bullets,
    "table": build_table,
    "comparison": build_comparison,
    "ladder": build_ladder,
    "quote": build_quote,
    "concept_pair": build_concept_pair,
    "cards": build_cards,
    "bullets_meter": build_bullets_meter,
}
