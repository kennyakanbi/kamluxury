import os
from pathlib import Path
from datetime import timedelta
from django.core.management.utils import get_random_secret_key
import dj_database_url
from decouple import config as env  # type: ignore

# -------------------------------------------------------------------
# BASE SETTINGS
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------
# ENVIRONMENT VARIABLES
# -------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY", default=get_random_secret_key())
DEBUG = env("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = env("ALLOWED_HOSTS", default="kamluxury.onrender.com,localhost,127.0.0.1").split(",")

# -------------------------------------------------------------------
# APPLICATIONS
# -------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "whitenoise.runserver_nostatic",
    "django_bootstrap5",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_filters",
    "cloudinary",
    "cloudinary_storage",
    "listings",
    "checkout",
    "django.contrib.humanize",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = ["bootstrap5"]
CRISPY_TEMPLATE_PACK = "bootstrap5"

# -------------------------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# -------------------------------------------------------------------
# URL CONFIGURATION
# -------------------------------------------------------------------
ROOT_URLCONF = "config.urls"

# -------------------------------------------------------------------
# TEMPLATES
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# WSGI
# -------------------------------------------------------------------
WSGI_APPLICATION = "config.wsgi.application"

# -------------------------------------------------------------------
# DATABASE
# -------------------------------------------------------------------
if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": dj_database_url.config(default=env("DATABASE_URL"))
    }


# -------------------------------------------------------------------
# PASSWORD VALIDATION
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------------------------------------------
# INTERNATIONALIZATION
# -------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# STATIC & MEDIA FILES
# -------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------------------------------------------------------
# MEDIA / CLOUDINARY CONFIGURATION
# -------------------------------------------------------------------
import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "dzfzcm1nt"),
    api_key=os.getenv("CLOUDINARY_API_KEY", "498946834664268"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
)

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dzfzcm1nt',
    'API_KEY': '498946834664268',
    'API_SECRET': '8FQf9O9kdjDJFZQxol8woOJr4Ww'
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
MEDIA_URL = '/media/'



# DEFAULT PRIMARY KEY FIELD TYPE
# -------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------------------------------------------------
# EMAIL CONFIG
# -------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = env("ADMIN_EMAIL", default="admin@example.com")

# -------------------------------------------------------------------
# ADMIN CONFIG
# -------------------------------------------------------------------
ADMIN_USER = env("ADMIN_USER", default="")
ADMIN_PASS = env("ADMIN_PASS", default="")
ADMIN_EMAIL = env("ADMIN_EMAIL", default="")

# -------------------------------------------------------------------
# SECURITY SETTINGS
# -------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
    "http://127.0.0.1",
    "http://localhost",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# -------------------------------------------------------------------
# LOGGING
# -------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
