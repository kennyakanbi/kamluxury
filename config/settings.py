# config/settings.py — tuned for Render (production-safe defaults + helpful comments)
import os
from pathlib import Path
from typing import Any
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------- helpers -------------------
def env_bool(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "on")

def env_list(name: str, default: list[str]) -> list[str]:
    v = os.environ.get(name)
    if not v:
        return default
    return [x.strip() for x in v.split(",") if x.strip()]

def env_str(name: str, default: str = "") -> str:
    return os.environ.get(name, default)

# ---------------- Security / debug ----------------
# IMPORTANT: ensure SECRET_KEY is set as an environment variable in Render for production.
SECRET_KEY = env_str("SECRET_KEY", "dev-secret-key")

# Default to False for safety; enable DEBUG explicitly with DEBUG=1 in your dev env
DEBUG = env_bool("DEBUG", False)

# ---------------- Hosts ----------------
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

    # third-party
    "django_bootstrap5",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_filters",

    # local apps
    "listings",
    "checkout",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = ["bootstrap5"]
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serve static files efficiently
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
# Use Render's DATABASE_URL if provided; fallback to sqlite for dev/test.
DATABASE_URL = env_str("DATABASE_URL", "").strip()

def use_sqlite_fallback() -> dict[str, Any]:
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "db.sqlite3"),
    }

if DATABASE_URL:
    try:
        # parse with a sensible conn_max_age for connection reuse
        DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
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
# Local filesystem for DEBUG; in production expect S3/backed storage
if DEBUG:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"
else:
    DEFAULT_FILE_STORAGE = env_str("DEFAULT_FILE_STORAGE", "storages.backends.s3boto3.S3Boto3Storage")
    AWS_S3_CUSTOM_DOMAIN = env_str("AWS_S3_CUSTOM_DOMAIN", "")
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/" if AWS_S3_CUSTOM_DOMAIN else "/media/"
    AWS_QUERYSTRING_AUTH = False

# ---------------- Static files ----------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Use whitenoise compressed manifest storage by default in production (keeps hashed filenames)
STATICFILES_STORAGE = env_str(
    "STATICFILES_STORAGE",
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------- App / third-party config ----------------
AWS_QUERYSTRING_AUTH = False
PAYSTACK_PUBLIC_KEY = env_str("PAYSTACK_PUBLIC_KEY", "")
PAYSTACK_SECRET_KEY = env_str("PAYSTACK_SECRET_KEY", "")
CURRENCY = env_str("CURRENCY", "NGN")
WHATSAPP_NUMBER = env_str("WHATSAPP_NUMBER", "2347036067548")

# ---------------- Security / cookie settings ----------------
# Enforce cookie security in production
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # Django's CSRF cookie is accessed by client-side JS in some integrations; leave False unless you know otherwise
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", not DEBUG)
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", not DEBUG)

# HSTS — only enable when you're sure the site is served over HTTPS
if not DEBUG and env_bool("SECURE_HSTS_ENABLED", True):
    SECURE_HSTS_SECONDS = int(env_str("SECURE_HSTS_SECONDS", "31536000"))  # 1 year by default
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
    SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", True)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ---------------- Logging (minimal) ----------------
# Send errors to stdout so Render captures them
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "standard"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

# ---------------- Optional helpers for deployment platforms ----------------
# Support optional django_heroku integration only when PLATFORM env explicitly sets it
try:
    if DATABASE_URL and "heroku" in os.environ.get("PLATFORM", ""):
        import django_heroku  # type: ignore
        django_heroku.settings(locals())
except Exception:
    pass

# --------------- End of file ---------------
