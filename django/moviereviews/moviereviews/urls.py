"""
URL configuration for moviereviews project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from movie import views as movieViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', movieViews.home),
    path('about/', movieViews.about),
    # name='signup' lets templates link/submit to this URL with
    # {% url 'signup' %} instead of hard-coding the path - see the
    # mailing-list form's `action` in movie/templates/movie/home.html.
    path('signup/', movieViews.signup, name='signup'),
    # include() hands everything under 'news/' off to news/urls.py's
    # own urlpatterns, instead of listing news's routes here directly
    # (the way movie's are above) - keeps each app's routing table in
    # that app's own folder as the project grows.
    path('news/', include('news.urls')),
    # movie's detail page uses the same include() pattern - see
    # movie/urls.py. home/about/signup above predate this file and stay
    # where they are rather than being moved, just to avoid churn.
    path('movie/', include('movie.urls')),
    # accounts/urls.py's own 'signup/' route ends up at
    # '/accounts/signup/', named 'signupaccount' - deliberately
    # different from this file's own name='signup' above (the movie
    # app's mailing-list form), which is an unrelated route that just
    # happens to share the word "signup".
    path('accounts/', include('accounts.urls')),
]

# Only wired up when DEBUG=True (local dev) - see MEDIA_URL/MEDIA_ROOT
# in settings.py. Without this, uploaded Movie.image files would save
# to disk fine but 404 when a template tries to display them.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
