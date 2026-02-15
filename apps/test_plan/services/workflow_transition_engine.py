from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied

from apps.test_plan.models import (
    PlanningItem,
    WorkflowTransition,
    PlanningDependency,
    PlanningItemFieldValue,
    EntityFieldDefinition,
)

from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import require_project_permission
from apps.test_plan.services.guards import ensure_test_planning_enabled

@transaction.atomic
def transition_planning_item(*, item, user, target_state_id):

    project = item.project

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)

    workflow = item.entity_type.workflow_definition

    if not workflow:
        raise ValidationError("Workflow not configured.")

    current_state = item.status

    if not current_state:
        raise ValidationError("Item has no current state.")

    if current_state.is_final:
        raise ValidationError("Cannot transition from final state.")

    # 1️⃣ Transition must exist
    transition = WorkflowTransition.objects.filter(
        workflow=workflow,
        from_state=current_state,
        to_state_id=target_state_id,
    ).first()

    if not transition:
        raise ValidationError("Invalid workflow transition.")

    # 2️⃣ Permission enforcement
    allowed_roles = transition.allowed_roles or []

    has_permission = False
    for role_key in allowed_roles:
        try:
            require_project_permission(project_user, role_key)
            has_permission = True
            break
        except Exception:
            continue

    if not has_permission:
        raise PermissionDenied("User not allowed to perform this transition.")

    # 3️⃣ Dependency blocking check
    blocking_dependencies = PlanningDependency.objects.filter(
        target_item=item,
        dependency_type="BLOCKS",
    )

    for dependency in blocking_dependencies:
        source = dependency.source_item
        if not source.status or not source.status.is_final:
            raise ValidationError(
                f"Blocked by item {source.id} not completed."
            )

    # 4️⃣ Required field validation
    definitions = EntityFieldDefinition.objects.filter(
        entity_type=item.entity_type,
        is_required=True,
    )

    existing_fields = PlanningItemFieldValue.objects.filter(
        planning_item=item
    ).values_list("field_definition__field_key", flat=True)

    for definition in definitions:
        if definition.field_key not in existing_fields:
            raise ValidationError(
                f"Required field '{definition.field_key}' missing."
            )

    # 5️⃣ Perform transition
    item.status_id = target_state_id
    item.save(update_fields=["status", "updated_at"])

    return item

