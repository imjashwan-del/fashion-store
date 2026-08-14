"""
Django settings for fashion_store project.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# SECURITY
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-demo-prototype-key-change-before-production",
)

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = [
    "fashion-store-vdud.onrender.com",
    "localhost",
    "127.0.0.1",
]

# ---------------------------------------------------------------------------
# APPLICATIONS
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "store",
]

# ---------------------------------------------------------------------------
# MIDDLEWARE
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# URLS
# ---------------------------------------------------------------------------
ROOT_URLCONF = "fashion_store.urls"

# ---------------------------------------------------------------------------
# TEMPLATES
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "store" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "store.context_processors.store_config",
                "store.context_processors.cart_count",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# WSGI
# ---------------------------------------------------------------------------
WSGI_APPLICATION = "fashion_store.wsgi.application"

# ---------------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ---------------------------------------------------------------------------
# PASSWORD VALIDATION
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ---------------------------------------------------------------------------
# INTERNATIONALIZATION
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# STATIC FILES
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "store" / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ---------------------------------------------------------------------------
# MEDIA FILES
# ---------------------------------------------------------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# DEFAULT PRIMARY KEY
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------------------------
LOGIN_URL = "/admin-dashboard/login/"
LOGIN_REDIRECT_URL = "/admin-dashboard/"
LOGOUT_REDIRECT_URL = "/admin-dashboard/login/"

# ---------------------------------------------------------------------------
# PRODUCTION SECURITY
# ---------------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"

# ---------------------------------------------------------------------------
# CSRF TRUSTED ORIGINS
# ---------------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    "https://fashion-store-vdud.onrender.com",
]

# ---------------------------------------------------------------------------
# WHITE-LABEL STORE DEFAULTS
# ---------------------------------------------------------------------------
STORE_DEFAULTS = {
    "SHOP_NAME": "Demo Fashion Store",
    "TAGLINE": "Style That Speaks For You",
    "PHONE": "+91 90000 00000",
    "ADDRESS": "12 MG Road, Khammam, Telangana 507001",
    "INSTAGRAM": "https://instagram.com/demofashionstore",
    "INSTAGRAM_HANDLE": "@demofashionstore",
    "OWNER_NAME": "Store Owner",
    "FOUNDED_YEAR": 2015,
    "OPENING_HOURS": (
        "Mon - Sat: 10:00 AM - 9:00 PM | "
        "Sun: 11:00 AM - 7:00 PM"
    ),
    "ABOUT_TEXT": (
        "Since {year}, {shop} has been serving our community with carefully "
        "selected fashion for every occasion. From everyday essentials to "
        "festive collections, we focus on quality, style and personal service."
    ),
    "STORE_LATITUDE": 17.2473,
    "STORE_LONGITUDE": 80.1514,
    "DELIVERY_RADIUS_KM": 10,
}
