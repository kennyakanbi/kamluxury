# config/settings.py — cleaned for Render deployment

import os
from pathlib import Path
import environ  # type: ignore
import dj_database_url

# Load environment variables from .env (development)
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(BASE_DIR / ".env")

# Security / secrets
SECRET_KEY = env("SECRET_KEY", default="dev-secret-key")
DEBUG = env.bool("DEBUG", default=True)

# ALLOWED_HOSTS: read from env or use sensible defaults (include Render wildcard)
# Provide comma separated values in env if you want multiple hosts.
default_hosts = ["localhost", "127.0.0.1", "kamluxng.onrender.com"]
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=default_hosts)

INSTALLED_APPS = [
    "django.contrib.humanize",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_bootstrap5",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_filters",
    "listings",
    "checkout",
]

# Crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = ["bootstrap5"]
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serve static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- DATABASE configuration (robust for Render) ---
import os
from urllib.parse import urlparse

DATABASE_URL = os.environ.get("DATABASE_URL", "") or ""

def is_valid_db_url(url: str) -> bool:
    # quick check: non-empty and contains a scheme (like 'postgres://' or 'sqlite:///')
    if not url:
        return False
    parsed = urlparse(url)
    return bool(parsed.scheme) and parsed.scheme != ""

if is_valid_db_url(DATABASE_URL):
    # dj_database_url.parse expects a normal URL like "postgres://..."
    try:
        DATABASES = {
            "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
        }
    except Exception:
        # If parsing fails, fall back to sqlite instead of crashing
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }
else:
    # Fallback to local sqlite for development or when DATABASE_URL not set / invalid
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
# --- end DATABASE block ---

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

# ---------------- MEDIA FILES ----------------
# Use local filesystem in development, S3 in production
if DEBUG:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"
else:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    # Expect the following env var(s) to be set when using S3:
    AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", default="")
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/" if AWS_S3_CUSTOM_DOMAIN else "/media/"
    AWS_QUERYSTRING_AUTH = False
# ------------------------------------------------

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AWS_QUERYSTRING_AUTH = False  # So URLs are public without signed querystrings

# Payments & WhatsApp
PAYSTACK_PUBLIC_KEY = env("PAYSTACK_PUBLIC_KEY", default="")
PAYSTACK_SECRET_KEY = env("PAYSTACK_SECRET_KEY", default="")
CURRENCY = "NGN"
WHATSAPP_NUMBER = env("WHATSAPP_NUMBER", default="2347036067548")

# ----- Proxy / security helpers -----
# Trust the X-Forwarded-Proto header that platforms like Render set
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Read security flags from env (set to True in production)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=False)
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
# -------------------------------------

# Only call django_heroku.settings when DATABASE_URL exists (Heroku helper)
# and wrap in try/except so a missing package or other error won't break startup.
try:
    if DATABASE_URL:
        import django_heroku  # type: ignore
        django_heroku.settings(locals())
except Exception:
    # Don't crash the app if django_heroku is not available or misbehaves.
    pass
