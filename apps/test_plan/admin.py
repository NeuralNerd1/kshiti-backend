from django.contrib import admin
from .models import (
    ProcessTemplate,
    PlanningEntityType,
    EntityFieldDefinition,
    WorkflowDefinition,
    WorkflowState,
    WorkflowTransition,
    TimeTrackingRule,
    PlanningItem,
    PlanningDependency,
    ExecutionBinding,
    TimeTrackingSession,
)

class EntityFieldInline(admin.TabularInline):
    model = EntityFieldDefinition
    extra = 0

class WorkflowStateInline(admin.TabularInline):
    model = WorkflowState
    extra = 0

class WorkflowTransitionInline(admin.TabularInline):
    model = WorkflowTransition
    extra = 0

class WorkflowDefinitionAdmin(admin.ModelAdmin):
    inlines = [WorkflowStateInline, WorkflowTransitionInline]

class TimeTrackingInline(admin.StackedInline):
    model = TimeTrackingRule
    extra = 0

class PlanningEntityTypeAdmin(admin.ModelAdmin):
    inlines = [EntityFieldInline, TimeTrackingInline]

@admin.register(ProcessTemplate)
class ProcessTemplateAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "company",
        "version_number",
        "status",
        "is_locked",
        "created_at",
    )

    list_filter = ("company", "status")

    search_fields = ("name",)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_locked:
            return False
        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj and obj.is_locked:
            return False
        return super().has_change_permission(request, obj)

@admin.register(PlanningItem)
class PlanningItemAdmin(admin.ModelAdmin):
    readonly_fields = [field.name for field in PlanningItem._meta.fields]
    list_display = ("id", "project", "entity_type", "status")


@admin.register(PlanningDependency)
class PlanningDependencyAdmin(admin.ModelAdmin):
    readonly_fields = [field.name for field in PlanningDependency._meta.fields]


@admin.register(ExecutionBinding)
class ExecutionBindingAdmin(admin.ModelAdmin):
    readonly_fields = [field.name for field in ExecutionBinding._meta.fields]


@admin.register(TimeTrackingSession)
class TimeTrackingSessionAdmin(admin.ModelAdmin):
    readonly_fields = [field.name for field in TimeTrackingSession._meta.fields]

