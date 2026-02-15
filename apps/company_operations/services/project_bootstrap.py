from apps.company_operations.models import ProjectRole, ProjectUser


def bootstrap_project_access(*, project, creator_company_user):
    """
    Create default project roles and assign creator.
    This is FEATURE-3 ONLY.
    """

    # ---- Project Admin Role ----
    admin_role = ProjectRole.objects.create(
        project=project,
        name="Project Admin",
        permissions_json={
            "can_view_project": True,
            "can_edit_project": True,
            "can_manage_project_users": True,

            # Feature-3
            "can_view_flows": True,
            "can_create_flows": True,
            "can_edit_flows": True,
            "can_capture_elements": True,
            "can_use_builder": True,
            "can_execute_tests": True,
            "can_view_reports": True,
            "can_create_templates": True,
        "can_edit_templates": True,
        "can_submit_templates": True,
        "can_approve_templates": True,
        "can_create_planning_items": True,
        "can_edit_planning_items": True,
        "can_review_planning_items": True,
        "can_bind_execution": True,
        "can_track_time": True,
        },
    )

    # ---- Project Member Role ----
    member_role = ProjectRole.objects.create(
        project=project,
        name="Project Member",
        permissions_json={
            "can_view_project": True,
        },
    )

    # ---- Assign Creator ----
    ProjectUser.objects.create(
        project=project,
        company_user=creator_company_user,
        role=admin_role,
        is_active=True,
    )

    return {
        "admin_role": admin_role,
        "member_role": member_role,
    }
