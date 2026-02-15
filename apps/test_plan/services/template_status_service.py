from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied

from apps.test_plan.models import ProcessTemplate
from apps.test_plan.services.guards import ensure_test_planning_enabled

from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import require_project_permission

@transaction.atomic
def transition_template_status(
    *,
    template,
    project,
    user,
    action,
    reviewer_id=None,
    rejection_note=None,
):
    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)

    if template.company_id != project.company_id:
        raise PermissionDenied("Company mismatch.")

    # ---------------------------------------
    # SUBMIT
    # ---------------------------------------
    if action == "submit":

        require_project_permission(project_user, "can_submit_templates")

        if template.status != ProcessTemplate.STATUS_DRAFT:
            raise ValidationError("Only DRAFT templates can be submitted.")

        template.status = ProcessTemplate.STATUS_SUBMITTED
        template.save(update_fields=["status", "updated_at"])
        return template

    # ---------------------------------------
    # ASSIGN REVIEWER
    # ---------------------------------------
        # ---------------------------------------
    # ASSIGN REVIEWER
    # ---------------------------------------
    if action == "assign_reviewer":

        require_project_permission(project_user, "can_edit_templates")

        if not project.template_needs_approval:
            raise ValidationError("Approval flow not enabled.")

        if template.status != ProcessTemplate.STATUS_SUBMITTED:
            raise ValidationError("Template must be SUBMITTED.")

        if not reviewer_id:
            raise ValidationError("Reviewer ID required.")

        # ✅ Correct resolution of reviewer
        from apps.company_operations.models import ProjectUser

        reviewer_project_user = ProjectUser.objects.filter(
            id=reviewer_id,
            project=project,
            is_active=True,
        ).select_related("company_user").first()

        if not reviewer_project_user:
            raise ValidationError("Reviewer must belong to this project.")

        # Reviewer must have approve permission
        require_project_permission(
            reviewer_project_user,
            "can_approve_templates"
        )

        template.reviewer = reviewer_project_user.company_user
        template.status = ProcessTemplate.STATUS_APPROVAL_PENDING
        template.save(update_fields=["reviewer", "status", "updated_at"])
        return template


    # ---------------------------------------
    # APPROVE
    # ---------------------------------------
    if action == "approve":

        require_project_permission(project_user, "can_approve_templates")

        if not project.template_needs_approval:
            raise ValidationError("Approval flow not enabled.")

        if template.status != ProcessTemplate.STATUS_APPROVAL_PENDING:
            raise ValidationError("Template not pending approval.")

        if template.reviewer_id != project_user.company_user_id:
            raise PermissionDenied("Only assigned reviewer can approve.")

        template.status = ProcessTemplate.STATUS_APPROVED
        template.save(update_fields=["status", "updated_at"])
        return template

    # ---------------------------------------
    # REJECT
    # ---------------------------------------
    if action == "reject":

        require_project_permission(project_user, "can_approve_templates")

        if not project.template_needs_approval:
            raise ValidationError("Approval flow not enabled.")

        if template.status != ProcessTemplate.STATUS_APPROVAL_PENDING:
            raise ValidationError("Template not pending approval.")

        if template.reviewer_id != project_user.company_user_id:
            raise PermissionDenied("Only assigned reviewer can reject.")

        if not rejection_note:
            raise ValidationError("Rejection note required.")

        template.status = ProcessTemplate.STATUS_DRAFT
        template.rejection_note = rejection_note
        template.reviewer = None
        template.save(
            update_fields=["status", "rejection_note", "reviewer", "updated_at"]
        )
        return template

    # ---------------------------------------
    # CREATE (FINALIZE)
    # ---------------------------------------
    if action == "create":

        require_project_permission(project_user, "can_create_templates")

        if project.template_needs_approval:
            if template.status != ProcessTemplate.STATUS_APPROVED:
                raise ValidationError("Template must be APPROVED.")
        else:
            if template.status != ProcessTemplate.STATUS_DRAFT:
                raise ValidationError("Template must be DRAFT.")

        template.status = ProcessTemplate.STATUS_CREATED
        template.is_locked = True
        template.save(update_fields=["status", "is_locked", "updated_at"])
        return template

    raise ValidationError("Invalid action.")

