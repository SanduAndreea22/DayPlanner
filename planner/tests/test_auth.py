from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="test@example.com",
    ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"],
)
class AuthFlowTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_sends_confirmation_email(self):
        response = self.client.post(
            reverse("register"),
            {
                "email": "alice@example.com",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "planner/auth/check_email.html")
        self.assertEqual(len(mail.outbox), 1)

    def test_activate_account(self):
        user = User.objects.create_user(
            username="ana",
            email="ana@example.com",
            password="ComplexPass123!",
            is_active=False,
        )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.get(reverse("activate", args=[uid, token]))

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTemplateUsed(response, "planner/auth/email_confirm_success.html")

    def test_login_logout_flow(self):
        user = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="ComplexPass123!",
        )

        response = self.client.post(
            reverse("login"),
            {"email": "bob@example.com", "password": "ComplexPass123!"},
        )

        self.assertRedirects(response, reverse("today"))

        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("home"))
