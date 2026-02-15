from rest_framework import serializers
from apps.test_plan.models import ProjectPlanningConfig


class ProjectPlanningConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for Project Planning Configuration.
    Handles entity level naming configuration.
    """

    class Meta:
        model = ProjectPlanningConfig
        fields = [
            "id",
            "project",
            "entity_level_1_name",
            "entity_level_2_name",
            "entity_level_3_name",
            "entity_level_4_name",
            "entity_level_5_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "project",
            "created_at",
            "updated_at",
        ]
