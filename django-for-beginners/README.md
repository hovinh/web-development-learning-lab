# django-for-beginners

Notes for working through *Django for Beginners* (William Vincent).
Unlike `django-impatient` (one running project), this book builds a
separate small Django project per chapter, so it follows this repo's
default convention of one subfolder per stage - see the root
[README.md](../README.md) for the full list of stages so far.

This README covers the core mental model the rest of the book builds
on: how a request turns into a rendered page, and the routine for
adding a new one.

## The MVT flow

Django calls its architecture **MVT** (Model-View-Template) - a
variant of the more familiar MVC. A request moves through four files
in a fixed order:

```
Browser
  |  GET /about/
  v
urls.py        <- matches the URL path to a view function
  |
  v
views.py       <- the view runs: pulls data from models (if any),
  |                builds a context dict, picks a template
  |
  +--> models.py    (optional - only if the page needs DB data)
  |
  v
templates/*.html   <- filled in with the context, rendered to HTML
  |
  v
HttpResponse
  |
  v
Browser (renders the HTML)
```

The **view is the only piece that talks to the other two** - `urls.py`
never touches models or templates directly, and templates never query
the database directly. Keeping that one-way flow is what makes each
piece easy to reason about on its own.

## URLs (`urls.py`)

Maps a URL pattern (a path string) to a view function:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('about/', views.about, name='about'),
]
```

- Every Django *project* has one root `urls.py`. Larger apps get their
  own `urls.py` too, wired into the root one with
  `include('app_name.urls')` - keeps each app's routes self-contained
  instead of piling everything into one file.
- The `name='about'` argument lets other code refer to this URL by
  name instead of hardcoding the path - e.g. `{% url 'about' %}` in a
  template, or `reverse('about')` in Python. If the path string ever
  changes, every reference using the name still works.

## Views (`views.py`)

A plain Python function (or class, for class-based views later in the
book) that takes an `HttpRequest` and returns an `HttpResponse`:

```python
from django.shortcuts import render

def about(request):
    return render(request, 'app_name/about.html', {'company': 'Acme'})
```

- `render()` is a shortcut that loads the named template, fills it in
  with the given context dict, and wraps the result in an
  `HttpResponse` - the three steps most views need every time.
- This is where the actual logic lives: reading query parameters,
  querying models, deciding which template applies, handling form
  submissions.

## Models (`models.py`)

A Python class subclassing `django.db.models.Model`. Each class is a
database table; each class attribute is a column:

```python
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

- Django's ORM lets you query the database with Python instead of SQL:
  `Article.objects.all()`, `Article.objects.filter(title__icontains='django')`,
  `Article.objects.get(pk=1)`.
- A model class only becomes a real database table after running:
  ```bash
  python manage.py makemigrations   # generates a migration file describing the schema change
  python manage.py migrate          # applies it to the database
  ```
  Any time a model is added or changed, both commands need to be
  re-run - Django never alters the database on its own just because
  `models.py` changed.

## Templates (`*.html`)

HTML with Django's own template tags mixed in:

- `{{ variable }}` - outputs a value from the context dict.
- `{% tag %}` - logic: `{% if %}`, `{% for %}`, `{% extends %}`,
  `{% block %}`, `{% include %}`, `{% url 'name' %}`.
- Templates live under each app's `templates/<app_name>/` folder (the
  app name repeated is intentional "namespacing" - with `APP_DIRS`
  enabled, every app's `templates/` folder is searched as one flat
  pool, so two apps' `home.html` would otherwise collide).
- The usual pattern is one `base.html` per project with the shared
  page shell (`<head>`, nav bar) and a `{% block content %}`
  placeholder; every other template does
  `{% extends "app_name/base.html" %}` and only fills in that block -
  avoids repeating boilerplate on every page.

## Checklist: adding a new page

Every new page touches some subset of these steps, roughly in this
order:

1. **Decide the URL** - e.g. `/articles/`.
2. **`urls.py`** - add a `path()` entry pointing at a (possibly new)
   view function, with a `name=`.
3. **`models.py`** (only if the page needs stored data that doesn't
   exist yet) - add/update a model class, then run `makemigrations`
   and `migrate`.
4. **`views.py`** - write the view function: pull data from the model
   if needed, build the context dict, `render()` the template.
5. **`templates/app_name/*.html`** - create the template,
   `{% extends %}` the shared base, fill in `{% block content %}`
   using the context variables the view passed in.
6. **Link to it** - if the page should be reachable from navigation,
   add a link in `base.html` (or wherever the nav lives) using
   `{% url 'name' %}` rather than a hardcoded path.
7. **Run and check** - `python manage.py runserver`, visit the new
   URL, confirm it renders as expected.
