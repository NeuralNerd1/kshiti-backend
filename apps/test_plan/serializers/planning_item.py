from rest_framework import serializers
from apps.test_plan.models import PlanningItem, PlanningEntityType
from apps.company_operations.models import ProjectUser


# ----------------------------
# OUTPUT SERIALIZER
# ----------------------------
class PlanningItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlanningItem
        fields = "__all__"
        read_only_fields = [
            "project",
            "path",
            "status",
            "created_by",
            "created_at",
            "updated_at",
        ]


# ----------------------------
# INPUT SERIALIZER (CREATE)
# ----------------------------
class PlanningItemCreateSerializer(serializers.Serializer):

    entity_type = serializers.PrimaryKeyRelatedField(
        queryset=PlanningEntityType.objects.all()
    )

    parent = serializers.PrimaryKeyRelatedField(
        queryset=PlanningItem.objects.all(),
        required=False,
        allow_null=True,
    )

    owner = serializers.PrimaryKeyRelatedField(
        queryset=ProjectUser.objects.all()
    )

    assigned_users = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=ProjectUser.objects.all()
        ),
        required=False,
        allow_empty=True,
    )

    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    field_values = serializers.DictField(required=False)

    def validate(self, data):

        if data.get("start_date") and data.get("end_date"):
            if data["end_date"] < data["start_date"]:
                raise serializers.ValidationError(
                    "End date cannot be before start date."
                )

        return data
