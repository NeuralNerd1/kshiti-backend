from rest_framework import serializers
from apps.project_planning.models import FlowFolder


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlowFolder
        fields = ["id", "name", "parent", "path"]


class FolderCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    parent_id = serializers.IntegerField(required=False, allow_null=True)


class FolderRenameSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
