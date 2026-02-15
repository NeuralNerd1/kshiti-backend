from rest_framework import serializers
from apps.test_plan.models import KanbanBoardConfig

class KanbanBoardConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = KanbanBoardConfig
        fields = [
            "id",
            "project",
            "view_key",
            "layout_type",
            "color_scheme",
            "card_density",
            "swimlane_attribute",
            "zoom_level",
            "enable_glass",
            "custom_accent_color",
            "show_owner",
            "show_due_date",
            "columns_config",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
