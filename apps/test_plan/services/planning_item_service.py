from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied

from apps.test_plan.models import (
    PlanningItem,
    PlanningItemFieldValue,
    ProjectTemplateBinding,
    EntityFieldDefinition,
)

from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import require_project_permission
from apps.test_plan.services.guards import ensure_test_planning_enabled

@transaction.atomic
def create_planning_item(*, project, user, data):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_create_planning_items")

    binding = ProjectTemplateBinding.objects.filter(
        project=project,
        is_active=True,
    ).select_related("template").first()

    if not binding:
        raise ValidationError("No active template bound to project.")

    template = binding.template
    entity_type = data["entity_type"]

    if entity_type.template_id != template.id:
        raise ValidationError("Entity type must belong to active template.")

    parent = data.get("parent")

    if parent:
        if parent.project_id != project.id:
            raise ValidationError("Parent must belong to same project.")

        if parent.entity_type.level_order >= entity_type.level_order:
            raise ValidationError("Invalid parent hierarchy.")

    owner = data["owner"]
    if owner.project_id != project.id:
        raise ValidationError("Owner must belong to project.")

    assigned_users = data.get("assigned_users", [])
    for assigned in assigned_users:
        if assigned.project_id != project.id:
            raise ValidationError("Assigned users must belong to project.")

    workflow = entity_type.workflow_definition
    if not workflow or not workflow.initial_state:
        raise ValidationError("Workflow initial state not configured.")

    item = PlanningItem.objects.create(
        project=project,
        entity_type=entity_type,
        parent=parent,
        path="",
        status=workflow.initial_state,
        owner=owner,
        created_by=project_user,
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
    )

    item.assigned_users.set(assigned_users)

    _validate_and_create_field_values(
        planning_item=item,
        entity_type=entity_type,
        field_values=data.get("field_values", {}),
        project=project,
    )

    return item

@transaction.atomic
def update_planning_item(*, project, item, user, data):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_planning_items")

    if item.project_id != project.id:
        raise PermissionDenied("Invalid project access.")

    if "owner" in data:
        owner = data["owner"]
        if owner.project_id != project.id:
            raise ValidationError("Owner must belong to project.")
        item.owner = owner

    if "assigned_users" in data:
        for assigned in data["assigned_users"]:
            if assigned.project_id != project.id:
                raise ValidationError("Assigned users must belong to project.")
        item.assigned_users.set(data["assigned_users"])

    if "parent" in data:
        parent = data["parent"]
        if parent and parent.project_id != project.id:
            raise ValidationError("Parent must belong to project.")
        item.parent = parent

    item.start_date = data.get("start_date", item.start_date)
    item.end_date = data.get("end_date", item.end_date)

    item.save()

    if "field_values" in data:
        item.field_values.all().delete()

        _validate_and_create_field_values(
            planning_item=item,
            entity_type=item.entity_type,
            field_values=data["field_values"],
            project=project,
        )

    return item

@transaction.atomic
def delete_planning_item(*, project, item, user):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_planning_items")

    if item.project_id != project.id:
        raise PermissionDenied("Invalid project access.")

    item.delete()

def _validate_and_create_field_values(*, planning_item, entity_type, field_values, project):

    definitions = EntityFieldDefinition.objects.filter(
        entity_type=entity_type
    )

    definition_map = {f.field_key: f for f in definitions}

    for definition in definitions:
        if definition.is_required and definition.field_key not in field_values:
            raise ValidationError(f"{definition.field_key} is required.")

    for key, value in field_values.items():

        if key not in definition_map:
            raise ValidationError(f"Invalid field: {key}")

        definition = definition_map[key]

        _validate_field_type(definition, value, project)

        PlanningItemFieldValue.objects.create(
            planning_item=planning_item,
            field_definition=definition,
            value_json=value,
        )

def _validate_field_type(definition, value, project):

    field_type = definition.field_type

    if field_type in ["text", "long_text"]:
        if not isinstance(value, str):
            raise ValidationError("Invalid text value.")

    elif field_type == "number":
        if not isinstance(value, (int, float)):
            raise ValidationError("Invalid number value.")

    elif field_type == "boolean":
        if not isinstance(value, bool):
            raise ValidationError("Invalid boolean value.")

    elif field_type == "date":
        pass

    elif field_type == "datetime":
        pass

    elif field_type == "select":
        options = definition.options_json or []
        if value not in options:
            raise ValidationError("Invalid select option.")

    elif field_type == "multi_select":
        if not isinstance(value, list):
            raise ValidationError("Multi select must be list.")
        options = definition.options_json or []
        invalid = set(value) - set(options)
        if invalid:
            raise ValidationError("Invalid multi select option.")

    elif field_type == "user":
        if not hasattr(value, "project_id") or value.project_id != project.id:
            raise ValidationError("Invalid user reference.")

    elif field_type == "multi_user":
        for user in value:
            if user.project_id != project.id:
                raise ValidationError("Invalid user reference.")
