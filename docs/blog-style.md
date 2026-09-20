# Blog post style guide

Conventions for drafting posts under `blog/` in this repo, mirrored from the author's
personal blog ([hovinh/hovinh.github.io](https://github.com/hovinh/hovinh.github.io),
`blog/_posts/*.md`, a Jekyll site). Follow this whenever starting a new blog post so
drafts here migrate to the personal blog with minimal rework.

## Where a post lives

- One new folder directly under `blog/`, named with a short topic slug (e.g.
  `blog/pairwise-alignment/`).
- One Markdown file inside it, named `YYYY-MM-DD-<topic-slug>.md` — the date is when the
  draft is written, matching Jekyll's `_posts` naming convention so the file can be
  dropped into the personal blog's `_posts/` folder as-is later.
- If the post has diagrams, put them in an `images/` subfolder alongside the post
  (`blog/<topic-slug>/images/*.svg`) and reference them with relative paths
  (`images/foo.svg`). The personal blog instead serves figures from
  `/assets/blog/YYYY-MM-DD/*.png` — leave that path rewrite (and any SVG→PNG conversion)
  to the author at migration time; don't try to guess the final asset path.
- Candidate topics for future posts are tracked in `blog/README.md` — check it before
  starting a new post, and note there which topic a new post covers.

## Frontmatter

```yaml
---
layout: post
title: "..."
description: >
  One to two sentences, shown as the post's summary/subtitle.
author: author1
comments: true
---
```

Title style: descriptive, often `"X: Y"` (a hook or frame, then what the post covers) or
`"An/A ... to ..."` — not clickbait, not a bare topic label.

## Opening lines

Immediately after the frontmatter, before the first section header:

- `**Prerequisite**: ...` — comma-separated list of what the reader should already know
  (concepts, languages). Omit only if the post is genuinely accessible with no
  background.
- No `**Code**: <a>Github</a>` line, and no other link to or mention of this repo by
  name — see Code below for why. The post has to carry enough real code on its own to
  stand without it.
- For a longer post (roughly 6+ sections), a Markdown table of contents: one bullet per
  `##` section, linking to its GitHub-style anchor (`#lowercase-hyphenated-heading`).
  Skip the TOC for a short post (the DTW-algorithm-style post in the personal blog omits
  it; the Sudoku-solver-style post includes it).

## Prose style

- First person, conversational, but technical — this is a technical deep-dive, not a
  casual note. Motivate *why* before showing *how*: open a section with the problem or
  biological/practical context, then bring in the code or math that solves it.
  Reads well as a story arc, not a reference doc: build one idea, then show how the next
  problem/section pressures it to generalize.
  Anecdotes and personal framing (a book that inspired the project, a real-world use
  case) are welcome in the intro — they're what make the post's opening distinct from a
  dry spec.
- Bold key terms the first time they're introduced (`**edit distance**`, `**indel**`).
- Section headers (`##`) should name the *idea*, not just the problem code — e.g. "When
  an Indel Is One Event, Not Many" rather than "GCON". If the section is grounded in a
  specific problem/dataset, name it right under the header, e.g.
  `**[GCON — Global Alignment with Constant Gap Penalty](https://rosalind.info/problems/gcon/)**`
  as its own line.
- Blockquotes (`>`) for a formal definition or a statement worth pausing on.
- End with a `## Summary` section that names the throughline explicitly (the axes of
  generalization, the recurring lesson) rather than just restating each section in
  miniature.

## Math

Use `$$...$$` (Jekyll/MathJax, KaTeX-compatible) for inline and block math — the
personal blog renders both this way. This applies to inline math too, even a single
variable sitting in a sentence: `$$i$$`, not `$i$` — a single `$...$` pair renders as
literal dollar signs rather than math on this setup, so it's an easy mistake to
reintroduce out of ordinary LaTeX habit. Prefer `$$...$$` over ASCII-art formulas
whenever a recurrence, sum, or optimization objective is being stated precisely.

## Code

This repo's solutions aren't meant to be public, in view of Rosalind's stance on
sharing solutions — so a post built on them can't point a reader at the repo to fill in
what a snippet leaves out, the way the Code-link convention above once assumed. That
changes what a snippet is allowed to look like, without changing where the logic comes
from:

- Base every snippet on this repo's actual implementation — never invented pseudocode.
  Adapting it for standalone presentation (dropping a leading underscore off a
  module-private helper's name, cutting an unused alternate constructor) is fine as
  long as the logic itself is untouched.
- Never name or link this repo, and drop the old `# bioinformatics/alignment/foo.py`
  source-file comment above a snippet — nothing in the post should point at a specific
  file in a specific repo.
- Each snippet must be complete and runnable on its own within the post. `...` (or a
  comment gesturing at "the rest lives elsewhere") is no longer a legitimate way to
  elide logic that's actually load-bearing for the mechanism being explained, since the
  reader has no repo to go check it against — expand it into the real code instead. It's
  still fine to leave out something genuinely incidental to the point being made (an
  unrelated helper, an alternate constructor the post never calls) — just don't gesture
  at what was cut.
- Syntax-highlighted fenced blocks (` ```python `, ` ```yaml `, etc.), never plain
  indented code.

## Figures

The personal blog embeds figures as:

```markdown
![FigNN](/assets/blog/YYYY-MM-DD/description.png){:data-width="1440" data-height="836"}
Fig. N. Caption text describing what the figure shows and how to read it.
{:.figure}
```

For a post drafted in this repo (no `/assets/blog/` path yet), use a relative path into
the post's own `images/` folder instead, and prefer hand-authored SVG over a generated
raster image so diagrams stay text-diffable and easy to tweak:

```markdown
![Fig01](images/dp-traceback-table.svg){:data-width="560" data-height="400"}
Fig. 1. Caption text.
{:.figure}
```

Number figures sequentially (`Fig01`, `Fig02`, ...) in the order they appear. Every
figure needs a caption that stands on its own — don't rely on the surrounding prose to
explain what's in it. Reach for a figure when a relationship is genuinely spatial or
comparative (a DP table with a traceback path, a state machine, several variants laid
out side by side) — not as decoration for a section that reads fine as prose.

When a figure is showing a *process* rather than a static structure — a DP table
filling in cell by cell, a traceback path growing back to the origin — an animated GIF
communicates that better than a static SVG. Generate it with a small Python script
under the post's own `blog/<topic-slug>/scripts/` folder (never inside `bioinformatics/`
— it's a visualization tool, not solving logic), free to import from `bioinformatics/`
directly for correctness even though the post's own code snippets can't quote it
verbatim (see Code above); write the rendered `.gif` into the post's `images/` folder
like any other figure. The generator script itself is plumbing, not prose — it's never
shown, linked, or referenced in the post body, only its output image is. Reserve GIFs
for genuine processes; a conceptual/structural diagram (a state machine, a table of
variants) is still clearer as a static SVG.

## Footnotes / external references

Numbered footnotes at the very end of the post, after `## Summary`, separated by a
horizontal rule (`---`):

```markdown
---

(1) <a href="https://...">https://...</a>
```

Reference them inline with a superscript link: `text<sup><a href="#fn1">(1)</a></sup>`
(the personal blog's actual posts link straight to the external URL twice — inline and
in the footnote — rather than an anchor-jump; match that if precision matters less than
matching precedent).

## What not to do

- Don't write the post as a flat list of "problem X does Y" entries — group by the idea
  each step adds, and let problem IDs anchor sections rather than structure them.
- Don't skip the biological/practical motivation for a generalization in favor of
  jumping straight to the code — the personal blog's posts consistently explain *why*
  the more complex version is needed before showing it.
- Don't invent figures/diagrams for relationships that are just as clear in a sentence.
- Don't name, link, or point at this repo (or a file path within it) anywhere in a post
  — see Code and Opening lines above.
