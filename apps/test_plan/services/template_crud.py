from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied

from apps.test_plan.models import ProcessTemplate
from apps.test_plan.services.template_versioning import clone_template_with_structure
from apps.test_plan.services.guards import ensure_test_planning_enabled

from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import require_project_permission

@transaction.atomic
def create_template(*, project, user, data):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_create_templates")

    return ProcessTemplate.objects.create(
        company=project.company,
        name=data["name"].strip(),
        description=data.get("description", ""),
        version_number=1,
        status=ProcessTemplate.STATUS_DRAFT,
        created_by=user.company_membership,
        is_locked=False,
    )

@transaction.atomic
def update_template(*, template, project, user, data):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    # Company isolation
    if template.company_id != project.company_id:
        raise PermissionDenied("Company mismatch.")

    # If CREATED → deep clone
    if template.status == ProcessTemplate.STATUS_CREATED:
        if not template.is_locked:
            raise ValidationError("CREATED template must be locked.")

        template = clone_template_with_structure(
            template=template,
            user=user,
        )

    # Only DRAFT editable
    if template.status != ProcessTemplate.STATUS_DRAFT:
        raise ValidationError("Only DRAFT templates can be edited.")

    template.name = data.get("name", template.name).strip()
    template.description = data.get("description", template.description)

    template.save(update_fields=["name", "description", "updated_at"])

    return template

@transaction.atomic
def delete_template(*, template, project, user):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    if template.company_id != project.company_id:
        raise PermissionDenied("Company mismatch.")

    if template.status != ProcessTemplate.STATUS_DRAFT:
        raise ValidationError("Only DRAFT templates can be deleted.")

    template.delete()

