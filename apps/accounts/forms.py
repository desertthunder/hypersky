"""Account Management Forms."""

import json

import httpx
from django import forms

from apps.accounts.models import Account
from apps.libs import BLUESKY, Logger

logger = Logger(__name__)


class CustomUserCreationForm(forms.Form):
    """User creation form."""

    @staticmethod
    def validate_handle(handle: str) -> None:
        """Validate handle."""
        if len(handle) == 0:
            raise forms.ValidationError("Handle is required.")

    @staticmethod
    def validate_password(password: str) -> None:
        """Validate password."""
        if len(password) == 0:
            raise forms.ValidationError("Password is required.")

    handle = forms.CharField(max_length=100, validators=[validate_handle])
    password = forms.CharField(max_length=100, validators=[validate_password])

    def save(self) -> None:
        """Save user."""
        if not self.is_valid():
            raise forms.ValidationError("Form is not valid.")

        handle = self.cleaned_data["handle"]
        password = self.cleaned_data["password"]

        try:
            resp = BLUESKY.get_user_jwt(handle, password)
            account, created = Account.objects.update_or_create(
                handle=resp.handle,
                email=resp.email,
                defaults={
                    "access_token": resp.accessJwt,
                    "refresh_token": resp.refreshJwt,
                },
            )

            if created:
                logger.info(f"User created: {account.id}")
            else:
                logger.info(f"User already exists: {account.id}")
        except httpx.HTTPStatusError as exc:
            data = exc.response.json()
            logger.error(f"Error creating user: {json.dumps(data, indent=2)}")
            raise forms.ValidationError(data) from exc
