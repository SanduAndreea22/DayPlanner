"""
Django settings for Emotional Planner.
Django 5.2.x
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# ====================================================
# 🔧 BASE
# ====================================================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

# ====================================================
# 🔐 SECURITY
# ====================================================
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "dev-secret-key-for-local-and-tests"
)

DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# ====================================================
# 📦 APPLICATIONS
# ====================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "planner",
]

# ====================================================
# 🧱 MIDDLEWARE
# ====================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ====================================================
# 🌍 URL / WSGI
# ====================================================
ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"

# ====================================================
# 🎨 TEMPLATES
# ====================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ====================================================
# 🗄 DATABASE
# ====================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ====================================================
# 🔑 PASSWORD VALIDATION
# ====================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ====================================================
# 🌐 I18N / TIME
# ====================================================
LANGUAGE_CODE = "ro"
TIME_ZONE = "Europe/Bucharest"
USE_I18N = True
USE_TZ = True

# ====================================================
# 📁 STATIC FILES
# ====================================================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# ====================================================
# ✉️ EMAIL (DEV + PROD READY)
# ====================================================
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
#EMAIL_HOST = "smtp-relay.brevo.com"
#EMAIL_PORT = 587
#EMAIL_USE_TLS = True

#EMAIL_HOST_USER = "apikey"
#EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

#DEFAULT_FROM_EMAIL = "Emotional Planner <emotional.planner.app@gmail.com>"
