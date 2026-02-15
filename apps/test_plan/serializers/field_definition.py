from rest_framework import serializers
from apps.test_plan.models import EntityFieldDefinition
import re


class FieldDefinitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = EntityFieldDefinition
        fields = [
            "id",
            "field_key",
            "display_name",
            "field_type",
            "is_required",
            "is_execution_field",
            "is_editable",
            "order",
            "options_json",
            "default_value_json",
        ]
        read_only_fields = ["id"]

    def validate_field_key(self, value):
        value = value.strip()
        if not re.match(r"^[a-z0-9_]+$", value):
            raise serializers.ValidationError(
                "field_key must be lowercase alphanumeric with underscores."
            )
        return value

    def validate_display_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("display_name cannot be empty.")
        return value

    def validate_order(self, value):
        if value < 0:
            raise serializers.ValidationError("order must be zero or positive.")
        return value
