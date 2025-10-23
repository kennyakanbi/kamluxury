# config/settings.py  — clean settings tuned for Render
import os
from pathlib import Path
from urllib.parse import urlparse

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Simple env helpers
def env_bool(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "on")

def env_list(name: str, default: list[str]) -> list[str]:
    v = os.environ.get(name)
    if not v:
        return default
    # comma separated
    return [x.strip() for x in v.split(",") if x.strip()]

# ---------------- Security / debug ----------------
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
DEBUG = env_bool("DEBUG", True)

# Default allowed hosts — override with ALLOWED_HOSTS env (comma separated)
DEFAULT_HOSTS = ["localhost", "127.0.0.1", "kamluxng.onrender.com"]
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", DEFAULT_HOSTS)

# ---------------- Installed apps / middleware ----------------
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

# ---------------- Database ----------------
# Render will provide a DATABASE_URL for Postgres; otherwise fallback to sqlite for dev.
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

def use_sqlite_fallback():
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }

if DATABASE_URL:
    try:
        # require ssl when Postgres on managed hosts (let dj_database_url handle parsing)
        # For local testing you might pass sqlite:///... which dj_database_url will parse too.
        DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
        # If dj_database_url returned an engineless dict for bad value, fallback:
        if not DATABASES["default"].get("ENGINE"):
            DATABASES["default"] = use_sqlite_fallback()
    except Exception:
        DATABASES = {"default": use_sqlite_fallback()}
else:
    DATABASES = {"default": use_sqlite_fallback()}

# ---------------- Password validation / i18n ----------------
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

# ---------------- Media ----------------
# Local filesystem for DEBUG; when not DEBUG expect S3 settings to be present.
if DEBUG:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"
else:
    DEFAULT_FILE_STORAGE = os.environ.get(
        "DEFAULT_FILE_STORAGE", "storages.backends.s3boto3.S3Boto3Storage"
    )
    AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN", "")
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/" if AWS_S3_CUSTOM_DOMAIN else "/media/"
    AWS_QUERYSTRING_AUTH = False

# ---------------- Static files ----------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
# Whitenoise manifest storage for production (keeps hashed filenames)
STATICFILES_STORAGE = os.environ.get(
    "STATICFILES_STORAGE", "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------- Third party / App config ----------------
AWS_QUERYSTRING_AUTH = False
PAYSTACK_PUBLIC_KEY = os.environ.get("PAYSTACK_PUBLIC_KEY", "")
PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY", "")
CURRENCY = os.environ.get("CURRENCY", "NGN")
WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER", "2347036067548")

# ---------------- Security / proxy helpers ----------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", False)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", False)
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", False)

# ---------------- Optional helpers for deployment platforms ----------------
# If you use django_heroku on Heroku-like platforms, keep invocation optional
try:
    if DATABASE_URL and "heroku" in os.environ.get("PLATFORM", ""):
        import django_heroku  # type: ignore
        django_heroku.settings(locals())
except Exception:
    pass

# --------------- End of file ---------------
