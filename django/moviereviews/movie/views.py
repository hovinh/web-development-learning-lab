from django.http import HttpResponse

# Create your views here.


def home(request):
    """The site's landing page ('' in moviereviews/urls.py)."""
    return HttpResponse("Welcome to Home Page")


def about(request):
    """The site's about page ('about/' in moviereviews/urls.py)."""
    return HttpResponse("Welcome to About Page")
