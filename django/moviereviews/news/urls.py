"""URL configuration for the news app.

Included into the project via moviereviews/urls.py's
`path('news/', include('news.urls'))` - paths here are relative to
that prefix, so '' below means '/news/' overall.

This is the first app-level urls.py in this project (movie/ still
routes straight from moviereviews/urls.py, see that file's comment) -
worth introducing here since a second app is exactly when routing
everything from one flat project-level file starts getting crowded.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="news-index"),
]
