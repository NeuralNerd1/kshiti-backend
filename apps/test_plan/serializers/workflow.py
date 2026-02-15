from rest_framework import serializers
from apps.test_plan.models import (
    WorkflowDefinition,
    WorkflowState,
    WorkflowTransition,
)

class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowDefinition
        fields = ["id", "entity_type", "initial_state"]
        read_only_fields = ["id", "entity_type"]

class WorkflowStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowState
        fields = ["id", "name", "is_final", "order"]
        read_only_fields = ["id"]

class WorkflowTransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowTransition
        fields = ["id", "from_state", "to_state", "allowed_roles"]
        read_only_fields = ["id"]

    def validate_allowed_roles(self, value):
        from apps.company_operations.project_permissions import PROJECT_PERMISSION_KEYS
        invalid = set(value) - PROJECT_PERMISSION_KEYS
        if invalid:
            raise serializers.ValidationError(
                f"Invalid roles: {', '.join(invalid)}"
            )
        return value

