from django.core.exceptions import PermissionDenied
from ..permissions import ALL_PERMISSION_KEYS
from rest_framework.exceptions import APIException

class PermissionDeniedError(APIException):
    status_code = 403
    default_code = "PERMISSION_DENIED"
    default_detail = "You do not have permission to perform this action."

def has_permission(company_user, permission_key: str) -> bool:
    """
    Strict permission resolution.
    No caching. Deny by default.
    """
    if permission_key not in ALL_PERMISSION_KEYS:
        raise ValueError(f"Unknown permission key: {permission_key}")

    if not company_user.is_active:
        return False

    perms = company_user.role.permissions_json or {}
    return bool(perms.get(permission_key, False))


def require_permission(company_user, permission_key: str):
    if not has_permission(company_user, permission_key):
        raise PermissionDeniedError()
