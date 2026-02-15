from rest_framework import serializers
from apps.test_plan.models import PlanningEntityType
import re


class EntityTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlanningEntityType
        fields = [
            "id",
            "internal_key",
            "display_name",
            "level_order",
            "allow_children",
            "allow_execution_binding",
            "allow_dependencies",
            "allow_time_tracking",
        ]
        read_only_fields = ["id"]

    def validate_internal_key(self, value):
        value = value.strip()
        if not re.match(r"^[a-z0-9_]+$", value):
            raise serializers.ValidationError(
                "internal_key must be lowercase alphanumeric with underscores."
            )
        return value

    def validate_display_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("display_name cannot be empty.")
        return value

    def validate_level_order(self, value):
        if value <= 0:
            raise serializers.ValidationError("level_order must be positive.")
        return value
