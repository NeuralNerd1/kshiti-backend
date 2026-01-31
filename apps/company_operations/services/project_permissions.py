from rest_framework.exceptions import PermissionDenied
from apps.company_operations.project_permissions import PROJECT_PERMISSION_KEYS


def require_project_permission(project_user, permission_key: str):
    """
    Enforce project-scoped permissions.
    NO fallback to company roles.
    """

    if permission_key not in PROJECT_PERMISSION_KEYS:
        raise ValueError(f"Unknown project permission: {permission_key}")

    if not project_user.is_active:
        raise PermissionDenied("Inactive project membership")

    permissions = project_user.role.permissions_json or {}

    if permissions.get(permission_key) is not True:
        raise PermissionDenied("Permission denied")
