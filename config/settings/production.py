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
    # Add external app host here when deploying
    # "exec.kshiti.io",
]

# -----------------------------------
# SECURITY
# -----------------------------------

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# Shared cookie domain so the external app on exec.kshiti.io
# automatically inherits the user session from kshiti.io
# SESSION_COOKIE_DOMAIN = ".kshiti.io"

# -----------------------------------
# CORS — allow external app origin
# -----------------------------------
# When you deploy the external app, add its origin here:
CORS_ALLOWED_ORIGINS = [
    "https://kshiti.io",
    "https://www.kshiti.io",
    "https://app.kshiti.io",
    "http://localhost:3000",
    # "https://exec.kshiti.io",  # ← uncomment when external app is deployed
]

# -----------------------------------
# BRIDGE API KEY (production)
# -----------------------------------
# Must be set as an environment variable / secret in your deployment.
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
BRIDGE_API_KEY = os.environ.get("BRIDGE_API_KEY", "")
if not BRIDGE_API_KEY:
    raise Exception(
        "BRIDGE_API_KEY must be set in production environment. "
        "Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
    )
