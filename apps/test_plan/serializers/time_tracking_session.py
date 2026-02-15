from rest_framework import serializers
from apps.test_plan.models import TimeTrackingSession


class TimeTrackingSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimeTrackingSession
        fields = [
            "id",
            "user",
            "started_at",
            "ended_at",
            "duration_seconds",
        ]
        read_only_fields = fields
