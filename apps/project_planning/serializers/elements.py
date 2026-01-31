from rest_framework import serializers
from apps.project_planning.models import (
    ElementFolder,
    Element,
    ElementLocator,
)


class ElementFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementFolder
        fields = ["id", "name", "parent", "path"]


class ElementLocatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementLocator
        fields = [
            "id",
            "selector_type",
            "selector_value",
            "priority",
            "is_active",
        ]


class ElementSerializer(serializers.ModelSerializer):
    locators = ElementLocatorSerializer(many=True, read_only=True)

    class Meta:
        model = Element
        fields = [
            "id",
            "name",
            "page_url",
            "folder",
            "created_at",
            "locators",
        ]
