# Worked example: labeling tool with roles

Use this as a model when comparing a full-stack framework against an API + SPA.

## Requirements

- Reviewers label rows (for example "is this prediction correct?") and results are saved.
- Admins see everyone's labels, export them, and manage users.
- A reviewer sees only the rows assigned to them.
- A long job re-scores the dataset with a new model in the background.

This touches functionalities 2 to 12, so it is a fair test of both stacks.

## Django (one project) vs FastAPI + React + Tailwind (two projects)

| Function | Django | FastAPI + React + Tailwind |
|---|---|---|
| Project structure | 1 repo, 1 process | API repo + front-end repo, 2 processes |
| Persistence | ORM models + migrations, built in | SQLAlchemy (or SQLModel) + Alembic, you set it up |
| Authentication | `django.contrib.auth`, login/logout pages included | You build login, hash passwords, issue JWTs (the ready-made `fastapi-users` is in maintenance mode) |
| Authorization | Groups and permissions; filter with `Label.objects.filter(assignee=request.user)` | Dependency checks written per endpoint |
| Data isolation | Queryset filter, plus a shared mixin so it is not forgotten | Same rule, enforced and tested in every endpoint |
| Forms and validation | Django forms, server-side, automatic | Pydantic on the API; form state and client validation in React |
| Admin / back office | **Django admin manages users and labels for free** | You build it |
| UI polish | Templates + Tailwind + daisyUI | React + Tailwind + shadcn/ui (nicer, more work) |
| Interactivity | Full page loads, plus small JS (htmx or vanilla) if needed | Smooth, instant updates, no reloads |
| API for other consumers | Add Django REST Framework | **Built in.** The API is the product, with auto docs |
| Background re-scoring | Queue + status page (see `background-jobs.md`) | Same; `BackgroundTasks` only for tiny work |
| Time to a working prototype | Days | 1 to 2 weeks |

(Time estimates are a judgement, not a measurement.)

## Verdict

- **Django wins** for a working labeling tool for a small team. Auth, admin, forms and
  ownership filtering are solved problems, and the admin alone covers "manage users and
  export labels".
- **FastAPI + React wins** when: the labeling UI is genuinely fast and app-like (keyboard
  shortcuts, instant next item, drag and drop); other systems also need the API (for
  example a model pipeline pulling labels); or a front-end engineer will own the UI.

For a data professional working alone, **start with Django**. If the UI feels limiting
later, add a Django REST Framework API and put React in front without throwing away the
data model.
