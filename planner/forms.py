from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Parolă",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"})
    )
    password2 = forms.CharField(
        label="Confirmă parola",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"})
    )

    class Meta:
        model = User
        fields = ["username", "email"]
        labels = {
            "username": "Nume utilizator",
            "email": "Adresa de email"
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Există deja un cont asociat cu acest email."
            )
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # ✅ Validăm parola doar dacă există
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Parolele nu coincid.")
            validate_password(password1)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        # 🔒 Setare parolă corect
        user.set_password(self.cleaned_data["password1"])

        # 🔒 Cont inactiv până la confirmarea emailului
        user.is_active = False

        if commit:
            user.save()

        return user

