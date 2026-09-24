"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # django.contrib.auth.urls wires up login/, logout/, password-change/,
    # etc. with built-in views - this is the "auth is free" claim the
    # blog makes, tested against demos/labeling-fastapi-react/api's
    # hand-rolled JWT endpoints. Only login/logout are actually used
    # here (see labeling/templates/registration/login.html); the rest
    # come along for free and are simply unlinked.
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('labeling.urls')),
]
