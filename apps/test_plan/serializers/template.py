from rest_framework import serializers
from apps.test_plan.models import ProcessTemplate

class TemplateCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProcessTemplate
        fields = ["name", "description"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Template name cannot be empty.")
        return value

class TemplateDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProcessTemplate
        fields = [
            "id",
            "name",
            "description",
            "version_number",
            "status",
            "is_locked",
            "created_by",
            "reviewer",
            "rejection_note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

