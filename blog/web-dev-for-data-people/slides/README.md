# Slide deck: Web Dev for Data People

A ~90-minute talk deck for PSA data colleagues (DS/DE/DI, no web-dev background) built from
[the blog post](../2026-09-20-web-dev-for-data-people.md) and the four `demos/` that back it.

**Who it's for, and why the deck is shaped the way it is:** the audience has its own data
projects; a web app arrives *afterwards* as a supporting tool, and they will ask an LLM to build
it. That's the talk's selling point, so the LLM thread runs through every section rather than
living in one: the hook says "you'll ask an LLM", the "Web is secondary here" thesis comes
straight after it, the 12 functionalities are framed as the requirements you hand the LLM, each
gap ends with what to put in your request, and the Django demo opens with the real `PROMPT.md`
that built it. See `content.py`'s module docstring for the full rationale.
Generated from Python rather than hand-built in PowerPoint or a slides app, so it's cheap to
fine-tune: edit a file, rerun a script, get a new build. There are **two outputs from the same
content**, both generated from `content.py`:

- **`web-dev-for-data-people-slides.pptx`** - for PowerPoint / offline presenting.
- **`html/index.html`** - a browser-based deck (reveal.js), for presenting from a browser tab.

Building both from `content.py` is deliberate, not just a demo of the tooling: the deck's own
opening argument is that a live web page makes a point a static file can't ("a chart in a
notebook convinces you, it rarely convinces a colleague who won't open it"). Presenting the deck
itself as a web page is that argument, live, in the room - see the small footnote on the title
slide and the "Stay in the driver's seat" section in [`content.py`](content.py) for the talk's
main thesis: web is *secondary* here, the point is choosing a stack and working with an LLM
without losing your grip on the backend/business logic.

Both decks' visual design is "editor tabs" - every slide is framed like a code editor, with a
dark tab bar (traffic-light window-control dots + a monospace fake filename) across the top. See
"Design language" below for how the two decks stay in sync on purpose, not just by convention.

## Files

- **`content.py`** - the actual talk content: `Section`s of `Slide`s (title, layout `kind`,
  bullets, image path, speaker notes, minute budget). **This is the file to edit to fine-tune
  either deck** - swap a bullet, add a slide, change a screenshot, adjust the timing - then rerun
  both generators below.
- **`theme.py`** - how a slide of a given `kind` (`title`, `bullets`, `table`, `ladder`,
  `comparison`, `image`, `image_pair`, `image_bullets`, `quote`, `concept_pair`, `cards`,
  `bullets_meter`, `code`) is drawn in the **.pptx**: colors, fonts, spacing, shapes. Owns the
  palette both themes share (see "Design language").
- **`theme_html.py`** - the same `kind` -> layout mapping, drawn as **HTML/CSS** instead of pptx
  shapes; calls `theme.tab_label_for()` for its tab-bar labels and reads `theme.MAC_RED` /
  `theme.DARK_BG` / etc. for colors, rather than re-deriving or re-typing any of it, so the two
  decks' chrome can't quietly drift apart again - see "Design language".
- **`generate_deck.py`** - builds the `.pptx` from `content.py` + `theme.py`; prints a
  total-minutes-vs-90 sanity check plus any screenshot paths still missing.
- **`generate_html_deck.py`** - builds `html/index.html` from the same `content.py` +
  `theme_html.py`, using [reveal.js](https://revealjs.com/) loaded from a CDN (no npm install, no
  build step - the same "CDN browser build" pattern `demos/labeling-django/` and
  `demos/psa-terminal-map/` already use in this repo).
- **`capture_screenshots.py`** - one Playwright function per demo (`capture_django()`,
  `capture_fastapi_react()`, `capture_long_jobs()`, `capture_psa_map()`, `capture_field_map()`),
  using the exact selectors confirmed working against each demo. Not one orchestrator, since the
  four demos need very different setup first (see below) - each function assumes its demo's
  server(s) are already running.
- **`assets/screenshots/<demo>/*.png`** - the captured screenshots, shared by both decks.
- **`tests/test_content.py`** - guards the things easy to break while editing `content.py`: a
  typo'd image path, a timing budget that's drifted far from 90 minutes, a slide `kind` either
  theme has no renderer for, that the HTML deck actually builds one slide per planned slide,
  that meter ticks are real positions (1-12), that `code` slides have 1-2 panels, and that no
  two slides share a tab-bar label.

## Regenerating the decks

```bash
# from the repo root, with .venv active
python blog/web-dev-for-data-people/slides/generate_deck.py
python blog/web-dev-for-data-people/slides/generate_html_deck.py
```

Rerun either any time after editing `content.py`/`theme.py`/`theme_html.py`. A screenshot path
that doesn't exist yet renders as a clearly-labeled placeholder instead of failing the build.

```bash
pytest blog/web-dev-for-data-people/slides/tests
```

## Presenting the HTML deck

Open `html/index.html` directly (double-click, or drag into a browser tab) - it has no external
data fetches, so plain `file://` works, unlike `demos/psa-terminal-map/`. Or serve it with the
repo-root tooling for a nicer URL: `npm run serve -- blog/web-dev-for-data-people/slides/html`.

Controls (all reveal.js defaults, nothing custom): arrow keys or click to advance, **S** for
speaker view (notes + per-slide minute budget + a timer, in a second window - works best served
over `http://`, not `file://`, since the speaker window talks to the main one), **F** for
fullscreen, **Esc** for the slide overview grid.

## Design language

**The .pptx (`theme.py`)** is "editor tabs" - every slide is framed like a code editor, chosen
after a round of side-by-side style samples because it tests better for a room of engineers than
a plain rule ever could, and reads as *of* the material (a coding talk) rather than decoration on
top of it:

- A dark tab bar runs across the top of every slide: the classic red/yellow/green macOS
  window-control dots, plus a monospace "filename" naming what the slide holds, auto-derived by
  `theme.tab_label_for()` - content.py never names it. Screenshot slides show the screenshot's
  own path (`django/alice-queue.png`); `code` slides show the file their first panel quotes
  (`PROMPT.md`); everything else gets a slug of the title with filler words and contractions
  dropped (`climb-must.md`, `12-functionalities.json`) - a plain "first three words" slug once
  produced labels like `what-we-ll.md` that read as typos from the audience.
- A thin accent gutter runs down the left edge below the bar, like an editor's line-number rail.
- The title slides (opening and "Questions?") and the "Web is secondary here" thesis quote
  slide (right after the hook) go full-terminal: a typed `# talk.md` / `/* ... */` comment,
  white text on a dark surface, a static cursor block - a moment, not a document.
- No icon badges anywhere - the tab-bar/terminal chrome itself is the personality, so a floating
  emoji badge would be redundant on top of it. (An earlier draft tried a circular icon badge
  riding on a solid color header band; it read as a decorative afterthought disconnected from the
  rest of the slide, which is why it's gone.)
- The ladder's rungs get a monospace `[1]`-style bracket tag instead of a badge; bullets get a
  monospace `›` prompt marker instead of a dash, on a hanging indent so wrapped lines align
  under the text rather than back under the marker.
- One accent color per section, cycling through the six-color categorical palette
  `demos/psa-terminal-map/css/style.css` uses for its own D3 charts (slightly darkened via
  `theme._shade()` for calmer on-slide use) - so the deck and the demo it screenshots read as one
  visual system.
- Bullet text has no per-line emoji; the two places emoji *do* appear (✅/🚫 in "Stay in the
  driver's seat") are load-bearing, not decoration.
- Three content-editing additions, added for specific slides rather than as a redesign:
  `concept_pair` (a small illustrated two-box contrast, e.g. a static notebook chart vs. a live
  web app, each drawn from primitive shapes rather than a screenshot), `cards` (a row of labeled
  cards plus an optional closing "hook" line that reads as prose, not another card), and
  `bullets_meter` (each line gets a 12-dot meter, one dot per row of the 12-functionality
  table, lit at the ticked *positions* - e.g. `[3, 6]` - so the audience sees how far right the
  ticks sit, which is what decides the rung). A `footer` field on `table`/`comparison`/`ladder`/
  `code` slides draws a bold one-line conclusion underneath, for a slide that needs to land a
  point rather than just present data. `col_weights` optionally sets relative table column
  widths.
- A `code` kind: one or two dark editor panels of monospace text, each headed by the file it
  quotes. Used for the two *evidence* slides - the real `PROMPT.md` that built the Django demo,
  and the same ownership rule in the Django and FastAPI codebases. `#` comments are highlighted
  (`theme.CODE_COMMENT`) because on those slides the comments are the message: the
  plain-language decision next to the code.

**The HTML deck (`theme_html.py`)** implements the same editor-tabs chrome in CSS: the same tab
bar with the same three dot colors, the same accent gutter (a `border-left` on `.slide-body`),
the same full-terminal title/quote slides (a typed `# talk.md` comment, a `/* ... */` block
comment, a static cursor block). This is a redesign of an earlier plainer "white canvas" HTML
look that drifted out of sync with the .pptx once already - closing that gap wasn't a one-time
fix, it's structural: `theme_html.py` calls `theme.tab_label_for(s)` for every tab label and
reads `theme.MAC_RED`/`theme.DARK_BG`/`theme.MUTED_BAR`/etc. for every shared color, instead of
re-deriving or re-typing any of it. Two things make a future drift loud instead of silent:
`tests/test_content.py`'s `test_every_slide_kind_is_a_known_html_renderer` fails the build if a
new `kind` gets a pptx builder but no HTML renderer, and its
`test_html_tab_labels_match_pptx_tab_labels` fails if the HTML deck's tab-bar text ever stops
matching `theme.tab_label_for()`'s output. Neither test checks pixel-for-pixel CSS parity (that
still needs a human glance after any layout change to either theme file) - they catch the two
failure modes that actually happened: a missing renderer, and a hand-typed value silently
diverging from its source of truth.

Every rule in `theme_html.CSS` is automatically scoped under `.reveal` (`_scope_under_reveal()`).
Without that, reveal.js's own theme selectors (`.reveal h2`, `.reveal ul`) out-ranked the
deck's bare class selectors, so slide titles rendered huge and black in reveal's heading font
and bullet lists got a disc bullet in front of the `›` marker - a silent mismatch with the
.pptx that only a screenshot revealed.

## Re-capturing screenshots

Each demo needs its own servers running before `capture_screenshots.py` can drive it - there's no
single "capture everything" command (`playwright` is already in the shared `.venv`; run
`playwright install chromium` once if the browser binary isn't present):

1. Start the demo per its own README (`demos/labeling-django/README.md`,
   `demos/labeling-fastapi-react/README.md`, `demos/long-jobs/README.md`,
   `demos/psa-terminal-map/README.md`) - migrate/seed if it has a database, start the server(s),
   wait for the URL to respond. (`capture_django()` labels a few items as alice and bob before
   shooting the admin page, so the "every reviewer's labels" screenshot isn't an empty list; it
   writes to the demo's gitignored `db.sqlite3`.)
2. Run the matching function, e.g. `python -c "import capture_screenshots as c; c.capture_django()"`
   from this folder - it re-captures that demo's whole shot list into `assets/screenshots/<demo>/`.
3. Stop whatever servers you started.

The exact shot list currently in the deck (see `content.py`'s `image`/`image_left`/`image_right`
fields for the authoritative list of what's expected):

| Demo | Screenshots |
|---|---|
| `django/` | `alice-queue.png`, `label-item.png`, `admin-labels.png`, `admin-users.png` |
| `fastapi-react/` | `login.png`, `alice-queue.png`, `labeling-in-progress.png`, `swagger-docs.png`, `swagger-admin-endpoint.png` |
| `long-jobs/` | `idle.png`, `queued-start.png`, `queued-progress.png`, `queued-done.png`, `blocking-stuck.png` |
| `psa-map/` | `map-overview.png`, `detail-card.png`, `build-trail.png`, `live-advisor.png` |
| `field-map/` | `field-map.png` (rasterized from `../images/field-map.svg` via a Playwright screenshot of the SVG element, not a separate SVG-to-PNG dependency) |

## Deck structure

17 sections, 39 slides in the planned run of show, budgeted to ~86.5 minutes including four
live demos (leaving a few minutes of slack in a 90-minute slot; the screenshots above are a
fallback if a live demo hiccups). See the section list in `content.py` for the full run of
show; roughly: why this matters (ending on "you'll ask an LLM to build it") → the driver's-seat
thesis → the field of tools → the 12-functionality framework → the ladder → pretty enough → the
two gaps (multi-user, background jobs) → the Django-vs-FastAPI+React comparison, the request
that built the Django demo, both live demos, and the ownership rule side by side in both
codebases → the long-jobs demo → the skill file and how to trigger it → the PSA map demo (the
skill as a runnable page, so it comes *after* the skill is introduced) → close (setup
cheat-sheet, takeaways, the repo URL, Q&A). The closing bullets slide is titled "Takeaways", not
"Three lessons" - it grew past three once already, so the title is deliberately count-agnostic.

Tick numbers follow one convention everywhere: the *deciding* ticks from the skill's
`references/use-cases.md` (a labeling tool is "#7-10"), not every functionality an app touches.

An 18th section, **Appendix** (`minutes=0`, so it doesn't count toward the budget): the "can I
get the best of both worlds" backup slide for Q&A, and the four "Run it: `<demo>` demo" slides
with each demo's exact terminal commands. Those used to sit right before each live demo; they
moved here because they're instructions for whoever runs the demo, not content the audience
needs mid-talk, and they cost ~3.5 minutes of flow. Give any future appendix slide `minutes=0`
too, so `total_minutes()` keeps reporting the actual talk length.

## Dependencies

`python-pptx` and `playwright` are direct dependencies in the repo-root `requirements.in` (see
its comments there for why). Neither is stage-specific tooling in the usual sense - they exist
only to build and populate this deck - but the repo's convention is one shared venv/lockfile for
everything, so they're pinned there like any other dependency. The HTML deck adds nothing to
that lockfile: reveal.js loads from a CDN at view time (`generate_html_deck.py`'s
`REVEAL_CDN`), the same no-install approach `demos/labeling-django/` and
`demos/psa-terminal-map/` already use for Tailwind/D3.
