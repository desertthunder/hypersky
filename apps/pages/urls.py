"""URL Patterns for Static Pages."""

from django.urls import path

from apps.pages.views import AppView, HomePageView

urlpatterns = [
    path("app/", AppView.as_view(), name="app"),
    path("", HomePageView.as_view(), name="home"),
]
