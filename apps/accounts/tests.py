from django.test import TestCase
from django.urls import reverse_lazy


class LoginViewTests(TestCase):
    """LoginView test cases."""

    def test_template_get_view(self):
        response = self.client.get(reverse_lazy("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.dj")
        self.assertContains(response, "Login")


class RegisterViewTests(TestCase):
    """RegisterView test cases."""

    def test_template_get_view(self):
        response = self.client.get(reverse_lazy("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.dj")
        self.assertContains(response, "Register")
