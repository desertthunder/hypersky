"""Account Management Views."""

from http import HTTPStatus

from django import views
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from apps.accounts.forms import CustomUserCreationForm
from apps.libs import Logger

logger = Logger(__name__)


class LoginView(views.View):
    """Login View."""

    template_name = "login.dj"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Get request."""
        form = CustomUserCreationForm()

        return render(
            request=request,
            template_name=self.template_name,
            context={"form": form},
        )

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Post request."""
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect(reverse_lazy("app"))

        return render(
            request=request,
            template_name=self.template_name,
            context={"form": form},
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
        )
