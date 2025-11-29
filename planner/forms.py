from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import uuid


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Parolă",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Parolă",
            "autocomplete": "new-password"
        })
    )

    password2 = forms.CharField(
        label="Confirmă parola",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Confirmă parola",
            "autocomplete": "new-password"
        })
    )

    class Meta:
        model = User
        fields = ["email"]
        labels = {"email": "Adresa de email"}
        widgets = {
            "email": forms.EmailInput(attrs={
                "placeholder": "Adresa de email"
            })
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("Există deja un cont asociat cu acest email.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise ValidationError("Parolele nu coincid.")
            validate_password(password1)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = uuid.uuid4().hex[:30]
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False

        if commit:
            user.save()

        return user


class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "placeholder": "Adresa de email"
        })
    )

    password = forms.CharField(
        label="Parolă",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Parolă"
        })
    )

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("Email sau parolă incorectă.")

        user = authenticate(username=user.username, password=password)

        if user is None:
            raise ValidationError("Email sau parolă incorectă.")

        if not user.is_active:
            raise ValidationError("Contul nu este activ. Verifică emailul.")

        self.user = user
        return self.cleaned_data

    def get_user(self):
        return self.user

from django import forms
from .models import UserProfile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "nickname",
            "bio",
            "pronoun",
            "evening_reminder_time",
        ]

        labels = {
            "nickname": "Cum vrei să te strig?",
            "bio": "Câteva cuvinte despre tine",
            "pronoun": "Pronume",
            "evening_reminder_time": "Ora reminderului de seară",
        }

        widgets = {
            "nickname": forms.TextInput(attrs={
                "placeholder": "Deea",
            }),
            "bio": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Sunt Deea...",
            }),
            "pronoun": forms.Select(),
            "evening_reminder_time": forms.TimeInput(attrs={
                "type": "time",
            }),
        }

