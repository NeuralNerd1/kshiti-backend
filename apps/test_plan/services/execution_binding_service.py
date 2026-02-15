from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied

from apps.test_plan.models import ExecutionBinding
from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import require_project_permission
from apps.test_plan.services.guards import ensure_test_planning_enabled

@transaction.atomic
def bind_execution(*, item, user, flow=None, test_case=None,
                   execution_mode=None, auto_trigger=False):

    project = item.project

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_bind_execution")

    # 1️⃣ Entity must allow binding
    if not item.entity_type.allow_execution_binding:
        raise ValidationError("Execution binding not allowed for this entity.")

    # 2️⃣ Must bind at least one
    if not flow and not test_case:
        raise ValidationError("Either flow or test_case must be provided.")

    # 3️⃣ Cross-project validation
    if flow and flow.project_id != project.id:
        raise ValidationError("Flow must belong to same project.")

    if test_case and test_case.project_id != project.id:
        raise ValidationError("TestCase must belong to same project.")

    binding, created = ExecutionBinding.objects.update_or_create(
        planning_item=item,
        defaults={
            "flow": flow,
            "test_case": test_case,
            "execution_mode": execution_mode or "",
            "auto_trigger": auto_trigger,
        },
    )

    return binding


@transaction.atomic
def delete_execution_binding(*, binding, user):

    project = binding.planning_item.project

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_bind_execution")

    binding.delete()

