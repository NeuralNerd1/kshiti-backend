from rest_framework import serializers


class WorkflowTransitionRequestSerializer(serializers.Serializer):
    target_state_id = serializers.IntegerField()
