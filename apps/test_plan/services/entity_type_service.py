from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied

from apps.test_plan.models import (
    PlanningEntityType,
    WorkflowDefinition,
    EntityFieldDefinition,
)
from apps.test_plan.services.guards import ensure_test_planning_enabled

from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import require_project_permission

@transaction.atomic
def create_entity_type(*, project, template, user, data):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    if template.company_id != project.company_id:
        raise PermissionDenied("Company mismatch.")

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    # level_order unique
    if PlanningEntityType.objects.filter(
        template=template,
        level_order=data["level_order"],
    ).exists():
        raise ValidationError("level_order must be unique within template.")

    # internal_key unique
    if PlanningEntityType.objects.filter(
        template=template,
        internal_key=data["internal_key"],
    ).exists():
        raise ValidationError("internal_key must be unique within template.")

    return PlanningEntityType.objects.create(
        template=template,
        **data,
    )

@transaction.atomic
def update_entity_type(*, project, entity_type, user, data):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    template = entity_type.template

    if template.company_id != project.company_id:
        raise PermissionDenied("Company mismatch.")

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    # level_order uniqueness (exclude self)
    if "level_order" in data:
        if PlanningEntityType.objects.filter(
            template=template,
            level_order=data["level_order"],
        ).exclude(id=entity_type.id).exists():
            raise ValidationError("level_order must be unique.")

    # internal_key uniqueness (exclude self)
    if "internal_key" in data:
        if PlanningEntityType.objects.filter(
            template=template,
            internal_key=data["internal_key"],
        ).exclude(id=entity_type.id).exists():
            raise ValidationError("internal_key must be unique.")

    for field, value in data.items():
        setattr(entity_type, field, value)

    entity_type.save()
    return entity_type

@transaction.atomic
def delete_entity_type(*, project, entity_type, user):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    template = entity_type.template

    if template.company_id != project.company_id:
        raise PermissionDenied("Company mismatch.")

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    # Block if workflow exists
    if WorkflowDefinition.objects.filter(entity_type=entity_type).exists():
        raise ValidationError("Cannot delete entity type with workflow.")

    # Block if fields exist
    if EntityFieldDefinition.objects.filter(entity_type=entity_type).exists():
        raise ValidationError("Cannot delete entity type with fields.")

    entity_type.delete()

