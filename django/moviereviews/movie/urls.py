"""URL configuration for the movie app's own '/movie/...' routes.

Included into the project via moviereviews/urls.py's
`path('movie/', include('movie.urls'))` - paths here are relative to
that prefix, so '<int:movie_id>/' below means '/movie/<id>/' overall.

home/about/signup still route directly from moviereviews/urls.py
(added before this file existed, when 3 routes was small enough to
list at the project level) - this file is only for movie routes added
from here on, following the same include() pattern news/urls.py
introduced first. Nothing wrong with a project having both styles at
once; it's just a question of when a given route was added.
"""

from django.urls import path

from . import views

urlpatterns = [
    # int converter means Django 404s automatically on a non-numeric
    # movie_id (e.g. '/movie/abc/') before views.detail() ever runs.
    path("<int:movie_id>/", views.detail, name="movie-detail"),
    path("<int:movie_id>/reviews/add/", views.add_review, name="add-review"),
    # These two key off the review's own id, not the movie's - a review
    # doesn't need its parent movie's id in the URL once it exists,
    # views.py's edit_review()/delete_review() get the movie via
    # review.movie. Prefixed with 'reviews/' (a literal, non-numeric
    # segment) so Django never confuses these with the '<int:movie_id>/'
    # pattern above - "reviews" isn't a valid int, so that pattern
    # simply doesn't match these URLs at all, regardless of list order.
    path("reviews/<int:review_id>/edit/", views.edit_review, name="edit-review"),
    path("reviews/<int:review_id>/delete/", views.delete_review, name="delete-review"),
]
