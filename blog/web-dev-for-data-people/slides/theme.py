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
and kind by `_tab_label_for()` - content.py never has to name it. Below the
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
chart colors. The macOS-style traffic-light dot colors (`_MAC_RED` etc.) are
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
# _shade() with the rest of the palette.
_MAC_RED = "#ff5f56"
_MAC_YELLOW = "#febc2e"
_MAC_GREEN = "#28c840"

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


def _tab_label_for(s) -> str:
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
    for i, color in enumerate((_MAC_RED, _MAC_YELLOW, _MAC_GREEN)):
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
    content_top = _chrome(slide, accent_hex, s.title, _tab_label_for(s))

    box = slide.shapes.add_textbox(CONTENT_LEFT, content_top, SLIDE_W - CONTENT_LEFT - MARGIN,
                                     SLIDE_H - content_top - Inches(0.3))
    tf = box.text_frame
    tf.word_wrap = True
    for i, bullet in enumerate(s.bullets):
        _bulleted_paragraph(tf, bullet, accent_hex=accent_hex, size=17, first=(i == 0))
    return slide


def build_image(prs, s, accent_hex, assets_dir):
    slide = _blank_slide(prs)
    content_top = _chrome(slide, accent_hex, s.title, _tab_label_for(s))

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
    content_top = _chrome(slide, accent_hex, s.title, _tab_label_for(s))

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
    content_top = _chrome(slide, accent_hex, s.title, _tab_label_for(s))

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
    content_top = _chrome(slide, accent_hex, s.title, _tab_label_for(s))

    n_rows = len(s.table_rows) + 1
    n_cols = len(s.table_headers)
    width = SLIDE_W - CONTENT_LEFT - MARGIN
    height = SLIDE_H - content_top - Inches(0.3)

    gshape = slide.shapes.add_table(n_rows, n_cols, CONTENT_LEFT, content_top, width, height)
    table = gshape.table
    _style_table(table, accent_hex, s.table_headers, s.table_rows)
    return slide


def build_comparison(prs, s, accent_hex, assets_dir):
    slide = _blank_slide(prs)
    content_top = _chrome(slide, accent_hex, s.title, _tab_label_for(s))

    headers = ["", s.comp_left_header, s.comp_right_header]
    n_rows = len(s.comp_rows) + 1
    width = SLIDE_W - CONTENT_LEFT - MARGIN
    height = SLIDE_H - content_top - Inches(0.3)

    gshape = slide.shapes.add_table(n_rows, 3, CONTENT_LEFT, content_top, width, height)
    table = gshape.table
    table.columns[0].width = Inches(2.3)
    table.columns[1].width = Emu(int((width - Inches(2.3)) / 2))
    table.columns[2].width = Emu(int((width - Inches(2.3)) / 2))
    rows = [[label, left_val, right_val] for label, left_val, right_val in s.comp_rows]
    _style_table(table, accent_hex, headers, rows)
    return slide


def build_ladder(prs, s, accent_hex, assets_dir):
    slide = _blank_slide(prs)
    content_top = _chrome(slide, accent_hex, s.title, _tab_label_for(s))

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
}
