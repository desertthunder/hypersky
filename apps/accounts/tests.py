import logging
from http import HTTPStatus
from unittest import mock

import httpx
from django import forms
from django.test import TestCase
from django.urls import reverse_lazy
from faker import Faker

from apps.accounts.forms import CustomUserCreationForm
from apps.accounts.models import Account
from apps.libs.services import BlueSkySessionResponseFactory

logging.disable(logging.CRITICAL)
fake = Faker()


class AccountManagerTests(TestCase):
    def setUp(self):
        self.response = BlueSkySessionResponseFactory.build()
        self.account = Account.objects.create(
            handle=self.response.handle,
            email=self.response.email,
            access_token=self.response.accessJwt,
            refresh_token=self.response.refreshJwt,
        )

    def test_retrieve_and_update_tokens(self):
        access = fake.sha256(raw_output=False)
        refresh = fake.sha256(raw_output=False)

        account = Account.auth.retrieve_and_update_tokens(
            email=self.account.email,
            access=access,
            refresh=refresh,
        )

        self.assertIsNotNone(account)
        self.assertEqual(account.access_token, access)
        self.assertEqual(account.refresh_token, refresh)

    def test_get_by_handle(self):
        account = Account.auth.get_by_handle(self.response.handle)

        self.assertRaises(
            Account.DoesNotExist,
            Account.auth.get_by_handle,
            handle=fake.user_name(),
        )
        self.assertIsNotNone(account)
        self.assertEqual(account.handle, self.response.handle)

    def test_get_by_email(self):
        account = Account.auth.get_by_email(self.response.email)

        self.assertRaises(
            Account.DoesNotExist,
            Account.auth.get_by_email,
            email=fake.email(),
        )
        self.assertIsNotNone(account)
        self.assertEqual(account.email, self.response.email)

    def test_create_from_api(self):
        response = BlueSkySessionResponseFactory.build()

        account = Account.auth.create_from_api(
            email=response.email,
            handle=response.handle,
            access=response.accessJwt,
            refresh=response.refreshJwt,
        )

        self.assertIsNotNone(account)
        self.assertEqual(account.email, response.email)
        self.assertEqual(account.handle, response.handle)
        self.assertEqual(account.access_token, response.accessJwt)
        self.assertEqual(account.refresh_token, response.refreshJwt)


class AccountTests(TestCase):
    def setUp(self):
        self.response = BlueSkySessionResponseFactory.build()
        self.account = Account.objects.create(
            handle=self.response.handle,
            email=self.response.email,
            access_token=self.response.accessJwt,
            refresh_token=self.response.refreshJwt,
        )

    def test_update_tokens(self):
        access = fake.sha256(raw_output=False)
        refresh = fake.sha256(raw_output=False)

        self.account.update_tokens(access, refresh)
        self.account.refresh_from_db()

        self.assertEqual(self.account.access_token, access)
        self.assertEqual(self.account.refresh_token, refresh)


class LoginFormTests(TestCase):
    def setUp(self):
        self.response = BlueSkySessionResponseFactory.build()
        self.email = self.response.email
        self.handle = self.response.handle
        self.password = fake.password()

    def test_validate_methods(self):
        self.assertRaises(
            forms.ValidationError,
            CustomUserCreationForm.validate_handle,
            handle="",
        )

        self.assertRaises(
            forms.ValidationError,
            CustomUserCreationForm.validate_password,
            password="",
        )

    @mock.patch("apps.libs.BlueSkyService.get_user_jwt")
    def test_save(self, mock_get_user_jwt: mock.MagicMock):
        mock_get_user_jwt.return_value = self.response
        form = CustomUserCreationForm(
            data={
                "handle": self.handle,
                "password": self.password,
            }
        )

        form.save()

        account = Account.objects.get(email=self.email)

        self.assertIsNotNone(account)
        self.assertEqual(account.email, self.email)
        self.assertEqual(account.handle, self.handle)
        self.assertEqual(account.access_token, self.response.accessJwt)
        self.assertEqual(account.refresh_token, self.response.refreshJwt)

    def test_save_invalid_form(self):
        form = CustomUserCreationForm(
            data={
                "handle": "",
                "password": "",
            }
        )

        self.assertRaises(forms.ValidationError, form.save)

    @mock.patch("httpx.post")
    def test_save_http_error(self, mock_post: mock.MagicMock):
        mock_post.return_value = httpx.Response(
            status_code=HTTPStatus.BAD_REQUEST,
            request=httpx.Request("POST", fake.url()),
            json={"error": "Bad Request"},
        )

        form = CustomUserCreationForm(
            data={
                "handle": self.handle,
                "password": self.password,
            }
        )

        self.assertRaises(forms.ValidationError, form.save)

    @mock.patch("apps.libs.BlueSkyService.get_user_jwt")
    def test_login(self, mock_get_user_jwt: mock.MagicMock):
        account = Account.objects.create(
            handle=fake.user_name(),
            email=fake.email(),
            access_token=str(fake.sha256(raw_output=False)),
            refresh_token=str(fake.sha256(raw_output=False)),
        )

        mock_get_user_jwt.return_value = BlueSkySessionResponseFactory.build(
            email=account.email, handle=account.handle
        )

        form = CustomUserCreationForm(
            data={
                "handle": account.handle,
                "password": self.password,
            }
        )

        form.save()

        self.assertEqual(Account.objects.last(), account)


class LoginViewTests(TestCase):
    """LoginView test cases."""

    def setUp(self):
        """Setup the test cases."""
        self.session = BlueSkySessionResponseFactory.build()
        self.user = Account.auth.create_from_api(
            email=self.session.email,
            handle=self.session.handle,
            access=self.session.accessJwt,
            refresh=self.session.refreshJwt,
        )

    def test_get_view(self):
        response = self.client.get(reverse_lazy("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.dj")
        self.assertContains(response, "Login")

    @mock.patch("apps.libs.BlueSkyService.get_user_jwt")
    def test_post_view_error(self, mock_get_user_jwt: mock.MagicMock):
        mock_get_user_jwt.return_value = self.session
        response = self.client.post(reverse_lazy("login"))
        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    @mock.patch("apps.libs.BlueSkyService.get_user_jwt")
    def test_post_view(self, mock_get_user_jwt: mock.MagicMock):
        mock_get_user_jwt.return_value = self.session
        response = self.client.post(
            reverse_lazy("login"),
            data={
                "handle": self.user.handle,
                "password": fake.password(),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy("app"))
