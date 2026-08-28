"""URL configuration for the accounts app.

Included into the project via moviereviews/urls.py's
`path('accounts/', include('accounts.urls'))` - paths here are
relative to that prefix, so 'signup/' below means '/accounts/signup/'
overall. Same include() pattern news/urls.py and movie/urls.py use.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.signupaccount, name="signupaccount"),
    path("login/", views.loginuser, name="login"),
    path("logout/", views.logoutuser, name="logout"),
]
