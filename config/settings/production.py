from .base import *
import os
from urllib.parse import urlparse

DEBUG = False

# -----------------------------------
# DATABASE (Supabase PostgreSQL)
# -----------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL not set for production")

db = urlparse(DATABASE_URL)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db.path[1:],  # remove leading /
        "USER": db.username,
        "PASSWORD": db.password,
        "HOST": db.hostname,
        "PORT": db.port,
        "OPTIONS": {
            "sslmode": "require",
        },
    }
}

# -----------------------------------
# ALLOWED HOSTS
# -----------------------------------

ALLOWED_HOSTS = [
    "api.kshiti.io",
    ".onrender.com",
]

# -----------------------------------
# SECURITY
# -----------------------------------

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
