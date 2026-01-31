from rest_framework.exceptions import PermissionDenied
from apps.company_operations.models import ProjectUser


def get_project_user(project, user):
    """
    Resolve active project membership.
    """
    try:
        return ProjectUser.objects.select_related("role").get(
            project=project,
            company_user__user=user,
            is_active=True,
        )
    except ProjectUser.DoesNotExist:
        raise PermissionDenied("User not added to this project")
