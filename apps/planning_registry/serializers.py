from rest_framework import serializers
from .models import ActionCategory, ActionDefinition


class ActionDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionDefinition
        fields = [
            "action_key",
            "action_name",
            "description",
            "is_risky",
            "parameter_schema",
        ]


class ActionCategorySerializer(serializers.ModelSerializer):
    actions = ActionDefinitionSerializer(many=True, read_only=True)

    class Meta:
        model = ActionCategory
        fields = [
            "key",
            "name",
            "order",
            "actions",
        ]
