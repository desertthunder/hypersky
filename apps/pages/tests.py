from django.test import TestCase
from django.urls import reverse_lazy


class PagesViewsTestCase(TestCase):
    """Test cases for the Pages app views."""

    def test_home_page(self):
        """Test the home page view."""
        path = reverse_lazy("home")
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.dj")
        self.assertContains(response, "Hypersky")
