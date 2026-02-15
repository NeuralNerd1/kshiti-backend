from rest_framework import serializers
from apps.test_plan.models import PlanningDependency, PlanningItem


class DependencyCreateSerializer(serializers.Serializer):

    target_item_id = serializers.IntegerField()
    dependency_type = serializers.ChoiceField(
        choices=PlanningDependency.DEP_TYPES
    )

class DependencySerializer(serializers.ModelSerializer):

    class Meta:
        model = PlanningDependency
        fields = "__all__"
