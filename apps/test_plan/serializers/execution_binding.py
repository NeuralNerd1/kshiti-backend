from rest_framework import serializers
from apps.test_plan.models import ExecutionBinding
from apps.project_planning.models import Flow, TestCase


class ExecutionBindingCreateSerializer(serializers.Serializer):

    flow_id = serializers.IntegerField(required=False)
    test_case_id = serializers.IntegerField(required=False)

    execution_mode = serializers.CharField(required=False, allow_blank=True)
    auto_trigger = serializers.BooleanField(required=False)


class ExecutionBindingSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExecutionBinding
        fields = "__all__"
