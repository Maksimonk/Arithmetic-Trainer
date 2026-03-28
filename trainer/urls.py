from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("train/", views.train, name="train"),
    path("settings/", views.settings_view, name="settings"),
]

