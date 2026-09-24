from django.urls import path

from . import views

urlpatterns = [
    path("", views.queue, name="queue"),
    path("<int:item_id>/", views.label_item, name="label-item"),
]
