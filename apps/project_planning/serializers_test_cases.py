# apps/project_planning/serializers_test_cases.py

from rest_framework import serializers
from apps.project_planning.models import (
    TestCase,
    TestCaseFolder,
    TestCaseVersion,
)


class TestCaseFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCaseFolder
        fields = [
            "id",
            "name",
            "path",
            "parent",
            "status",
            "created_at",
        ]

class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = [
            "id",
            "name",
            "description",
            "status",
            "current_version",
            "folder",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "status",
            "current_version",
            "created_at",
            "updated_at",
        ]


# ======================================================
# VERSION SERIALIZER
# ======================================================

class TestCaseVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCaseVersion
        fields = [
            "version_number",
            "pre_conditions_json",
            "steps_json",
            "expected_outcomes_json",
            "created_from_version",
            "created_at",
        ]