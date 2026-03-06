"""
Bridge Authentication
=====================
Supports two authentication modes:

1. JWT (user-facing) — standard DRF JWT for when a human user's frontend
   calls the bridge directly on behalf of a user session.

2. API Key (machine-to-machine) — a shared secret in the request header
   for external apps (execution engine, etc.) calling server-to-server.

Both modes are checked in `authenticate_bridge_request`.
"""

import os
from django.conf import settings


BRIDGE_API_KEY_HEADER = "X-Bridge-Api-Key"


def get_bridge_api_key() -> str:
    """
    Return the configured bridge API key.
    Reads from settings (which reads from env var).
    """
    return getattr(settings, "BRIDGE_API_KEY", "")


def authenticate_bridge_request(request) -> tuple:
    """
    Returns (user, error_response_dict | None).

    Priority:
    1. Valid JWT via DRF authentication (user already set by DRF middleware)
    2. Valid X-Bridge-Api-Key header (machine-to-machine)
    """
    # Mode 1: JWT — DRF already authenticated user via middleware
    if request.user and request.user.is_authenticated:
        return request.user, None

    # Mode 2: Shared API key
    provided_key = request.headers.get(BRIDGE_API_KEY_HEADER, "")
    expected_key = get_bridge_api_key()

    if not expected_key:
        return None, {"error": "Bridge API key not configured on server."}

    if not provided_key:
        return None, {"error": "Authentication required. Provide JWT or X-Bridge-Api-Key header."}

    if provided_key != expected_key:
        return None, {"error": "Invalid bridge API key."}

    # Key-auth: no user context; views must handle user_id param separately
    return None, None
