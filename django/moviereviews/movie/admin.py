from django.contrib import admin

from .models import Movie

# Registering a model here is what makes it manageable (list/add/edit/
# delete) from the admin site at /admin/ - without this line, Movie
# would exist in the database but be invisible to the admin UI.
admin.site.register(Movie)
