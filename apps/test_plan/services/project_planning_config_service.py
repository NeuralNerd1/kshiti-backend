from django.db import transaction
from django.core.exceptions import ValidationError

from apps.test_plan.models import ProjectPlanningConfig
from apps.test_plan.services.guards import ensure_test_planning_enabled

from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import require_project_permission

def get_or_create_planning_config(*, project, user):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)

    # View-level permission can be lighter
    require_project_permission(project_user, "can_edit_templates")

    config, _ = ProjectPlanningConfig.objects.get_or_create(
        project=project
    )

    return config

@transaction.atomic
def update_planning_config(*, project, user, data):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    config, _ = ProjectPlanningConfig.objects.get_or_create(
        project=project
    )

    for field, value in data.items():
        setattr(config, field, value)

    config.save()
    return config

