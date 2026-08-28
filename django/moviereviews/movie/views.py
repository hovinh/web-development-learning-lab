from django.shortcuts import render

# Create your views here.


def home(request):
    """The site's landing page ('' in moviereviews/urls.py)."""
    # The search form in home.html submits via GET, so its "searchTerm"
    # field lands in request.GET rather than request.POST. .get() with a
    # default of "" means a fresh page load (no search submitted yet)
    # doesn't blow up with a KeyError.
    search_term = request.GET.get("searchTerm", "")

    # The dict passed as render()'s third argument is the template's
    # *context* - each key becomes a variable the template can use with
    # {{ name }}. See movie/templates/movie/home.html.
    context = {"name": "Xuan Vinh", "searchTerm": search_term}
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
