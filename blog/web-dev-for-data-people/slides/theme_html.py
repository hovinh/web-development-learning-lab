"""HTML rendering for the deck - the web counterpart to theme.py's pptx builders.

Same idea as theme.py: content.py says *what* a slide contains, this module
says *how* it's drawn, one `render_<kind>()` function per slide `kind`. This
module deliberately imports its chrome logic - not just its colors - from
`theme.py`: the tab label for a slide comes from `theme.tab_label_for(s)`
(the exact same function the .pptx uses), and the traffic-light dot colors,
dark-surface colors, and muted illustration color come from `theme.MAC_RED`
/ `theme.DARK_BG` / `theme.MUTED_BAR` etc. rather than being re-typed as
literal hex values here. The goal is that theme.py stays the single source
of truth for the look, so a future change to the .pptx chrome (a new accent,
a resized tab bar, a new dark color) either shows up here automatically or
fails loudly (a `theme_html` name that no longer exists) - not silently, the
way the two decks' chrome drifted apart the first time.

Both decks are built on the SAME `content.py`, walked by their own generator
script (`generate_deck.py` / `generate_html_deck.py`); adding a new slide
`kind` requires a renderer in both `theme.BUILDERS` and this module's
`RENDERERS`, or `tests/test_content.py`'s
`test_every_slide_kind_is_a_known_html_renderer` fails the build - that
test is what actually enforces "add a kind here too", not just this
docstring.

The deck is built on reveal.js (loaded from a CDN, no npm install / build
step - the same "CDN browser build" pattern `demos/labeling-django/` and
`demos/psa-terminal-map/` already use in this repo for Tailwind/D3). Each
`render_*` function returns one `<section>` - one reveal.js slide.
"""

from __future__ import annotations

import re
from html import escape
from pathlib import Path

import theme

ESC = lambda text: escape(str(text), quote=False)  # noqa: E731 - tiny, used everywhere below


def _header(title: str, tab_label: str) -> str:
    """The tab bar + the opening of `.slide-body` (title inside it).

    Every render_* function that calls this MUST close the div itself with
    a literal `"</div>"` once its own content is written - see any render_*
    below for the pattern. Keeping the close in the caller (rather than
    bundling a `_footer()` counterpart) means a render_* function can put
    a picture, a table, or anything else inside `.slide-body` without this
    helper needing to know what content kinds exist.
    """
    return (
        f'<div class="tab-bar">'
        f'<span class="tab-dot tab-dot--red"></span>'
        f'<span class="tab-dot tab-dot--yellow"></span>'
        f'<span class="tab-dot tab-dot--green"></span>'
        f'<span class="tab-label">{ESC(tab_label)}</span>'
        f"</div>"
        f'<div class="slide-body">'
        f'<h2 class="slide-title">{ESC(title)}</h2>'
    )


def _notes(notes: str, minutes: float) -> str:
    text = f"[~{minutes:g} min] {notes}" if notes else f"[~{minutes:g} min]"
    return f'<aside class="notes">{ESC(text)}</aside>'


def _image_or_placeholder(rel_path: str | None, assets_dir: Path, alt: str) -> str:
    if rel_path and (assets_dir / rel_path).exists():
        return f'<img src="../assets/screenshots/{rel_path}" alt="{ESC(alt)}">'
    label = rel_path or "(no image set)"
    return f'<div class="img-placeholder">screenshot pending:<br>{ESC(label)}</div>'


def render_title(s, accent, assets_dir, footnote: str | None = None) -> str:
    """The opening moment: a full-slide dark terminal, mirroring
    theme.build_title - a typed `# talk.md` comment, the title, an optional
    subtitle read as a `>` line, and a static `$ _` cursor.
    """
    sub_html = ""
    if s.subtitle:
        sub_html = f'<p class="title-subtitle"><span class="mono-prompt">&gt; </span>{ESC(s.subtitle)}</p>'
    footnote_html = f'<p class="title-footnote">{ESC(footnote)}</p>' if footnote else ""
    return (
        f'<section class="title-slide" style="--accent: {accent}">'
        f'<div class="tab-bar tab-bar--floating">'
        f'<span class="tab-dot tab-dot--red"></span>'
        f'<span class="tab-dot tab-dot--yellow"></span>'
        f'<span class="tab-dot tab-dot--green"></span>'
        f'<span class="tab-label">talk.md</span>'
        f"</div>"
        f'<p class="title-comment"><span class="mono-prompt"># </span>talk.md</p>'
        f'<h1 class="title-heading">{ESC(s.title)}</h1>'
        f"{sub_html}"
        f'<p class="title-cursor"><span class="mono-prompt">$</span><span class="cursor-block"></span></p>'
        f"{footnote_html}"
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_bullets(s, accent, assets_dir) -> str:
    items = "".join(f"<li>{ESC(b)}</li>" for b in s.bullets)
    return (
        f'<section style="--accent: {accent}">'
        f"{_header(s.title, theme.tab_label_for(s))}"
        f'<ul class="bullet-list">{items}</ul>'
        f"</div>"
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_image(s, accent, assets_dir) -> str:
    img_html = _image_or_placeholder(s.image, assets_dir, s.title)
    cap_html = f'<p class="img-caption">{ESC(s.caption)}</p>' if s.caption else ""
    return (
        f'<section style="--accent: {accent}">'
        f"{_header(s.title, theme.tab_label_for(s))}"
        f'<div class="img-single">{img_html}</div>'
        f"{cap_html}"
        f"</div>"
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
        f"{_header(s.title, theme.tab_label_for(s))}"
        f'<div class="img-pair">'
        f'<div class="img-col">{left_img}{left_cap}</div>'
        f'<div class="img-col">{right_img}{right_cap}</div>'
        f"</div>"
        f"</div>"
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_image_bullets(s, accent, assets_dir) -> str:
    img_html = _image_or_placeholder(s.image, assets_dir, s.title)
    items = "".join(f"<li>{ESC(b)}</li>" for b in s.bullets)
    return (
        f'<section style="--accent: {accent}">'
        f"{_header(s.title, theme.tab_label_for(s))}"
        f'<div class="img-bullets-row">'
        f'<div class="img-single img-single--side">{img_html}</div>'
        f'<ul class="bullet-list">{items}</ul>'
        f"</div>"
        f"</div>"
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def _table_html(headers, rows, col_weights=None) -> str:
    # Same optional relative column widths as theme.build_table, as a
    # <colgroup> of percentages.
    colgroup = ""
    if col_weights:
        total = sum(col_weights)
        cols = "".join(f'<col style="width:{100 * w / total:.1f}%">' for w in col_weights)
        colgroup = f"<colgroup>{cols}</colgroup>"
    thead = "".join(f"<th>{ESC(h)}</th>" for h in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{ESC(v)}</td>" for v in row)
        body_rows.append(f"<tr>{cells}</tr>")
    return f'<table>{colgroup}<thead><tr>{thead}</tr></thead><tbody>{"".join(body_rows)}</tbody></table>'


def _footer_html(footer: str) -> str:
    return f'<p class="table-footer">{ESC(footer)}</p>' if footer else ""


def render_table(s, accent, assets_dir) -> str:
    return (
        f'<section style="--accent: {accent}">'
        f"{_header(s.title, theme.tab_label_for(s))}"
        f'<div class="table-wrap">{_table_html(s.table_headers, s.table_rows, s.col_weights)}</div>'
        f"{_footer_html(s.footer)}"
        f"</div>"
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_comparison(s, accent, assets_dir) -> str:
    headers = ["", s.comp_left_header, s.comp_right_header]
    return (
        f'<section style="--accent: {accent}">'
        f"{_header(s.title, theme.tab_label_for(s))}"
        f'<div class="table-wrap">{_table_html(headers, s.comp_rows)}</div>'
        f"{_footer_html(s.footer)}"
        f"</div>"
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_ladder(s, accent, assets_dir) -> str:
    rows = []
    for num, name, desc, setup in s.ladder_rungs:
        setup_html = f'<span class="ladder-setup">{ESC(setup)}</span>' if setup else ""
        rows.append(
            f'<div class="ladder-row">'
            f'<span class="ladder-tag">[{num}]</span>'
            f'<div class="ladder-body"><b>{ESC(name)}</b> {ESC(desc)}{setup_html}</div>'
            f"</div>"
        )
    return (
        f'<section style="--accent: {accent}">'
        f"{_header(s.title, theme.tab_label_for(s))}"
        f'<div class="ladder">{"".join(rows)}</div>'
        f"{_footer_html(s.footer)}"
        f"</div>"
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_quote(s, accent, assets_dir) -> str:
    """The thesis slide: a block comment (`/* ... */`) on the same dark
    terminal surface as the title slide, mirroring theme.build_quote.
    """
    kicker_html = f'<p class="quote-kicker"><span class="mono-prompt"># </span>{ESC(s.title)}</p>' if s.title else ""
    return (
        f'<section class="quote-slide" style="--accent: {accent}">'
        f'<div class="quote-mark">/*</div>'
        f"{kicker_html}"
        f'<p class="quote-text">{ESC(s.quote_text)}</p>'
        f'<div class="quote-mark quote-mark--end">*/</div>'
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_concept_pair(s, accent, assets_dir) -> str:
    def mock(kind, bars):
        cls = "concept-mock--static" if kind == "static" else "concept-mock--live"
        bar_cls = "concept-bar--static" if kind == "static" else "concept-bar--live"
        bars_html = "".join(f'<div class="concept-bar {bar_cls}" style="height:{h}%"></div>' for h in bars)
        return f'<div class="concept-mock {cls}">{bars_html}</div>'

    left_html = mock("static", [35, 60, 45, 75, 50])
    right_html = mock("live", [30, 75, 50, 85, 40])
    insight_html = (
        f'<p class="concept-insight"><span class="mono-prompt">&rsaquo;  </span>{ESC(s.insight)}</p>'
        if s.insight
        else ""
    )
    return (
        f'<section style="--accent: {accent}">'
        f"{_header(s.title, theme.tab_label_for(s))}"
        f'<div class="concept-pair">'
        f'<div class="concept-box">{left_html}'
        f'<p class="concept-label">{ESC(s.concept_left_label)}</p>'
        f'<p class="concept-note">{ESC(s.concept_left_note)}</p></div>'
        f'<div class="concept-box">{right_html}'
        f'<p class="concept-label">{ESC(s.concept_right_label)}</p>'
        f'<p class="concept-note">{ESC(s.concept_right_note)}</p></div>'
        f"</div>"
        f"{insight_html}"
        f"</div>"
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_cards(s, accent, assets_dir) -> str:
    cards_html = "".join(
        f'<div class="card"><h3>{ESC(t)}</h3><p>{ESC(d)}</p></div>' for t, d in s.cards
    )
    hook_html = f'<p class="cards-hook">{ESC(s.hook)}</p>' if s.hook else ""
    return (
        f'<section style="--accent: {accent}">'
        f"{_header(s.title, theme.tab_label_for(s))}"
        f'<div class="cards-row">{cards_html}</div>'
        f"{hook_html}"
        f"</div>"
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_bullets_meter(s, accent, assets_dir) -> str:
    # Dots are positions (dot N lit = functionality N ticked), not a count -
    # see theme.build_bullets_meter for why.
    rows = []
    for text, ticks in s.meter_items:
        dots = "".join(
            f'<span class="meter-dot{" meter-dot--on" if (d + 1) in ticks else ""}"></span>' for d in range(12)
        )
        rows.append(
            f'<div class="meter-row">'
            f'<span class="meter-text">{ESC(text)}</span>'
            f'<span class="meter-dots">{dots}<span class="meter-count">{ESC(theme.meter_label(ticks))}</span></span>'
            f"</div>"
        )
    items = "".join(f"<li>{ESC(b)}</li>" for b in s.bullets)
    bullets_html = f'<ul class="bullet-list">{items}</ul>' if s.bullets else ""
    return (
        f'<section style="--accent: {accent}">'
        f"{_header(s.title, theme.tab_label_for(s))}"
        f'<div class="meter-list">{"".join(rows)}</div>'
        f"{bullets_html}"
        f"</div>"
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


def render_code(s, accent, assets_dir) -> str:
    """One or two dark editor-like panels - mirrors theme.build_code, using
    theme.split_code_line so `#` comments get the same highlight here.
    """
    panels = []
    for header, code in s.code_panels:
        lines = []
        for line in code.split("\n"):
            code_part, comment_part = theme.split_code_line(line)
            comment_html = f'<span class="code-comment">{ESC(comment_part)}</span>' if comment_part else ""
            lines.append(f"{ESC(code_part)}{comment_html}")
        panels.append(
            f'<div class="code-panel">'
            f'<div class="code-header">{ESC(header)}</div>'
            f'<pre class="code-body">{chr(10).join(lines)}</pre>'
            f"</div>"
        )
    return (
        f'<section style="--accent: {accent}; --code-size: {s.code_size / 13:.3f}rem">'
        f"{_header(s.title, theme.tab_label_for(s))}"
        f'<div class="code-row">{"".join(panels)}</div>'
        f"{_footer_html(s.footer)}"
        f"</div>"
        f"{_notes(s.notes, s.minutes)}"
        f"</section>"
    )


RENDERERS = {
    "title": render_title,
    "code": render_code,
    "bullets": render_bullets,
    "image": render_image,
    "image_pair": render_image_pair,
    "image_bullets": render_image_bullets,
    "table": render_table,
    "comparison": render_comparison,
    "ladder": render_ladder,
    "quote": render_quote,
    "concept_pair": render_concept_pair,
    "cards": render_cards,
    "bullets_meter": render_bullets_meter,
}


CSS = f"""
:root {{
  --text-primary: {theme.TEXT_PRIMARY};
  --text-secondary: {theme.TEXT_SECONDARY};
  --text-muted: {theme.TEXT_MUTED};
  --gridline: {theme.GRIDLINE};
  --panel: {theme.PANEL};
  --surface: {theme.SURFACE};
  --dark-bg: {theme.DARK_BG};
  --dark-panel: {theme.DARK_PANEL};
  --dark-text: {theme.DARK_TEXT};
  --dark-text-secondary: {theme.DARK_TEXT_SECONDARY};
  --dark-gridline: {theme.DARK_GRIDLINE};
  --mac-red: {theme.MAC_RED};
  --mac-yellow: {theme.MAC_YELLOW};
  --mac-green: {theme.MAC_GREEN};
  --muted-bar: {theme.MUTED_BAR};
  --code-comment: {theme.CODE_COMMENT};
}}

.reveal {{ font-family: "Segoe UI", "Calibri", Arial, sans-serif; color: var(--text-primary); }}
.reveal .slides section {{
  text-align: left;
  top: 0 !important;
  height: 100%;
  box-sizing: border-box;
  padding: 0 3rem 1.5rem;
  background: var(--surface);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}}

/* --- tab-bar chrome: mirrors theme._tab_bar()/theme._chrome() exactly - a
   dark strip with the same three traffic-light dots and a monospace
   "filename" from theme.tab_label_for(), then an accent gutter down the
   left edge of the body below it. --- */
.tab-bar {{
  margin: 0 -3rem 1.4rem;
  background: var(--dark-panel);
  padding: 0.55rem 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-shrink: 0;
}}
.tab-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
.tab-dot--red {{ background: var(--mac-red); }}
.tab-dot--yellow {{ background: var(--mac-yellow); }}
.tab-dot--green {{ background: var(--mac-green); }}
.tab-label {{ margin-left: 0.7rem; font-family: Consolas, monospace; font-size: 0.85rem; color: var(--dark-text-secondary); }}

.slide-body {{
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding-left: 1.1rem;
  border-left: 4px solid var(--accent);
}}
.slide-title {{ font-family: "Segoe UI Semibold", "Segoe UI", Arial, sans-serif; text-transform: none; letter-spacing: normal; font-size: 1.55rem; font-weight: 700; margin: 0 0 1.1rem; color: var(--accent); flex-shrink: 0; }}

.mono-prompt {{ font-family: Consolas, monospace; color: var(--accent); font-weight: 700; }}

.bullet-list {{ list-style: none; margin: 0; padding: 0; }}
.bullet-list li {{
  position: relative;
  padding-left: 1.6rem;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  line-height: 1.5;
  color: var(--text-primary);
}}
.bullet-list li::before {{
  content: "\\203a";
  position: absolute;
  left: 0;
  font-family: Consolas, monospace;
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
.table-footer {{ margin-top: 0.9rem; font-weight: 700; color: var(--accent); font-size: 1.05rem; }}

.ladder {{ display: flex; flex-direction: column; }}
.ladder-row {{
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid var(--gridline);
}}
.ladder-row:last-child {{ border-bottom: none; }}
.ladder-tag {{
  min-width: 2.4rem;
  font-family: Consolas, monospace;
  font-weight: 700;
  color: var(--accent);
  padding-top: 0.15rem;
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
.img-single img {{ max-width: 100%; max-height: 420px; border: 1px solid var(--gridline); }}
.img-pair {{ display: flex; gap: 1.75rem; margin-top: 0.5rem; }}
.img-col {{ flex: 1; display: flex; flex-direction: column; align-items: center; min-width: 0; }}
.img-col img {{ max-width: 100%; max-height: 400px; border: 1px solid var(--gridline); }}
.img-bullets-row {{ display: flex; gap: 2rem; align-items: center; margin-top: 0.75rem; }}
.img-single--side {{ flex: 0 0 45%; }}
.img-single--side img {{ max-height: 360px; }}
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

/* --- title & quote "moment" slides: full-slide dark terminal, mirroring
   theme.build_title()/theme.build_quote(). --- */
.title-slide, .quote-slide {{
  background: var(--dark-bg) !important;
  justify-content: center;
  padding: 0 4rem !important;
  position: relative;
  color: var(--dark-text);
}}
.title-slide .tab-bar--floating {{
  position: absolute;
  top: 0; left: 0; right: 0;
  margin: 0;
}}
.title-comment {{ font-family: Consolas, monospace; color: var(--dark-text-secondary); font-size: 1.05rem; margin: 3.5rem 0 0.5rem; }}
.title-heading {{ font-family: "Segoe UI Semibold", "Segoe UI", Arial, sans-serif; text-transform: none; letter-spacing: normal; font-size: 2.9rem; font-weight: 700; margin: 0 0 0.6rem; color: #ffffff; }}
.title-subtitle {{ font-family: Consolas, monospace; font-size: 1.05rem; color: var(--dark-text-secondary); margin: 0 0 1.5rem; }}
.title-cursor {{ margin: 0; }}
.cursor-block {{ display: inline-block; width: 0.6rem; height: 1.1rem; background: var(--accent); margin-left: 0.4rem; vertical-align: middle; }}
.title-footnote {{
  position: absolute;
  bottom: 1.5rem;
  right: 2.5rem;
  font-size: 0.9rem;
  color: var(--dark-text-secondary);
  font-style: italic;
}}

.quote-mark {{ font-family: Consolas, monospace; font-size: 2.4rem; font-weight: 700; color: var(--accent); line-height: 1; }}
.quote-mark--end {{ margin-top: 1.2rem; }}
.quote-kicker {{ font-family: Consolas, monospace; font-size: 1rem; color: var(--dark-text-secondary); margin: 0.6rem 0 1.5rem; }}
.quote-text {{ font-size: 1.85rem; font-weight: 700; color: #ffffff; line-height: 1.4; max-width: 46rem; }}

.concept-pair {{ display: flex; gap: 1.75rem; margin-top: 0.5rem; }}
.concept-box {{ flex: 1; min-width: 0; }}
.concept-mock {{
  border: 1px solid var(--gridline);
  border-radius: 8px;
  height: 220px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 0.6rem;
  padding: 0.75rem;
  box-sizing: border-box;
  position: relative;
  overflow: hidden;
}}
.concept-mock--static {{ background: var(--panel); }}
.concept-mock--live {{ background: var(--surface); }}
.concept-mock--live::before {{
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 22px;
  background: var(--dark-panel);
}}
.concept-bar {{ width: 26px; border-radius: 3px 3px 0 0; }}
.concept-bar--static {{ background: var(--muted-bar); }}
.concept-bar--live {{ background: var(--accent); }}
.concept-label {{ font-weight: 700; margin: 0.9rem 0 0.2rem; color: var(--text-primary); }}
.concept-note {{ margin: 0; color: var(--text-secondary); font-size: 0.95rem; }}
.concept-insight {{ margin-top: 1.1rem; font-weight: 700; font-style: italic; color: var(--text-primary); }}

.cards-row {{ display: flex; gap: 1.25rem; margin-top: 0.5rem; }}
.card {{
  flex: 1;
  border: 1px solid var(--gridline);
  border-top: 4px solid var(--accent);
  border-radius: 8px;
  padding: 1rem 1.1rem;
  min-width: 0;
}}
.card h3 {{ margin: 0 0 0.5rem; font-size: 1.1rem; color: var(--accent); }}
.card p {{ margin: 0; font-size: 0.95rem; color: var(--text-primary); }}
.cards-hook {{ margin-top: 1.25rem; font-style: italic; color: var(--text-secondary); font-size: 1.05rem; }}

.meter-list {{ display: flex; flex-direction: column; }}
.meter-row {{ display: flex; align-items: center; gap: 1.25rem; padding: 0.6rem 0; border-bottom: 1px solid var(--gridline); }}
.meter-row:last-child {{ border-bottom: none; }}
.meter-text {{ flex: 1; font-size: 1.05rem; color: var(--text-primary); }}
.meter-dots {{ display: flex; align-items: center; gap: 0.22rem; flex-shrink: 0; }}
.meter-dot {{ width: 10px; height: 10px; border-radius: 50%; background: var(--gridline); }}
.meter-dot--on {{ background: var(--accent); }}
.meter-count {{ font-family: Consolas, monospace; font-size: 0.75rem; color: var(--text-muted); margin-left: 0.5rem; }}

/* --- "code" slides: dark editor panels, mirroring theme.build_code(). --- */
.code-row {{ display: flex; gap: 1.2rem; flex: 1; min-height: 0; }}
.code-panel {{
  flex: 1;
  min-width: 0;
  background: var(--dark-bg);
  border-radius: 8px;
  padding: 0.6rem 1rem 0.8rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}}
.code-header {{
  font-family: Consolas, monospace;
  font-size: 0.75rem;
  color: var(--dark-text-secondary);
  padding-bottom: 0.45rem;
  margin-bottom: 0.55rem;
  border-bottom: 1px solid var(--dark-gridline);
}}
.reveal pre.code-body {{
  margin: 0;
  width: auto;
  box-shadow: none;
  background: transparent;
  font-family: Consolas, monospace;
  font-size: var(--code-size);
  line-height: 1.45;
  color: var(--dark-text);
  white-space: pre-wrap;
}}
.code-comment {{ color: var(--code-comment); }}
"""


def _scope_under_reveal(css: str) -> str:
    """Prefix every selector in `css` with `.reveal ` (unless it already
    starts with `.reveal` or is `:root`).

    Why: reveal.js's own theme (simple.css) styles elements through
    `.reveal h2`, `.reveal ul`, `.reveal p` and so on. A bare class selector
    like `.slide-title` has *lower* specificity than `.reveal h2`, so the
    theme silently won - slide titles came out huge and black instead of in
    the section accent color, and bullet lists got a disc bullet in front of
    the deck's own `›` marker. Scoping every rule under `.reveal` adds one
    class of specificity, enough to beat the theme's element-level rules
    without sprinkling `!important` everywhere.

    Deliberately simple (a regex over "selectors {"): the CSS above has no
    @media blocks or nested rules - if one is ever added, revisit this.
    """

    def scope_selector_list(match: re.Match) -> str:
        selectors = [s.strip() for s in match.group(1).split(",")]
        scoped = [s if s.startswith((".reveal", ":root")) else f".reveal {s}" for s in selectors]
        return ", ".join(scoped) + " {"

    # A rule starts at the beginning of a line with something other than a
    # brace or a `/*` comment, and runs up to its opening `{`.
    return re.sub(r"(?m)^([^{}\s/][^{}]*?)\s*\{", scope_selector_list, css)


CSS = _scope_under_reveal(CSS)
