from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("train/", views.train, name="train"),
    path("history/", views.history, name="history"),
    path("stats/", views.stats, name="stats"),
    path("settings/", views.settings_view, name="settings"),
]

