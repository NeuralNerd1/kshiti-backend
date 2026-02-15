from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied

from apps.test_plan.models import (
    ProcessTemplate,
    ProjectTemplateBinding,
)

from apps.test_plan.services.guards import ensure_test_planning_enabled

from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import require_project_permission


@transaction.atomic
def activate_template_for_project(*, project, template, user):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    # Company isolation
    if template.company_id != project.company_id:
        raise PermissionDenied("Template does not belong to same company.")

    # Must be CREATED or ACTIVATED (re-activation) and locked
    if template.status not in (ProcessTemplate.STATUS_CREATED, ProcessTemplate.STATUS_ACTIVATED):
        raise ValidationError("Only CREATED or ACTIVATED templates can be activated.")

    if not template.is_locked:
        raise ValidationError("Template must be locked before activation.")

    # Find templates currently active for this project to revert their status
    currently_active_bindings = ProjectTemplateBinding.objects.filter(
        project=project,
        is_active=True,
    ).select_related("template")

    for old_binding in currently_active_bindings:
        old_template = old_binding.template
        # Only revert to CREATED if it's not the same template we are activating
        if old_template.id != template.id:
            # Check if this template is active in ANY OTHER project
            other_active_bindings = ProjectTemplateBinding.objects.filter(
                template=old_template,
                is_active=True
            ).exclude(project=project).exists()

            if not other_active_bindings:
                old_template.status = ProcessTemplate.STATUS_CREATED
                old_template.save(update_fields=["status", "updated_at"])

    # Deactivate existing active bindings for this project
    currently_active_bindings.update(is_active=False)

    # Activate (or re-activate) binding for this template
    binding, _created = ProjectTemplateBinding.objects.update_or_create(
        project=project,
        template=template,
        defaults={
            "activated_by": user.company_membership,
            "is_active": True,
        },
    )

    # Update template status to ACTIVATED
    template.status = ProcessTemplate.STATUS_ACTIVATED
    template.save(update_fields=["status", "updated_at"])

    return binding
