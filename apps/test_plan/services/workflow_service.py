from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied

from apps.test_plan.models import (
    WorkflowDefinition,
    WorkflowState,
    WorkflowTransition,
)
from apps.test_plan.services.guards import ensure_test_planning_enabled

from apps.company_operations.project_permissions import PROJECT_PERMISSION_KEYS
from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import require_project_permission

@transaction.atomic
def create_workflow(*, project, entity_type, user):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    template = entity_type.template

    if template.company_id != project.company_id:
        raise PermissionDenied("Company mismatch.")

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    if WorkflowDefinition.objects.filter(entity_type=entity_type).exists():
        raise ValidationError("Workflow already exists.")

    return WorkflowDefinition.objects.create(
        entity_type=entity_type
    )

@transaction.atomic
def update_workflow(*, project, workflow, user, data):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    template = workflow.entity_type.template

    if template.company_id != project.company_id:
        raise PermissionDenied("Company mismatch.")

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    initial_state_id = data.get("initial_state")

    if initial_state_id:
        state = WorkflowState.objects.filter(
            id=initial_state_id,
            workflow=workflow
        ).first()

        if not state:
            raise ValidationError("Initial state must belong to workflow.")

        workflow.initial_state = state

    workflow.save()
    return workflow

@transaction.atomic
def delete_workflow(*, project, workflow, user):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    template = workflow.entity_type.template

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    if WorkflowState.objects.filter(workflow=workflow).exists():
        raise ValidationError("Cannot delete workflow with states.")

    workflow.delete()

@transaction.atomic
def create_state(*, project, workflow, user, data):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    template = workflow.entity_type.template

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    if WorkflowState.objects.filter(
        workflow=workflow,
        name=data["name"]
    ).exists():
        raise ValidationError("State name must be unique.")

    if WorkflowState.objects.filter(
        workflow=workflow,
        order=data["order"]
    ).exists():
        raise ValidationError("State order must be unique.")

    return WorkflowState.objects.create(
        workflow=workflow,
        **data
    )

@transaction.atomic
def update_state(*, project, state, user, data):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    workflow = state.workflow
    template = workflow.entity_type.template

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    if "name" in data:
        if WorkflowState.objects.filter(
            workflow=workflow,
            name=data["name"]
        ).exclude(id=state.id).exists():
            raise ValidationError("State name must be unique.")

    if "order" in data:
        if WorkflowState.objects.filter(
            workflow=workflow,
            order=data["order"]
        ).exclude(id=state.id).exists():
            raise ValidationError("State order must be unique.")

    for key, value in data.items():
        setattr(state, key, value)

    state.save()
    return state

@transaction.atomic
def delete_state(*, project, state, user):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    workflow = state.workflow
    template = workflow.entity_type.template

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    if workflow.initial_state_id == state.id:
        raise ValidationError("Cannot delete initial state.")

    if WorkflowTransition.objects.filter(from_state=state).exists() or \
       WorkflowTransition.objects.filter(to_state=state).exists():
        raise ValidationError("Cannot delete state used in transitions.")

    state.delete()

@transaction.atomic
def create_transition(*, project, workflow, user, data):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    template = workflow.entity_type.template

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    from_state_val = data["from_state"]
    to_state_val = data["to_state"]

    # DRF ForeignKey fields resolve to model instances in validated_data
    from_state_id = from_state_val.id if isinstance(from_state_val, WorkflowState) else from_state_val
    to_state_id = to_state_val.id if isinstance(to_state_val, WorkflowState) else to_state_val

    from_state = WorkflowState.objects.filter(
        id=from_state_id,
        workflow=workflow
    ).first()

    to_state = WorkflowState.objects.filter(
        id=to_state_id,
        workflow=workflow
    ).first()

    if not from_state or not to_state:
        raise ValidationError("States must belong to workflow.")

    if from_state.id == to_state.id:
        raise ValidationError("Self transitions not allowed.")

    if WorkflowTransition.objects.filter(
        workflow=workflow,
        from_state=from_state,
        to_state=to_state,
    ).exists():
        raise ValidationError("Transition already exists.")

    allowed_roles = data.get("allowed_roles", [])
    invalid = set(allowed_roles) - PROJECT_PERMISSION_KEYS
    if invalid:
        raise ValidationError(f"Invalid roles: {', '.join(invalid)}")

    return WorkflowTransition.objects.create(
        workflow=workflow,
        from_state=from_state,
        to_state=to_state,
        allowed_roles=allowed_roles,
    )

@transaction.atomic
def update_transition(*, project, transition, user, data):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    template = transition.workflow.entity_type.template

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    if "allowed_roles" in data:
        invalid = set(data["allowed_roles"]) - PROJECT_PERMISSION_KEYS
        if invalid:
            raise ValidationError(f"Invalid roles: {', '.join(invalid)}")
        transition.allowed_roles = data["allowed_roles"]

    transition.save()
    return transition

@transaction.atomic
def delete_transition(*, project, transition, user):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    template = transition.workflow.entity_type.template

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    transition.delete()
