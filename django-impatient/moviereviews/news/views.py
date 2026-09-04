from django.shortcuts import render

from .models import News


def index(request):
    """The news listing page ('' under news/urls.py's include('news.urls'),
    reachable at '/news/' - see moviereviews/urls.py).
    """
    # order_by('-date') puts the most recent story first (the '-'
    # reverses the sort). Written explicitly here rather than relying
    # solely on News.Meta.ordering in models.py, so this view's "most
    # recent first" requirement is visible at the call site too.
    news_list = News.objects.order_by("-date")
    return render(request, "news/index.html", {"news_list": news_list})
