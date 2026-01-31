from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.company_operations.services.project_users import (
    get_project_user,
)
from apps.company_operations.services.project_permissions import (
    require_project_permission,
)


def ensure_test_cases_enabled(project):
    """
    Feature flag enforcement.
    """
    if not project.test_cases_enabled:
        raise ValidationError(
            "Test cases are disabled for this project"
        )


def ensure_can_create_test_cases(user, project):
    """
    Permission: can_create_test_cases
    """
    project_user = get_project_user(project, user)
    require_project_permission(
        project_user,
        "can_create_test_cases",
    )


def ensure_can_edit_test_cases(user, project):
    """
    Permission: can_edit_test_cases
    """
    project_user = get_project_user(project, user)
    require_project_permission(
        project_user,
        "can_edit_test_cases",
    )


def ensure_can_view_test_cases(user, project):
    """
    Permission: can_view_test_cases
    """
    project_user = get_project_user(project, user)
    require_project_permission(
        project_user,
        "can_view_test_cases",
    )
