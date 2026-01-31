from rest_framework import serializers
from apps.project_planning.models import Flow, FlowVersion


class FlowListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flow
        fields = [
            "id",
            "name",
            "description",
            "status",
            "current_version",
            "folder_id",
            "created_at",
            "updated_at",
        ]


class FlowCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    folder_id = serializers.IntegerField(required=False)


class FlowVersionCreateSerializer(serializers.Serializer):
    steps_json = serializers.ListField()
    created_from_version = serializers.IntegerField(required=False)


class FlowVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlowVersion
        fields = [
            "version_number",
            "steps_json",
            "created_from_version",
            "created_at",
        ]
        
class FlowUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)