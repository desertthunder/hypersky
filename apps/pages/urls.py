"""URL Patterns for Static Pages."""

from django.urls import path
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    """Home Page View."""

    template_name = "home.dj"


urlpatterns = [path("", HomePageView.as_view(), name="home")]
