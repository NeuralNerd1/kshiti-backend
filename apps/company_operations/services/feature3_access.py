from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import (
    require_project_permission,
)
from django.core.exceptions import PermissionDenied
from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import (
    require_project_permission,
)

def enforce_feature3_permission(*, project, user, permission_key):
    project_user = get_project_user(project, user)
    require_project_permission(project_user, permission_key)
    return project_user

def enforce_feature3_access(
    *,
    project,
    user,
    permission_key,
    require_enabled=True,
):
    """
    Central enforcement for Feature-3 (Planning).

    Rules:
    - flows_enabled must be true (unless explicitly skipped)
    - user must be a ProjectUser
    - user must have the required project permission
    """

    if require_enabled and not project.flows_enabled:
        raise PermissionDenied("Flows are disabled for this project")

    project_user = get_project_user(project, user)
    require_project_permission(project_user, permission_key)

    return project_user