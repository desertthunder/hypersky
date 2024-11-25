import logging
from unittest import mock

import httpx
from django.test import RequestFactory, TestCase
from django.urls import reverse_lazy
from faker import Faker

from apps.accounts.models import Account
from apps.libs.authentication import BlueSkyJWTBackend
from apps.libs.services import BlueSkySessionResponseFactory

fake = Faker()
logging.disable(logging.CRITICAL)


class JWTBackendTestCase(TestCase):
    def setUp(self):
        self.backend = BlueSkyJWTBackend()
        self.access_token = fake.sha256(raw_output=False)
        self.refresh_token = fake.sha256(raw_output=False)
        self.user = Account.auth.create_from_api(
            email=fake.email(),
            handle=fake.user_name(),
            access=self.access_token,
            refresh=self.refresh_token,
        )

        self.request_factory = RequestFactory()

    def test_authenticate(self):
        path = reverse_lazy("home")
        request = self.request_factory.post(
            path,
            headers={"Authorization": f"Bearer {self.user.access_token}"},
        )
        backend = BlueSkyJWTBackend()
        result = backend.authenticate(request)

        self.assertEqual(result, self.user)

    def test_authenticate_no_request(self):
        backend = BlueSkyJWTBackend()
        result = backend.authenticate()

        self.assertIsNone(result)

    @mock.patch("apps.libs.services.BlueSkyService.get_user_jwt")
    def test_update_tokens(self, mock_get_user_jwt: mock.MagicMock):
        response = BlueSkySessionResponseFactory.build(email=self.user.email)
        mock_get_user_jwt.return_value = response

        request = self.request_factory.post(
            reverse_lazy("home"),
            data={
                "identifier": self.user.email,
                "password": fake.password(),
            },
        )

        if result := self.backend.authenticate(request):
            self.assertEqual(result, self.user)
            self.assertIsNotNone(result)
            self.assertNotEqual(result.access_token, self.access_token)
            self.assertNotEqual(result.refresh_token, self.refresh_token)
            self.assertEqual(result.access_token, response.accessJwt)
            self.assertEqual(result.refresh_token, response.refreshJwt)
        else:
            self.fail("User not authenticated")

    @mock.patch("apps.libs.services.BlueSkyService.get_user_jwt")
    def test_create_account(self, mock_get_user_jwt: mock.MagicMock):
        response = BlueSkySessionResponseFactory.build(email=fake.email())
        mock_get_user_jwt.return_value = response
        accounts_count = Account.objects.count()
        request = self.request_factory.post(
            reverse_lazy("home"),
            data={"identifier": fake.email(), "password": fake.password()},
        )

        if result := self.backend.authenticate(request):
            self.assertEqual(Account.objects.count(), accounts_count + 1)
            self.assertEqual(result.email, response.email)
            self.assertEqual(result.handle, response.handle)
            self.assertEqual(result.access_token, response.accessJwt)
            self.assertEqual(result.refresh_token, response.refreshJwt)
        else:
            self.fail("User not authenticated")

    @mock.patch("httpx.post")
    def test_authentication_error(self, mock_post: mock.MagicMock):
        mock_post.return_value = httpx.Response(
            status_code=fake.random_int(400, 599),
            request=httpx.Request("POST", fake.url()),
        )

        request = self.request_factory.post(
            reverse_lazy("home"),
            data={"identifier": fake.email(), "password": fake.password()},
        )

        result = self.backend.authenticate(request)
        self.assertIsNone(result)
