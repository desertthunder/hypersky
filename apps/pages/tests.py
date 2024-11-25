import logging
from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse_lazy
from faker import Faker

from apps.accounts.models import Account

fake = Faker()

logging.disable(logging.CRITICAL)


class PagesViewsTestCase(TestCase):
    """Test cases for the Pages app views."""

    def setUp(self):
        """Setup the test cases."""
        self.user = Account.auth.create_from_api(
            email=fake.email(),
            handle=fake.user_name(),
            access=fake.sha256(raw_output=False),
            refresh=fake.sha256(raw_output=False),
        )

    def test_unauthenticated_home_page(self):
        """Test the home page view."""
        path = reverse_lazy("home")
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.dj")
        self.assertContains(response, "Hypersky")

    def test_home_redirect_authenticated(self):
        path = reverse_lazy("home")
        response = self.client.get(
            path,
            headers={"Authorization": f"Bearer {self.user.access_token}"},
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_authenticated_app_page(self):
        """Test the home page view."""
        path = reverse_lazy("app")
        response = self.client.get(
            path,
            headers={"Authorization": f"Bearer {self.user.access_token}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app.dj")
        self.assertContains(response, "Hypersky")
