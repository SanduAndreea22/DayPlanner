from datetime import date

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import Day


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
                "username": "alice",
                "email": "alice@example.com",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "planner/auth/check_email.html")
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertEqual(email.to, ["alice@example.com"])
        self.assertIn("http://testserver/activate/", email.body)
        self.assertTrue(
            any("http://testserver/activate/" in alt[0] for alt in email.alternatives)
        )

    def test_activate_account_marks_user_active(self):
        user = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="ComplexPass123!",
            is_active=False,
        )
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        response = self.client.get(reverse("activate", args=[uidb64, token]))

        self.assertTemplateUsed(response, "planner/auth/email_confirm_success.html")
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_activate_account_invalid_token(self):
        user = User.objects.create_user(
            username="carol",
            email="carol@example.com",
            password="ComplexPass123!",
            is_active=False,
        )
        bad_token = default_token_generator.make_token(user) + "x"
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        response = self.client.get(reverse("activate", args=[uidb64, bad_token]))

        self.assertTemplateUsed(response, "planner/auth/email_confirm_invalid.html")
        user.refresh_from_db()
        self.assertFalse(user.is_active)


@override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])
class DayViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="dana",
            email="dana@example.com",
            password="ComplexPass123!",
        )
        self.day = Day.objects.create(user=self.user, date=date.today())
        self.client = Client()
        self.client.force_login(self.user)

    def test_update_day_notes(self):
        response = self.client.post(
            reverse("update_day_text"),
            {"day_id": self.day.id, "notes": "A meaningful note"},
        )

        self.assertEqual(response.status_code, 302)
        self.day.refresh_from_db()
        self.assertEqual(self.day.notes, "A meaningful note")

    def test_mood_chart_template_exists(self):
        response = self.client.get(reverse("mood_chart"))
        self.assertTemplateUsed(response, "planner/chart/mood.html")

    def test_productivity_chart_template_exists(self):
        response = self.client.get(reverse("productivity_chart"))
        self.assertTemplateUsed(response, "planner/chart/productivity.html")

