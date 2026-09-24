# Demos: backing the "Web Dev for Data People" blog post

The blog draft
[`blog/web-dev-for-data-people/2026-09-20-web-dev-for-data-people.md`](../blog/web-dev-for-data-people/2026-09-20-web-dev-for-data-people.md)
makes two claims entirely in prose: that Django and FastAPI+React solve the same labeling-tool
problem very differently ("Two Real Stacks, One Problem"), and that a long-running job needs a
specific shape ("Long-running jobs"). The `web-stack-advisor` skill's
[`worked-example-labeling-tool.md`](../.claude/skills/web-stack-advisor/references/worked-example-labeling-tool.md)
and [`background-jobs.md`](../.claude/skills/web-stack-advisor/references/background-jobs.md)
carry the same claims and were, until now, written from documentation rather than run.

These three demos make those claims checkable by actually running the code.

| Demo | Backs | Proves |
|---|---|---|
| [`labeling-django/`](labeling-django/README.md) | "Two Real Stacks, One Problem" | Ownership filtering is one queryset line; auth and admin are free. |
| [`labeling-fastapi-react/`](labeling-fastapi-react/README.md) | "Two Real Stacks, One Problem" | Auth is hand-built (JWT); ownership is a check repeated per endpoint; the payoff is a fast, app-like UI. |
| [`long-jobs/`](long-jobs/README.md) | "Long-running jobs" | The blocking-vs-queued contrast, and that Huey-on-SQLite is a real, Windows-safe default. |

## Shared scenario

All three demos triage-label the same thing: a model has predicted a category for a batch of
support tickets, and a human reviewer confirms or corrects each prediction. Demos 1 and 2 are a
head-to-head on that exact task — same [sample data](sample-data/README.md), same three users
(`admin`, `alice`, `bob`), same ownership rule (a reviewer only ever sees their own assigned
rows). Demo 3 is intentionally its own minimal app rather than a feature bolted onto Demo 1, so
the long-jobs lesson reads without auth/admin noise around it.

## Why `sample-data/` is shared

This repo's rule is that stages are self-contained (see the root
[CLAUDE.md](../CLAUDE.md)). `demos/sample-data/` deliberately breaks that rule: Demos 1 and 2
are only a fair comparison if they label byte-identical rows, so both seed scripts read the same
[`sample-data/predictions.json`](sample-data/README.md) by relative path. Neither demo writes to
it.

## Running a demo

Each demo folder has its own README ending in a copy-pasteable run block. Every demo is meant to
actually be started and clicked through, not just read — see each README's "Manual checks"
section for the specific thing to look for (a 404 when `bob` requests `alice`'s item, the Django
admin listing everyone's labels for free, the FastAPI `/docs` Swagger form, the blocking endpoint
hanging vs. the queued one staying responsive).

## Out of scope

Deployment, Postgres, Celery/Redis, shadcn/ui, label export, and any edit to the blog post body
itself. These demos are meant to be small enough to actually run and read in one sitting — adding
any of the above would trade that off for realism these three claims don't need.
