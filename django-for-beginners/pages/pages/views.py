from django.shortcuts import render


def home(request):
    # render() loads the named template, fills it in with the context
    # dict, and wraps the result in an HttpResponse - the three steps
    # every simple view needs (see the "Views" section of
    # django-for-beginners/README.md).
    return render(request, 'pages/home.html')


def about(request):
    return render(request, 'pages/about.html')
