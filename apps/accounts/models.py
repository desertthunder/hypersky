"""Custom user model."""

import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    UserManager,
)
from django.db import models
from django_stubs_ext.db.models import TypedModelMeta


class UUIDModel(models.Model):
    """UUID model mixin."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    class Meta(TypedModelMeta):
        """Meta class for UUIDModel."""

        abstract = True


class AccountManager(BaseUserManager["Account"]):
    """Account manager cls."""

    def retrieve_and_update_tokens(
        self,
        email: str,
        access: str,
        refresh: str,
    ) -> "Account":
        """Retrieve and update tokens."""
        account = self.get_by_email(email)
        account.access_token = access
        account.refresh_token = refresh
        account.save()
        account.refresh_from_db()

        return account

    def get_by_handle(self, handle: str) -> "Account":
        """Retrieve account by handle."""
        if account := self.filter(handle=handle).first():
            return account

        raise self.model.DoesNotExist(f"Account with handle {handle} does not exist.")

    def get_by_email(self, email: str) -> "Account":
        """Retrieve account by email."""
        if account := self.filter(email=email).first():
            return account

        raise self.model.DoesNotExist(f"Account with email {email} does not exist.")

    def create_from_api(
        self, email: str, handle: str, access: str, refresh: str
    ) -> "Account":
        """Create account from API."""
        return self.create(
            email=email,
            handle=handle,
            access_token=access,
            refresh_token=refresh,
        )


class Account(AbstractBaseUser, PermissionsMixin, UUIDModel):
    """BlueSky Account SQL representation."""

    email = models.EmailField(unique=True)
    handle = models.CharField(max_length=40, unique=True)
    access_token = models.CharField(max_length=255, blank=True)
    refresh_token = models.CharField(max_length=255, blank=True)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["handle"]

    objects = UserManager()
    auth: AccountManager = AccountManager()

    def update_tokens(self, access: str, refresh: str) -> None:
        """Update access and refresh tokens."""
        self.access_token = access
        self.refresh_token = refresh
        self.save()

        self.refresh_from_db()
