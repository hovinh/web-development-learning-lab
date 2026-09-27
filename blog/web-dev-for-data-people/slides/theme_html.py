"""HTML rendering for the deck - the web counterpart to theme.py's pptx builders.

Same idea as theme.py: content.py says *what* a slide contains, this module
says *how* it's drawn, one `render_<kind>()` function per slide `kind`. The
two themes deliberately import their palette from the same place (`theme.py`
itself) so the .pptx and the web deck read as one visual system, not two -
restrained, white-canvas, one accent color per section, used sparingly.

The deck is built on reveal.js (loaded from a CDN, no npm install / build
step - the same "CDN browser build" pattern `demos/labeling-django/` and
`demos/psa-terminal-map/` already use in this repo for Tailwind/D3). Each
`render_*` function returns one `<section>` - one reveal.js slide.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

import theme

ESC = lambda text: escape(str(text), quote=False)  # noqa: E731 - tiny, used everywhere below


def _header(title: str) -> str:
    return f'<div class="slide-header"><h2 class="slide-title">{ESC(title)}</h2></div>'


def _notes(notes: str, minutes: float) -> str:
    text = f"[~{minutes:g} min] {notes}" if notes else f"[~{minutes:g} min]"
    return f'<aside class="notes">{ESC(text)}</aside>'


def _image_or_placeholder(rel_path: str | None, assets_dir: Path, alt: str) -> str:
    if rel_path and (assets_dir / rel_path).exists():
        return f'<img src="../assets/screenshots/{rel_path}" alt="{ESC(alt)}">'
    label = rel_path or "(no image set)"
    return f'<div class="img-placeholder">screenshot pending:<br>{ESC(label)}</div>'


def render_title(s, accent, assets_dir, footnote: str | None = None) -> str:
    sub_html = f'<p class="title-subtitle">{ESC(s.subtitle)}</p>' if s.subtitle else ""
    footnote_html = f'<p class="title-footnote">{ESC(footnote)}</p>' if footnote else ""
    return (
        f'<section class="title-slide" style="--accent: {accent}">'
        f'<h1 class="title-heading">{ESC(s.title)}</h1>'
        f'<hr class="accent-rule">'
        f"{sub_html}"
        f"{footnote_html}"
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_bullets(s, accent, assets_dir) -> str:
    items = "".join(f"<li>{ESC(b)}</li>" for b in s.bullets)
    return (
        f'<section style="--accent: {accent}">'
        f"{_header(s.title)}"
        f'<ul class="bullet-list">{items}</ul>'
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_image(s, accent, assets_dir) -> str:
    img_html = _image_or_placeholder(s.image, assets_dir, s.title)
    cap_html = f'<p class="img-caption">{ESC(s.caption)}</p>' if s.caption else ""
    return (
        f'<section style="--accent: {accent}">'
        f"{_header(s.title)}"
        f'<div class="img-single">{img_html}</div>'
        f"{cap_html}"
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_image_pair(s, accent, assets_dir) -> str:
    left_img = _image_or_placeholder(s.image_left, assets_dir, s.caption_left)
    right_img = _image_or_placeholder(s.image_right, assets_dir, s.caption_right)
    left_cap = f'<p class="img-caption">{ESC(s.caption_left)}</p>' if s.caption_left else ""
    right_cap = f'<p class="img-caption">{ESC(s.caption_right)}</p>' if s.caption_right else ""
    return (
        f'<section style="--accent: {accent}">'
        f"{_header(s.title)}"
        f'<div class="img-pair">'
        f'<div class="img-col">{left_img}{left_cap}</div>'
        f'<div class="img-col">{right_img}{right_cap}</div>'
        f"</div>"
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_image_bullets(s, accent, assets_dir) -> str:
    img_html = _image_or_placeholder(s.image, assets_dir, s.title)
    items = "".join(f"<li>{ESC(b)}</li>" for b in s.bullets)
    return (
        f'<section style="--accent: {accent}">'
        f"{_header(s.title)}"
        f'<div class="img-bullets-row">'
        f'<div class="img-single img-single--side">{img_html}</div>'
        f'<ul class="bullet-list">{items}</ul>'
        f"</div>"
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def _table_html(headers, rows) -> str:
    thead = "".join(f"<th>{ESC(h)}</th>" for h in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{ESC(v)}</td>" for v in row)
        body_rows.append(f"<tr>{cells}</tr>")
    return f'<table><thead><tr>{thead}</tr></thead><tbody>{"".join(body_rows)}</tbody></table>'


def render_table(s, accent, assets_dir) -> str:
    return (
        f'<section style="--accent: {accent}">'
        f"{_header(s.title)}"
        f'<div class="table-wrap">{_table_html(s.table_headers, s.table_rows)}</div>'
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_comparison(s, accent, assets_dir) -> str:
    headers = ["", s.comp_left_header, s.comp_right_header]
    return (
        f'<section style="--accent: {accent}">'
        f"{_header(s.title)}"
        f'<div class="table-wrap">{_table_html(headers, s.comp_rows)}</div>'
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_ladder(s, accent, assets_dir) -> str:
    rows = []
    for num, name, desc, setup in s.ladder_rungs:
        setup_html = f'<span class="ladder-setup">{ESC(setup)}</span>' if setup else ""
        rows.append(
            f'<div class="ladder-row">'
            f'<span class="ladder-badge">{num}</span>'
            f'<div class="ladder-body"><b>{ESC(name)}</b> {ESC(desc)}{setup_html}</div>'
            f"</div>"
        )
    return (
        f'<section style="--accent: {accent}">'
        f"{_header(s.title)}"
        f'<div class="ladder">{"".join(rows)}</div>'
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_quote(s, accent, assets_dir) -> str:
    kicker_html = f'<p class="quote-kicker">{ESC(s.title.upper())}</p>' if s.title else ""
    return (
        f'<section class="quote-slide" style="--accent: {accent}">'
        f'<div class="quote-mark">&ldquo;</div>'
        f"{kicker_html}"
        f'<p class="quote-text">{ESC(s.quote_text)}</p>'
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


RENDERERS = {
    "title": render_title,
    "bullets": render_bullets,
    "image": render_image,
    "image_pair": render_image_pair,
    "image_bullets": render_image_bullets,
    "table": render_table,
    "comparison": render_comparison,
    "ladder": render_ladder,
    "quote": render_quote,
}


CSS = f"""
:root {{
  --text-primary: {theme.TEXT_PRIMARY};
  --text-secondary: {theme.TEXT_SECONDARY};
  --text-muted: {theme.TEXT_MUTED};
  --gridline: {theme.GRIDLINE};
  --panel: {theme.PANEL};
  --surface: {theme.SURFACE};
}}

.reveal {{ font-family: "Segoe UI", "Calibri", Arial, sans-serif; color: var(--text-primary); }}
.reveal .slides section {{
  text-align: left;
  top: 0 !important;
  height: 100%;
  box-sizing: border-box;
  padding: 2.2rem 3rem 1.5rem;
  border-top: 5px solid var(--accent, var(--gridline));
  background: var(--surface);
  display: flex;
  flex-direction: column;
}}

.slide-header {{
  padding-bottom: 0.9rem;
  border-bottom: 1px solid var(--gridline);
  margin-bottom: 1.6rem;
  flex-shrink: 0;
}}
.slide-title {{ font-size: 1.65rem; font-weight: 600; margin: 0; color: var(--text-primary); }}

.bullet-list {{ list-style: none; margin: 0; padding: 0; }}
.bullet-list li {{
  position: relative;
  padding-left: 1.5rem;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  line-height: 1.5;
  color: var(--text-primary);
}}
.bullet-list li::before {{
  content: "\\2013";
  position: absolute;
  left: 0;
  color: var(--accent);
  font-weight: 700;
}}

.table-wrap {{ overflow: auto; }}
table {{ width: 100%; border-collapse: collapse; font-size: 1rem; }}
th {{
  background: var(--accent);
  color: #fff;
  text-align: left;
  padding: 0.65rem 0.9rem;
  font-weight: 600;
}}
td {{ padding: 0.6rem 0.9rem; border-bottom: 1px solid var(--gridline); font-size: 0.95rem; }}
tbody tr:nth-child(even) td {{ background: var(--panel); }}
td:first-child {{ font-weight: 600; }}

.ladder {{ display: flex; flex-direction: column; }}
.ladder-row {{
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid var(--gridline);
}}
.ladder-row:last-child {{ border-bottom: none; }}
.ladder-badge {{
  width: 2.4rem;
  height: 2.4rem;
  min-width: 2.4rem;
  border: 1.5px solid var(--accent);
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: var(--accent);
}}
.ladder-body {{ font-size: 1.1rem; color: var(--text-secondary); padding-top: 0.15rem; }}
.ladder-body b {{ color: var(--text-primary); }}
.ladder-setup {{
  display: block;
  font-family: Consolas, monospace;
  color: var(--accent);
  font-size: 0.85rem;
  margin-top: 0.3rem;
}}

.img-single {{ display: flex; align-items: center; justify-content: center; margin-top: 0.75rem; }}
.img-single img {{ max-width: 100%; max-height: 460px; border: 1px solid var(--gridline); }}
.img-pair {{ display: flex; gap: 1.75rem; margin-top: 0.5rem; }}
.img-col {{ flex: 1; display: flex; flex-direction: column; align-items: center; min-width: 0; }}
.img-col img {{ max-width: 100%; max-height: 440px; border: 1px solid var(--gridline); }}
.img-bullets-row {{ display: flex; gap: 2rem; align-items: center; margin-top: 0.75rem; }}
.img-single--side {{ flex: 0 0 45%; }}
.img-single--side img {{ max-height: 400px; }}
.img-bullets-row .bullet-list {{ flex: 1; }}
.img-caption {{
  text-align: center;
  color: var(--text-secondary);
  font-style: italic;
  font-size: 0.95rem;
  margin: 0.75rem 0 0;
}}
.img-placeholder {{
  width: 100%;
  padding: 3rem 1rem;
  text-align: center;
  border: 1px dashed var(--gridline);
  border-radius: 8px;
  background: var(--panel);
  color: var(--text-muted);
  font-style: italic;
}}

.title-slide, .quote-slide {{
  border-top: none !important;
  border-left: 6px solid var(--accent);
  justify-content: center;
  padding-left: 4rem;
  position: relative;
}}
.title-heading {{ font-size: 2.9rem; font-weight: 700; margin: 0; color: var(--text-primary); }}
.accent-rule {{ width: 80px; border: none; border-top: 3px solid var(--accent); margin: 1.3rem 0; }}
.title-subtitle {{ font-size: 1.35rem; color: var(--text-secondary); margin: 0; }}
.title-footnote {{
  position: absolute;
  bottom: 1.5rem;
  right: 2.5rem;
  font-size: 0.9rem;
  color: var(--text-muted);
  font-style: italic;
}}

.quote-mark {{ font-size: 5rem; font-weight: 700; color: var(--accent); line-height: 1; font-family: Georgia, serif; }}
.quote-kicker {{ font-size: 0.95rem; font-weight: 700; letter-spacing: 0.04em; color: var(--accent); margin: 0.5rem 0 1.5rem; }}
.quote-text {{ font-size: 1.85rem; font-weight: 700; color: var(--text-primary); line-height: 1.4; max-width: 46rem; }}
"""
