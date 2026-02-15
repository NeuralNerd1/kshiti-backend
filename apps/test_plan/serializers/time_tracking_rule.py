from rest_framework import serializers
from apps.test_plan.models import TimeTrackingRule


class TimeTrackingRuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimeTrackingRule
        fields = [
            "id",
            "start_mode",
            "stop_mode",
            "allow_multiple_sessions",
        ]
        read_only_fields = ["id"]

    def validate(self, data):

        start_mode = data.get("start_mode")
        stop_mode = data.get("stop_mode")

        if start_mode == stop_mode:
            raise serializers.ValidationError(
                "start_mode and stop_mode cannot be identical."
            )

        return data
