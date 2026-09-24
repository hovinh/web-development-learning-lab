# Demo 1 — labeling tool, Django

Backs the blog's ["Two Real Stacks, One Problem"](../../blog/web-dev-for-data-people/2026-09-20-web-dev-for-data-people.md)
section and the `web-stack-advisor` skill's
[`worked-example-labeling-tool.md`](../../.claude/skills/web-stack-advisor/references/worked-example-labeling-tool.md).
Its head-to-head counterpart is [`../labeling-fastapi-react/`](../labeling-fastapi-react/README.md) —
same task, same [shared sample data](../sample-data/README.md), same three users.

## The idea

A model has predicted a category for a batch of support tickets ([`Item`](labeling/models.py)).
A reviewer opens their queue, sees only the tickets assigned to them, and records whether the
prediction was correct ([`Label`](labeling/models.py)). Everything about "only their own tickets"
and "who can see what" is the thing this demo is here to test.

This follows the [`django-for-beginners`](../../django-for-beginners/README.md) scaffold
convention exactly: project package `django_project`, app package `labeling`, function-based
views, named URLs, `app.apps.AppConfig` in `INSTALLED_APPS` under a `# local` comment. See
[docs/python-implementation.md](../../docs/python-implementation.md)'s framework-scaffold
exception.

## Ownership: one line, not a per-view check

The blog's strongest claim is that Django's ownership filtering is "a queryset filter, one line".
[`labeling/views.py`](labeling/views.py)'s `queue()` view is exactly that:

```python
items = Item.objects.filter(assigned_to=request.user)
```

There's no separate step to remember — the query itself can't return anyone else's rows.
`label_item()` enforces the same rule when a reviewer opens one specific ticket, this time via
`get_object_or_404(Item, pk=item_id, assigned_to=request.user)`, so guessing another reviewer's
item id in the URL 404s instead of leaking their ticket. `labeling/tests.py`'s
`test_reviewer_cannot_open_another_reviewers_item` is the automated version of that check — run
the identical assertion against [`../labeling-fastapi-react/`](../labeling-fastapi-react/README.md)
and you're comparing the same guarantee built two different ways.

## Auth: built in, not built by hand

`django_project/urls.py` wires up `django.contrib.auth.urls`, which is what gives this demo
login/logout, "wrong password" handling, and `LOGIN_URL`/`LOGIN_REDIRECT_URL`-driven redirects
with **zero hand-written view code** — only [`registration/login.html`](labeling/templates/registration/login.html)
was written, to skin the built-in `LoginView`. Compare
[`../labeling-fastapi-react/api/security.py`](../labeling-fastapi-react/api/security.py), which
has to mint and verify its own JWTs from scratch. That contrast is the whole point of this demo
existing rather than reusing `django-impatient/moviereviews`'s own hand-rolled `accounts` app —
"built in" is exactly the claim under test here.

## Admin: the strongest argument

[`labeling/admin.py`](labeling/admin.py) registers `Item` and `Label` with `list_display`/
`list_filter`/`search_fields`. That's the entire implementation of "admins see everyone's labels
and manage users" — no view, no template, no code written for it beyond those two decorator
calls.

**To log in as admin:**

1. Start the server (see "Run it" below) and open http://127.0.0.1:8000/admin/.
2. Django's admin app has its **own** login page, separate from the styled one at `/accounts/login/`
   that `@login_required` sends reviewers to — visiting `/admin/` while logged out redirects to
   `/admin/login/` (a plain, unstyled Django-generated form, not `registration/login.html`).
   Same `User` table either way, so the same credentials work at both.
3. Log in with `admin` / `demo-admin-pw` (see the credentials table below).

**To set up an account or change a password**, from `/admin/` click **Users** under
**AUTHENTICATION AND AUTHORIZATION**:

- **Change a password:** click a username (e.g. `alice`) to open their change form, then
  **"this form"** in the small blue text under the password field (URL: `/admin/auth/user/<id>/password/`) —
  a dedicated "set password" form, not the plain text field the rest of the page uses.
- **Create a new account:** click **"ADD USER +"** in the top right of the user list, fill in a
  username and password, then open the new user's change form to set `is_staff`/`is_superuser`
  if they should also have admin access.

Every reviewer's labels (filterable by decision or reviewer) and the full `User` list are there
with no view or template written for either — that's `django.contrib.auth`'s free half of this
comparison.

## Styling: prototype-only Tailwind

[`labeling/templates/labeling/base.html`](labeling/templates/labeling/base.html) loads Tailwind 4
and daisyUI 5 as browser builds straight from a CDN (`@tailwindcss/browser@4`), the same "no
Node, no build step" approach `django-impatient/moviereviews` uses for Bootstrap via jsDelivr.
This is explicitly **not** production-ready: the browser build recompiles Tailwind's whole
utility set on every page load (there's no scan-and-purge step trimming it to only the classes
actually used) and the page won't render without internet access. A real deployment would run
the Tailwind CLI (or `@tailwindcss/vite`, as Demo 2 does) ahead of time and ship a small, purged
CSS file instead.

## Seeding

```
python manage.py seed_demo
```

`labeling/management/commands/seed_demo.py` creates one superuser (`admin`) and two reviewers
(`alice`, `bob`), then loads [`../sample-data/predictions.json`](../sample-data/README.md) and
assigns its 30 rows to the two reviewers round-robin (15 each). It's `get_or_create`-based, so
running it again after the first time is a no-op.

**Demo credentials — local dev only, never real passwords:**

| Username | Password | Role |
|---|---|---|
| `admin` | `demo-admin-pw` | Superuser, `/admin/` access |
| `alice` | `demo-alice-pw` | Reviewer |
| `bob` | `demo-bob-pw` | Reviewer |

## Tests

`labeling/tests.py` uses Django's own test runner (no pytest here — no Django stage in this repo
does; see [docs/python-implementation.md](../../docs/python-implementation.md)). The two that
matter most: a reviewer's queue never shows another reviewer's ticket, and opening another
reviewer's item id directly 404s.

## Run it

```bash
# from the repo root, with .venv active
python demos/labeling-django/manage.py migrate
python demos/labeling-django/manage.py seed_demo
python demos/labeling-django/manage.py runserver
python demos/labeling-django/manage.py test labeling
```

Then open http://127.0.0.1:8000/, log in as `alice` or `bob`, and label a few tickets.

## Manual checks

1. Log in as `alice`, note an item id from her queue (the URL `/1/` etc.); log in as `bob` (or
   an incognito window) and visit that same URL — expect a 404, matching the same check in
   [`../labeling-fastapi-react/`](../labeling-fastapi-react/README.md).
2. Log in as `admin` and open http://127.0.0.1:8000/admin/ — every reviewer's labels and the
   full user list are there, with no view or template written for them.

## Reproducing this demo

[`PROMPT.md`](PROMPT.md) is the build prompt this demo was implemented from, kept for future
reference (e.g. to rebuild the same demo, with the same gotchas already worked out, elsewhere).
