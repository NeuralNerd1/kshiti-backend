# backend/apps/test_plan/views/entity_schema.py

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.company_operations.models import Project
from apps.company_operations.services.project_users import get_project_user
from apps.test_plan.models import PlanningEntityType, EntityFieldDefinition
from apps.test_plan.serializers.field_definition import FieldDefinitionSerializer
from apps.test_plan.services.guards import ensure_test_planning_enabled


class EntitySchemaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, entity_type_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        entity_type = get_object_or_404(
            PlanningEntityType.objects.select_related("template"),
            id=entity_type_id,
            template__company=project.company,
        )

        level = entity_type.level_order

        # -------------------------------------------------
        # SYSTEM FIELDS (From PlanningItem Model)
        # -------------------------------------------------

        system_fields = []

        # Common for all levels
        system_fields.append({
            "field_key": "owner",
            "display_name": "Owner",
            "field_type": "user",
            "source": "system",
            "editable": True,
        })

        system_fields.append({
            "field_key": "assigned_users",
            "display_name": "Users",
            "field_type": "user_multi",
            "source": "system",
            "editable": True,
        })

        if level == 1:  # Sprint
            system_fields.extend([
                {
                    "field_key": "start_date",
                    "display_name": "Start Date",
                    "field_type": "date",
                    "source": "system",
                    "editable": True,
                },
                {
                    "field_key": "end_date",
                    "display_name": "End Date",
                    "field_type": "date",
                    "source": "system",
                    "editable": True,
                },
            ])

        if level == 4:  # Task
            system_fields.extend([
                {
                    "field_key": "start_time",
                    "display_name": "Start Time",
                    "field_type": "datetime",
                    "source": "system",
                    "editable": True,
                },
                {
                    "field_key": "end_time",
                    "display_name": "End Time",
                    "field_type": "datetime",
                    "source": "system",
                    "editable": True,
                },
            ])

        # -------------------------------------------------
        # DEFAULT TEMPLATE FIELDS (Created via Bootstrap)
        # -------------------------------------------------

        default_template_keys = {
            1: ["title", "description", "duration", "epic_linked"],
            2: ["name", "description", "link_sprint", "stories_linked", "level_1_connected"],
            3: ["story_description", "sprint_link", "epic_link", "tasks_linked"],
            4: ["task_description", "story_link"],
        }

        default_template_fields = []

        bootstrap_fields = EntityFieldDefinition.objects.filter(
            entity_type=entity_type
        )

        for field in bootstrap_fields:
            if field.field_key in default_template_keys.get(level, []):
                default_template_fields.append({
                    **FieldDefinitionSerializer(field).data,
                    "source": "default_template",
                })

        # -------------------------------------------------
        # CUSTOM FIELDS (User Added After Bootstrap)
        # -------------------------------------------------

        custom_fields = []

        for field in bootstrap_fields:
            if field.field_key not in default_template_keys.get(level, []):
                custom_fields.append({
                    **FieldDefinitionSerializer(field).data,
                    "source": "custom",
                })

        return Response({
            "entity": {
                "id": entity_type.id,
                "display_name": entity_type.display_name,
                "level_order": level,
            },
            "system_fields": system_fields,
            "default_template_fields": default_template_fields,
            "custom_fields": custom_fields,
        })
