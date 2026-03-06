from .base import *
import os
from urllib.parse import urlparse
from pathlib import Path

# Load .env file from the backend root
from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

DEBUG = True

DATABASE_URL = os.getenv("DATABASE_URL", "")

if DATABASE_URL:
    db = urlparse(DATABASE_URL)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": db.path[1:],
            "USER": db.username,
            "PASSWORD": db.password,
            "HOST": db.hostname,
            "PORT": db.port,
            "OPTIONS": {
                "sslmode": "require",
            },
        },
        "sqlite_old": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # Fallback to SQLite if no DATABASE_URL is set
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ─────────────────────────────────────────────────────────────────────────────
# BRIDGE — local development
# ─────────────────────────────────────────────────────────────────────────────
# Use this key in X-Bridge-Api-Key header when testing bridge endpoints locally.
# Override via env var: export BRIDGE_API_KEY=your-local-key
import os
BRIDGE_API_KEY = os.environ.get("BRIDGE_API_KEY", "dev-bridge-secret-changeme")

# Allow the external app running locally to call the bridge
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",   # main Next.js frontend
    "http://localhost:3001",   # execution frontend (separate app)
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]
