from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from apps.company_operations.models import Project
from apps.common.api_errors import api_error
from rest_framework.exceptions import APIException
from apps.company_operations.services.project_bootstrap import (
    bootstrap_project_access,
)

class ProjectCreationDisabled(APIException):
    status_code = 403
    default_code = "PROJECT_CREATION_DISABLED"
    default_detail = "Project creation is disabled for this company."


class MaxProjectLimitReached(APIException):
    status_code = 403
    default_code = "MAX_PROJECT_LIMIT_REACHED"
    default_detail = "Maximum number of projects reached for this company."


def validate_project_creation(company):
    """
    Enforce company-level project creation rules.
    SINGLE SOURCE OF TRUTH.
    """
    if not company.can_create_projects:
        raise ProjectCreationDisabled()

    active_count = Project.objects.filter(
        company=company,
        status=Project.STATUS_ACTIVE,
    ).count()

    if company.max_projects > 0 and active_count >= company.max_projects:
        raise MaxProjectLimitReached()


@transaction.atomic
def create_project(*, company, data):
    """
    Atomic project creation.
    Prevents race conditions on max_projects.
    """
    validate_project_creation(company)

    project = Project.objects.create(
        company=company,
        name=data["name"],
        description=data.get("description", ""),
        max_team_members=data["max_team_members"],
        project_admin=data["project_admin"],
    )
    bootstrap_project_access(
        project=project,
        creator_company_user=data["project_admin"],
    )

    return project
