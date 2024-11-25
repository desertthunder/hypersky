"""App pages views."""

from django import views
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse


class HomePageView(views.View):
    """Home page view."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Get request."""
        if authenticate(request):
            return redirect(reverse("app"))

        return render(request, template_name="home.dj")


class AppView(views.View, LoginRequiredMixin):
    """App page view."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Get request."""
        return render(request, template_name="app.dj")
