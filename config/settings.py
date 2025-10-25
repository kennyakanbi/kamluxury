import os
from pathlib import Path
from datetime import timedelta
from django.core.management.utils import get_random_secret_key
import dj_database_url
from decouple import config  # type: ignore # ✅ correct import



# -------------------------------------------------------------------
# BASE SETTINGS
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------
# ENVIRONMENT VARIABLES
# -------------------------------------------------------------------
from decouple import config as env # pyright: ignore[reportMissingImports]

SECRET_KEY = env("SECRET_KEY", default=get_random_secret_key())
DEBUG = env("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = env("ALLOWED_HOSTS", default="*").split(",")

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
    'django.contrib.humanize',  
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
# Render provides DATABASE_URL automatically

DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://kamluxng_db_user:jznfj0Gi3uWXwti0DkAEj3SmKRUnxOyj@dpg-d3udajogjchc73a8f0ag-a/kamluxng_db'
    )
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
# Local filesystem by default (Render free-friendly)
USE_S3 = env("USE_S3", default=False, cast=bool)

if USE_S3:
    # If you later enable S3
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", default="")
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/" if AWS_S3_CUSTOM_DOMAIN else "/media/"
    AWS_QUERYSTRING_AUTH = False
else:
    # Local file uploads (default)
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Whitenoise handles static files nicely for Render
STATICFILES_STORAGE = env(
    "STATICFILES_STORAGE",
    default="whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# -------------------------------------------------------------------
# DEFAULT PRIMARY KEY FIELD TYPE
# -------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------------------------------------------------
# EMAIL CONFIG (optional)
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
# LOGGING (Optional but helpful)
# -------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
