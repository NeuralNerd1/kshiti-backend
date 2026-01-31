from django.core.exceptions import PermissionDenied

# Explicit and isolated permission scope
TEST_CASE_PERMISSION_KEYS = {
    "can_create_test_cases",
    "can_edit_test_cases",
    "can_view_test_cases",
}


def require_test_case_permission(project_user, permission_key: str):
    """
    Enforce test case–specific permissions.

    No fallback to project or flow permissions.
    """

    if permission_key not in TEST_CASE_PERMISSION_KEYS:
        raise ValueError(
            f"Unknown test case permission: {permission_key}"
        )

    if not project_user.is_active:
        raise PermissionDenied("Inactive project membership")

    permissions = project_user.role.permissions_json or {}

    if permissions.get(permission_key) is not True:
        raise PermissionDenied("Permission denied")
