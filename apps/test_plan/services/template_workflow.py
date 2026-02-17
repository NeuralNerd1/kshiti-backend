from django.core.exceptions import ValidationError, PermissionDenied
from apps.company_operations.services.project_permissions import require_project_permission
from apps.company_operations.services.project_users import get_project_user
from apps.test_plan.models import ProcessTemplate

def transition_template_status(
    *,
    template: ProcessTemplate,
    project,
    user,
    action: str,
    rejection_note: str = None,
):
    """
    Central state machine for template transitions.
    """

    project_user = get_project_user(project, user)

    if not project.test_planning_enabled:
        raise PermissionDenied("Test planning is disabled.")

    current_status = template.status
    needs_approval = project.template_needs_approval

    # -----------------------------------------
    # CASE 1: Approval Required
    # -----------------------------------------
    if needs_approval:

        if current_status == ProcessTemplate.STATUS_DRAFT:

            if action == "submit":
                require_project_permission(project_user, "can_submit_templates")
                template.status = ProcessTemplate.STATUS_SUBMITTED
                template.save(update_fields=["status"])
                return template

            raise ValidationError("Invalid action from DRAFT.")

        if current_status == ProcessTemplate.STATUS_SUBMITTED:

            if action == "assign_reviewer":
                require_project_permission(project_user, "can_edit_templates")
                template.status = ProcessTemplate.STATUS_APPROVAL_PENDING
                template.reviewer = project_user.company_user
                template.save(update_fields=["status", "reviewer"])
                return template

            raise ValidationError("Invalid action from SUBMITTED.")

        if current_status == ProcessTemplate.STATUS_APPROVAL_PENDING:

            if action == "approve":
                require_project_permission(project_user, "can_approve_templates")
                template.status = ProcessTemplate.STATUS_APPROVED
                template.save(update_fields=["status"])
                return template

            if action == "reject":
                require_project_permission(project_user, "can_approve_templates")
                template.status = ProcessTemplate.STATUS_REJECTED
                template.rejection_note = rejection_note
                template.save(update_fields=["status", "rejection_note"])
                return template

            raise ValidationError("Invalid action from APPROVAL_PENDING.")

        if current_status == ProcessTemplate.STATUS_APPROVED:

            if action == "create":
                require_project_permission(project_user, "can_create_templates")
                template.status = ProcessTemplate.STATUS_CREATED
                template.is_locked = True
                template.save(update_fields=["status", "is_locked"])
                return template

            raise ValidationError("Invalid action from APPROVED.")

        if current_status == ProcessTemplate.STATUS_REJECTED:

            if action == "edit":
                require_project_permission(project_user, "can_edit_templates")
                template.status = ProcessTemplate.STATUS_DRAFT
                template.rejection_note = None
                template.save(update_fields=["status", "rejection_note"])
                return template

            raise ValidationError("Invalid action from REJECTED.")

    # -----------------------------------------
    # CASE 2: No Approval Required
    # -----------------------------------------
    else:

        if current_status == ProcessTemplate.STATUS_DRAFT:

            if action == "save":
                require_project_permission(project_user, "can_create_templates")
                template.status = ProcessTemplate.STATUS_CREATED
                template.is_locked = True
                template.save(update_fields=["status", "is_locked"])
                return template

            raise ValidationError("Invalid action from DRAFT.")

    raise ValidationError("Invalid transition.")

