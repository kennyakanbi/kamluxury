from pathlib import Path
import os
from decouple import config as env
import dj_database_url
from django.core.management.utils import get_random_secret_key
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------
# MEDIA / CLOUDINARY setup
# ------------------------


MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", str(BASE_DIR / "media")))

# default to local storage
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

CLOUDINARY_URL = os.getenv("CLOUDINARY_URL") or None
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME") or None
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY") or None
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET") or None

if CLOUDINARY_URL:
    # parse CLOUDINARY_URL like: cloudinary://API_KEY:API_SECRET@CLOUD_NAME
    parsed = urlparse(CLOUDINARY_URL)
    # parsed.hostname is the cloud name for cloudinary://...@CLOUD_NAME
    parsed_cloud = parsed.hostname or CLOUDINARY_CLOUD_NAME

    CLOUDINARY_CLOUD_NAME = CLOUDINARY_CLOUD_NAME or parsed_cloud
    # try to fill api key/secret from URL if not provided separately
    if parsed.username and not CLOUDINARY_API_KEY:
        CLOUDINARY_API_KEY = parsed.username
    if parsed.password and not CLOUDINARY_API_SECRET:
        CLOUDINARY_API_SECRET = parsed.password

if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    # Enable Cloudinary storage
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
        "API_KEY": CLOUDINARY_API_KEY,
        "API_SECRET": CLOUDINARY_API_SECRET,
    }
    # Helpful MEDIA_URL pointing to Cloudinary upload base (templates typically use field.url though)
    MEDIA_URL = f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/upload/"
else:
    # local development fallback
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

# ------------------------
# STATIC FILES CONFIGURATION
# ------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Optional: for local dev
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# security / env
SECRET_KEY = env("SECRET_KEY", default=get_random_secret_key())
DEBUG = env("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = env("ALLOWED_HOSTS", default="kamluxng.onrender.com,localhost,127.0.0.1").split(",")

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
    "listings",
    "checkout",
     "cloudinary",
    "cloudinary_storage",
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

ADMIN_USER = env("ADMIN_USER", default="")
ADMIN_PASS = env("ADMIN_PASS", default="")
ADMIN_EMAIL = env("ADMIN_EMAIL", default="")



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





