from django.shortcuts import render

from .models import Movie

# Create your views here.


def home(request):
    """The site's landing page ('' in moviereviews/urls.py)."""
    # The search form in home.html submits via GET, so its "searchTerm"
    # field lands in request.GET rather than request.POST. .get() with a
    # default of "" means a fresh page load (no search submitted yet)
    # doesn't blow up with a KeyError.
    search_term = request.GET.get("searchTerm", "")

    # `icontains` is a case-insensitive substring match (Django's ORM
    # turns this into SQL's `LIKE '%term%'` under the hood) - "batman"
    # should still find "The Dark Knight"'s title only if "batman"
    # literally appears in it, so this is a title search, not a fuzzy
    # one. An empty search_term (fresh page load) shows every movie.
    if search_term:
        movies = Movie.objects.filter(title__icontains=search_term)
    else:
        movies = Movie.objects.all()

    # The dict passed as render()'s third argument is the template's
    # *context* - each key becomes a variable the template can use with
    # {{ name }}. See movie/templates/movie/home.html.
    context = {"name": "Xuan Vinh", "searchTerm": search_term, "movies": movies}
    return render(request, "movie/home.html", context)


def about(request):
    """The site's about page ('about/' in moviereviews/urls.py)."""
    context = {"name": "Xuan Vinh"}
    return render(request, "movie/about.html", context)


def signup(request):
    """Mailing-list signup confirmation ('signup/' in moviereviews/urls.py).

    Reached by submitting the mailing-list form on the home page.
    """
    email = request.GET.get("email", "")
    context = {"email": email}
    return render(request, "movie/signup.html", context)
