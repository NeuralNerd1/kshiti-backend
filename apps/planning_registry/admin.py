# apps/planning_registry/admin.py

from django.contrib import admin
from .models import ActionCategory, ActionDefinition


@admin.register(ActionCategory)
class ActionCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "order")
    ordering = ("order",)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ActionDefinition)
class ActionDefinitionAdmin(admin.ModelAdmin):
    list_display = (
        "action_key",
        "action_name",
        "category",
        "is_risky",
    )
    list_filter = ("category", "is_risky")
    search_fields = ("action_key", "action_name")

    readonly_fields = ("created_at",)

    def has_add_permission(self, request):
        return True  # allow seeding

    def has_change_permission(self, request, obj=None):
        return False  # immutable in prod

    def has_delete_permission(self, request, obj=None):
        return False
