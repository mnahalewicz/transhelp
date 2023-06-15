from django.urls import path, include

from . import views

urlpatterns = [
    path("gaussian/", views.gaussian, name="gaussian"),
]
