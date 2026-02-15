from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied

from apps.test_plan.models import TimeTrackingRule
from apps.test_plan.services.guards import ensure_test_planning_enabled

from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import require_project_permission


@transaction.atomic
def create_time_rule(*, project, entity_type, user, data):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    template = entity_type.template

    if template.company_id != project.company_id:
        raise PermissionDenied("Company mismatch.")

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    if not entity_type.allow_time_tracking:
        raise ValidationError("Time tracking not allowed for this entity type.")

    if TimeTrackingRule.objects.filter(entity_type=entity_type).exists():
        raise ValidationError("Time tracking rule already exists for this entity.")

    return TimeTrackingRule.objects.create(
        entity_type=entity_type,
        **data,
    )


@transaction.atomic
def update_time_rule(*, project, rule, user, data):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    template = rule.entity_type.template

    if template.company_id != project.company_id:
        raise PermissionDenied("Company mismatch.")

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    for key, value in data.items():
        setattr(rule, key, value)

    rule.save()
    return rule


@transaction.atomic
def delete_time_rule(*, project, rule, user):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    template = rule.entity_type.template

    if template.company_id != project.company_id:
        raise PermissionDenied("Company mismatch.")

    if template.is_locked:
        raise ValidationError("Cannot modify locked template.")

    rule.delete()
