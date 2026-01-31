from rest_framework import serializers
from apps.project_planning.models import Variable, VariableFolder


class VariableFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariableFolder
        fields = ["id", "name", "parent", "path"]


class VariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variable
        fields = [
            "id",
            "key",
            "value",
            "description",
            "folder",
            "created_at",
            "updated_at",
        ]
