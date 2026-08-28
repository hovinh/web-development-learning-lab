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
from django.urls import path

from movie import views as movieViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', movieViews.home),
    path('about/', movieViews.about),
    # name='signup' lets templates link/submit to this URL with
    # {% url 'signup' %} instead of hard-coding the path - see the
    # mailing-list form's `action` in movie/templates/movie/home.html.
    path('signup/', movieViews.signup, name='signup'),
]

# Only wired up when DEBUG=True (local dev) - see MEDIA_URL/MEDIA_ROOT
# in settings.py. Without this, uploaded Movie.image files would save
# to disk fine but 404 when a template tries to display them.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
