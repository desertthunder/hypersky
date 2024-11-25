"""Custom user model."""

import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
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


class Account(AbstractBaseUser, PermissionsMixin, UUIDModel):
    """BlueSky Account SQL representation."""

    email = models.EmailField(unique=True)
    handle = models.CharField(max_length=40, unique=True)
    token = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, help_text="App password")

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["handle"]

    objects = BaseUserManager()
