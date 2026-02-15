# backend/apps/test_plan/services/template_bootstrap_service.py

from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied

from apps.test_plan.models import (
    PlanningEntityType,
    EntityFieldDefinition,
    WorkflowDefinition,
    WorkflowState,
    TimeTrackingRule,
    ProcessTemplate,
)

from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import require_project_permission
from apps.test_plan.services.guards import ensure_test_planning_enabled


@transaction.atomic
def bootstrap_default_template_structure(*, project, template, user):

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_templates")

    if template.company_id != project.company_id:
        raise PermissionDenied("Company mismatch.")

    if template.status != ProcessTemplate.STATUS_DRAFT:
        raise ValidationError("Bootstrap allowed only for DRAFT templates.")

    if template.is_locked:
        raise ValidationError("Cannot bootstrap locked template.")

    if template.entity_types.exists():
        raise ValidationError("Template already initialized.")

    summary = {
        "entities_created": 0,
        "fields_created": 0,
        "workflows_created": 0,
        "time_rules_created": 0,
    }

    # -------------------------------------------------
    # DEFAULT ENTITY BLUEPRINT
    # -------------------------------------------------

    entity_blueprint = [
        {
            "internal_key": "sprint",
            "display_name": "Sprint",
            "level_order": 1,
            "allow_children": True,
            "allow_execution_binding": False,
            "allow_dependencies": True,
            "allow_time_tracking": False,
            "fields": [
                ("title", "Title", "text", True),
                ("description", "Description", "long_text", False),
                ("duration", "Duration", "number", False),
                ("epic_linked", "Epic Linked", "json", False),
            ],
        },
        {
            "internal_key": "epic",
            "display_name": "Epic",
            "level_order": 2,
            "allow_children": True,
            "allow_execution_binding": False,
            "allow_dependencies": True,
            "allow_time_tracking": False,
            "fields": [
                ("name", "Name", "text", True),
                ("description", "Description", "long_text", False),
                ("link_sprint", "Link Sprint", "json", False),
                ("stories_linked", "Stories Linked", "json", False),
                ("level_1_connected", "Level 1 Connected", "json", False),
            ],
        },
        {
            "internal_key": "story",
            "display_name": "Story",
            "level_order": 3,
            "allow_children": True,
            "allow_execution_binding": False,
            "allow_dependencies": True,
            "allow_time_tracking": False,
            "fields": [
                ("story_description", "Story Description", "long_text", True),
                ("sprint_link", "Sprint Link", "json", False),
                ("epic_link", "Epic Link", "json", False),
                ("tasks_linked", "Tasks Linked", "json", False),
            ],
        },
        {
            "internal_key": "task",
            "display_name": "Task",
            "level_order": 4,
            "allow_children": False,
            "allow_execution_binding": True,
            "allow_dependencies": True,
            "allow_time_tracking": True,
            "fields": [
                ("task_description", "Task Description", "long_text", True),
                ("start_time", "Start Time", "datetime", False),
                ("end_time", "End Time", "datetime", False),
                ("story_link", "Story Link", "json", False),
            ],
        },
    ]

    # -------------------------------------------------
    # CREATE ENTITIES + FIELDS + WORKFLOWS
    # -------------------------------------------------

    for entity_data in entity_blueprint:

        fields = entity_data.pop("fields")

        entity = PlanningEntityType.objects.create(
            template=template,
            **entity_data,
        )

        summary["entities_created"] += 1

        # Create Fields
        order_counter = 1
        for key, label, field_type, required in fields:

            EntityFieldDefinition.objects.create(
                entity_type=entity,
                field_key=key,
                display_name=label,
                field_type=field_type,
                is_required=required,
                order=order_counter,
            )

            order_counter += 1
            summary["fields_created"] += 1

        # Create Workflow
        workflow = WorkflowDefinition.objects.create(
            entity_type=entity
        )

        backlog = WorkflowState.objects.create(
            workflow=workflow,
            name="Backlog",
            order=1,
        )

        in_progress = WorkflowState.objects.create(
            workflow=workflow,
            name="In Progress",
            order=2,
        )

        done = WorkflowState.objects.create(
            workflow=workflow,
            name="Done",
            order=3,
            is_final=True,
        )

        workflow.initial_state = backlog
        workflow.save(update_fields=["initial_state"])

        summary["workflows_created"] += 1

        # Time Tracking for Task
        if entity.allow_time_tracking:
            TimeTrackingRule.objects.create(
                entity_type=entity,
                start_mode="MANUAL",
                stop_mode="MANUAL",
                allow_multiple_sessions=False,
            )
            summary["time_rules_created"] += 1

    return summary
