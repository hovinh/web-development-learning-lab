from django.shortcuts import render

# Create your views here.


def home(request):
    """The site's landing page ('' in moviereviews/urls.py)."""
    # The dict passed as render()'s third argument is the template's
    # *context* - each key becomes a variable the template can use with
    # {{ name }}. See movie/templates/movie/home.html.
    context = {"name": "Xuan Vinh"}
    return render(request, "movie/home.html", context)


def about(request):
    """The site's about page ('about/' in moviereviews/urls.py)."""
    context = {"name": "Xuan Vinh"}
    return render(request, "movie/about.html", context)
