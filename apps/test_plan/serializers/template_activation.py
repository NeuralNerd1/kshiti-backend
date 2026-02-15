from rest_framework import serializers
from apps.test_plan.models import ProjectTemplateBinding


class ProjectTemplateBindingSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectTemplateBinding
        fields = [
            "id",
            "template",
            "is_active",
            "activated_by",
            "activated_at",
        ]
        read_only_fields = fields
