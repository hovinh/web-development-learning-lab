# Build prompt: Demo 1 — Django labeling app

Saved for future reference — hand this to a fresh Claude Code session to rebuild this demo from
scratch (e.g. in another repo with the same conventions). See [`README.md`](README.md) for what
was actually built and how to run it.

---

Build a Django demo app at demos/labeling-django/ inside this repo, following its existing
conventions (see CLAUDE.md and docs/python-implementation.md). If demos/sample-data/predictions.json
doesn't exist yet, create it first: 30 rows of {id, text, model_label, model_score} - a fictional
model's triage prediction over a support ticket (model_label one of billing/technical/account/
shipping/refund), with a mix of high- and low-confidence, right and wrong predictions.

Scaffold with `django-admin startproject django_project .` then `startapp labeling`, matching
django-for-beginners/message-board's conventions exactly: function-based views, named URLs,
`labeling.apps.LabelingConfig` in INSTALLED_APPS under a `# local` comment, templates only under
labeling/templates/labeling/ and labeling/templates/registration/.

Models (labeling/models.py):
- Item: text, model_label, model_score, assigned_to (FK to settings.AUTH_USER_MODEL, null=True,
  on_delete=SET_NULL).
- Label: FK item, FK reviewer, decision (choices correct/incorrect/unsure), corrected_label,
  note, created_at, unique_together=(item, reviewer).

Views:
- queue() - @login_required, `Item.objects.filter(assigned_to=request.user)`. This one line is
  the whole point of the demo - comment it as such.
- label_item(item_id) - `get_object_or_404(Item, pk=item_id, assigned_to=request.user)` so another
  reviewer's item 404s. GET renders a LabelForm, POST saves (look up an existing Label for this
  reviewer+item first, so relabeling updates it instead of hitting the unique constraint).

Auth: use `django.contrib.auth.urls` (login/logout for free) rather than hand-rolling views -
that's the point of this demo vs. the FastAPI one. Set LOGIN_URL/LOGIN_REDIRECT_URL. Only write
labeling/templates/registration/login.html to skin the built-in LoginView.

Admin: register Item and Label in labeling/admin.py with list_display/list_filter/search_fields -
this is the "admins see everyone's labels and manage users for free" argument, give it weight.
Note for the README: Django admin has its OWN login page at /admin/login/, separate from
/accounts/login/ (same User table, same credentials, different unstyled form) - don't let that
confuse the write-up.

Styling: base.html loads Tailwind 4 + daisyUI 5 as browser builds from a CDN
(`@tailwindcss/browser@4` + daisyUI's CDN stylesheet, not the `@plugin "daisyui"` directive,
which needs an actual build step). Comment that this is prototype-only (no purge step, needs
internet).

Seed command (labeling/management/commands/seed_demo.py): creates admin/demo-admin-pw
(superuser), alice/demo-alice-pw, bob/demo-bob-pw (reviewers), loads
demos/sample-data/predictions.json by relative path, assigns rows round-robin by list position.
get_or_create-based so it's safe to re-run.

Tests (labeling/tests.py, Django's own runner, not pytest): the load-bearing one is logging in as
one reviewer and requesting another reviewer's item id directly - expect 404. Also test the queue
only shows a reviewer's own items, and that submitting/resubmitting a label works correctly.

Write demos/labeling-django/README.md covering: the idea, the ownership one-liner, the auth
contrast, the admin walkthrough (including how to log in as admin and how to change a user's
password or add a new user - click Users -> click a username -> "this form" link under the
password field -> /admin/auth/user/<id>/password/), the styling caveat, seeding, tests, and a
run block (migrate, seed_demo, runserver, test).

Verify by actually running: migrate, seed_demo, runserver, hit it with curl or a browser, run the
test suite, and confirm the 404 ownership check really happens.
