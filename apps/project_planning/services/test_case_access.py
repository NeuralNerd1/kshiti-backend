# apps/project_planning/services/test_case_access.py

from django.core.exceptions import PermissionDenied

from apps.company_operations.services.project_users import (
    get_project_user,
)


def enforce_test_case_access(
    *,
    project,
    user,
    permission_key: str,
    require_enabled: bool = True,
):
    """
    Central access enforcement for Test Case feature.

    Enforces in order:
    1. Project feature flag (test_cases_enabled)
    2. Project membership
    3. Project role permission (test case scoped)

    This mirrors enforce_feature3_access used for flows.
    """

    # -------------------------------------------------
    # 1. Feature flag enforcement
    # -------------------------------------------------

    if require_enabled and not project.test_cases_enabled:
        raise PermissionDenied(
            "Test cases are disabled for this project"
        )

    # -------------------------------------------------
    # 2. Project membership
    # -------------------------------------------------

    project_user = get_project_user(project, user)

    # -------------------------------------------------
    # 3. Permission enforcement
    # -------------------------------------------------

    permissions = project_user.role.permissions_json or {}

    if permissions.get(permission_key) is not True:
        raise PermissionDenied("Permission denied")

    return project_user
