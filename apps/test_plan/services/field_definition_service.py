from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied

from apps.test_plan.models import (
    EntityFieldDefinition,
)
from apps.test_plan.services.guards import ensure_test_planning_enabled

from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import require_project_permission

@transaction.atomic
def create_field_definition(*, project, entity_type, user, data):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    template = entity_type.template

    if template.company_id != project.company_id:
        raise PermissionDenied("Company mismatch.")

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    # field_key uniqueness
    if EntityFieldDefinition.objects.filter(
        entity_type=entity_type,
        field_key=data["field_key"],
    ).exists():
        raise ValidationError("field_key must be unique within entity type.")

    # order uniqueness
    if EntityFieldDefinition.objects.filter(
        entity_type=entity_type,
        order=data["order"],
    ).exists():
        raise ValidationError("order must be unique within entity type.")

    _validate_field_logic(data)

    return EntityFieldDefinition.objects.create(
        entity_type=entity_type,
        **data,
    )

@transaction.atomic
def update_field_definition(*, project, field, user, data):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    template = field.entity_type.template

    if template.company_id != project.company_id:
        raise PermissionDenied("Company mismatch.")

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    # Prevent changing structural keys
    if "field_key" in data and data["field_key"] != field.field_key:
        raise ValidationError("Changing field_key is not allowed.")

    if "field_type" in data and data["field_type"] != field.field_type:
        raise ValidationError("Changing field_type is not allowed.")

    # order uniqueness
    if "order" in data:
        if EntityFieldDefinition.objects.filter(
            entity_type=field.entity_type,
            order=data["order"],
        ).exclude(id=field.id).exists():
            raise ValidationError("order must be unique.")

    _validate_field_logic(data, instance=field)

    for key, value in data.items():
        setattr(field, key, value)

    field.save()
    return field
@transaction.atomic
def delete_field_definition(*, project, field, user):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    template = field.entity_type.template

    if template.company_id != project.company_id:
        raise PermissionDenied("Company mismatch.")

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    field.delete()

def _validate_field_logic(data, instance=None):

    field_type = data.get("field_type") or (instance.field_type if instance else None)
    options = data.get("options_json") or (instance.options_json if instance else None)

    if field_type in ["select", "multi_select"]:

        if not isinstance(options, list) or not options:
            raise ValidationError("Select fields must have non-empty options_json.")

        cleaned = [str(o).strip() for o in options]

        if "" in cleaned:
            raise ValidationError("Options cannot contain empty values.")

        if len(cleaned) != len(set(cleaned)):
            raise ValidationError("Duplicate options not allowed.")

    if data.get("is_required") and field_type in ["select", "multi_select"]:
        if not options:
            raise ValidationError("Required select field must define options.")
