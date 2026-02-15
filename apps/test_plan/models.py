from django.db import models

# Create your models here.
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.company_auth.models import CompanyUser
from apps.company_operations.models import Project
from apps.project_planning.models import Flow, TestCase
from apps.company_operations.models import ProjectUser

class ProcessTemplate(models.Model):

    STATUS_DRAFT = "DRAFT"
    STATUS_SUBMITTED = "SUBMITTED"
    STATUS_APPROVAL_PENDING = "APPROVAL_PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_CREATED = "CREATED"
    STATUS_REJECTED = "REJECTED"
    STATUS_ACTIVATED = "ACTIVATED"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_APPROVAL_PENDING, "Approval Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_CREATED, "Created"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_ACTIVATED, "Activated"),
    ]

    company = models.ForeignKey(
        "company_auth.Company",
        on_delete=models.CASCADE,
        related_name="process_templates",
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    version_number = models.PositiveIntegerField(default=1)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )

    created_by = models.ForeignKey(
        CompanyUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_process_templates",
    )

    reviewer = models.ForeignKey(
        CompanyUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewing_process_templates",
    )

    rejection_note = models.TextField(blank=True, null=True)

    is_locked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def lock(self):
        self.is_locked = True
        self.save(update_fields=["is_locked"])

    def clean(self):
        if self.status == self.STATUS_CREATED:
            self.is_locked = True

class PlanningEntityType(models.Model):

    template = models.ForeignKey(
        ProcessTemplate,
        on_delete=models.CASCADE,
        related_name="entity_types",
    )

    internal_key = models.CharField(max_length=100)
    display_name = models.CharField(max_length=255)

    level_order = models.PositiveIntegerField()

    allow_children = models.BooleanField(default=True)
    allow_execution_binding = models.BooleanField(default=False)
    allow_dependencies = models.BooleanField(default=False)
    allow_time_tracking = models.BooleanField(default=False)

    workflow = models.ForeignKey(
        "WorkflowDefinition",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entity_types",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("template", "level_order")
        ordering = ["level_order"]


class EntityFieldDefinition(models.Model):

    FIELD_TYPES = [
        ("text", "Text"),
        ("long_text", "Long Text"),
        ("number", "Number"),
        ("date", "Date"),
        ("datetime", "DateTime"),
        ("select", "Select"),
        ("multi_select", "Multi Select"),
        ("user", "User"),
        ("multi_user", "Multi User"),
        ("boolean", "Boolean"),
        ("json", "JSON"),
    ]

    entity_type = models.ForeignKey(
        PlanningEntityType,
        on_delete=models.CASCADE,
        related_name="fields",
    )

    field_key = models.CharField(max_length=100)
    display_name = models.CharField(max_length=255)

    field_type = models.CharField(max_length=50, choices=FIELD_TYPES)

    is_required = models.BooleanField(default=False)
    is_execution_field = models.BooleanField(default=False)
    is_editable = models.BooleanField(default=True)

    order = models.PositiveIntegerField(default=0)

    options_json = models.JSONField(blank=True, null=True)
    default_value_json = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

class WorkflowDefinition(models.Model):

    entity_type = models.OneToOneField(
        PlanningEntityType,
        on_delete=models.CASCADE,
        related_name="workflow_definition",
    )

    initial_state = models.ForeignKey(
        "WorkflowState",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    created_at = models.DateTimeField(auto_now_add=True)


class WorkflowState(models.Model):

    workflow = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        related_name="states",
    )

    name = models.CharField(max_length=100)
    is_final = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]


class WorkflowTransition(models.Model):

    workflow = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        related_name="transitions",
    )

    from_state = models.ForeignKey(
        WorkflowState,
        on_delete=models.CASCADE,
        related_name="transitions_from",
    )

    to_state = models.ForeignKey(
        WorkflowState,
        on_delete=models.CASCADE,
        related_name="transitions_to",
    )

    allowed_roles = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

class PlanningDependency(models.Model):

    DEP_TYPES = [
        ("BLOCKS", "Blocks"),
        ("RELATES", "Relates To"),
    ]

    source_item = models.ForeignKey(
        "PlanningItem",
        on_delete=models.CASCADE,
        related_name="outgoing_dependencies",
    )

    target_item = models.ForeignKey(
        "PlanningItem",
        on_delete=models.CASCADE,
        related_name="incoming_dependencies",
    )

    dependency_type = models.CharField(max_length=20, choices=DEP_TYPES)

    created_at = models.DateTimeField(auto_now_add=True)

class TimeTrackingRule(models.Model):

    START_MODES = [
        ("MANUAL", "Manual"),
        ("STATUS_CHANGE", "On Status Change"),
        ("EXECUTION_START", "On Execution Start"),
    ]

    STOP_MODES = [
        ("MANUAL", "Manual"),
        ("STATUS_CHANGE", "On Status Change"),
        ("EXECUTION_END", "On Execution End"),
    ]

    entity_type = models.OneToOneField(
        PlanningEntityType,
        on_delete=models.CASCADE,
        related_name="time_tracking_rule",
    )

    start_mode = models.CharField(max_length=50, choices=START_MODES)
    stop_mode = models.CharField(max_length=50, choices=STOP_MODES)

    allow_multiple_sessions = models.BooleanField(default=False)

class TimeTrackingSession(models.Model):

    planning_item = models.ForeignKey(
        "PlanningItem",
        on_delete=models.CASCADE,
        related_name="time_sessions",
    )

    user = models.ForeignKey(
        ProjectUser,
        on_delete=models.CASCADE,
    )

    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)

    duration_seconds = models.PositiveIntegerField(default=0)

    def clean(self):
        if self.ended_at and self.ended_at < self.started_at:
            raise ValidationError("End time cannot be before start time.")

class PlanningItem(models.Model):

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="planning_items",
    )

    entity_type = models.ForeignKey(
        PlanningEntityType,
        on_delete=models.CASCADE,
        related_name="planning_items",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    path = models.CharField(max_length=255)

    status = models.ForeignKey(
        WorkflowState,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    owner = models.ForeignKey(
        ProjectUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_planning_items",
    )

    assigned_users = models.ManyToManyField(
        ProjectUser,
        related_name="assigned_planning_items",
        blank=True,
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    created_by = models.ForeignKey(
        ProjectUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_planning_items",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PlanningItemFieldValue(models.Model):

    planning_item = models.ForeignKey(
        PlanningItem,
        on_delete=models.CASCADE,
        related_name="field_values",
    )

    field_definition = models.ForeignKey(
        EntityFieldDefinition,
        on_delete=models.CASCADE,
    )

    value_json = models.JSONField()

class ExecutionBinding(models.Model):

    planning_item = models.OneToOneField(
        PlanningItem,
        on_delete=models.CASCADE,
        related_name="execution_binding",
    )

    flow = models.ForeignKey(
        Flow,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    test_case = models.ForeignKey(
        TestCase,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    execution_mode = models.CharField(max_length=100, blank=True)
    auto_trigger = models.BooleanField(default=False)


class ProjectPlanningConfig(models.Model):

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name="planning_config",
    )

    entity_level_1_name = models.CharField(max_length=255, blank=True)
    entity_level_2_name = models.CharField(max_length=255, blank=True)
    entity_level_3_name = models.CharField(max_length=255, blank=True)
    entity_level_4_name = models.CharField(max_length=255, blank=True)
    entity_level_5_name = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProjectTemplateBinding(models.Model):
    project = models.ForeignKey(
        "company_operations.Project",
        on_delete=models.CASCADE,
        related_name="template_bindings",
    )

    template = models.ForeignKey(
        "test_plan.ProcessTemplate",
        on_delete=models.PROTECT,
        related_name="project_bindings",
    )

    is_active = models.BooleanField(default=True)

    activated_by = models.ForeignKey(
        "company_auth.CompanyUser",
        on_delete=models.PROTECT,
        related_name="activated_templates",
    )

    activated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "template")


class KanbanBoardConfig(models.Model):
    LAYOUT_STANDARD = "STANDARD"
    LAYOUT_COMPACT = "COMPACT"
    LAYOUT_USER_GROUPED = "USER_GROUPED"

    LAYOUT_CHOICES = [
        (LAYOUT_STANDARD, "Standard"),
        (LAYOUT_COMPACT, "Compact"),
        (LAYOUT_USER_GROUPED, "Grouped by User"),
    ]

    THEME_CLASSIC = "CLASSIC"
    THEME_MODERN = "MODERN"
    THEME_HIGH_CONTRAST = "HIGH_CONTRAST"

    THEME_CHOICES = [
        (THEME_CLASSIC, "Classic"),
        (THEME_MODERN, "Modern-Dark"),
        (THEME_HIGH_CONTRAST, "High-Contrast"),
    ]

    DENSITY_COMPACT = "COMPACT"
    DENSITY_COMFORTABLE = "COMFORTABLE"
    DENSITY_SPACIOUS = "SPACIOUS"

    DENSITY_CHOICES = [
        (DENSITY_COMPACT, "Compact"),
        (DENSITY_COMFORTABLE, "Comfortable"),
        (DENSITY_SPACIOUS, "Spacious"),
    ]

    SWIMLANE_NONE = "NONE"
    SWIMLANE_OWNER = "OWNER"
    SWIMLANE_PRIORITY = "PRIORITY"
    SWIMLANE_SECTION = "SECTION"

    SWIMLANE_CHOICES = [
        (SWIMLANE_NONE, "None"),
        (SWIMLANE_OWNER, "Assignee"),
        (SWIMLANE_PRIORITY, "Priority"),
        (SWIMLANE_SECTION, "Section"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="kanban_configs",
        null=True,
    )

    view_key = models.CharField(max_length=100, default="GLOBAL")

    layout_type = models.CharField(
        max_length=50,
        choices=LAYOUT_CHOICES,
        default=LAYOUT_STANDARD
    )

    color_scheme = models.CharField(
        max_length=50,
        choices=THEME_CHOICES,
        default=THEME_MODERN
    )

    card_density = models.CharField(
        max_length=20,
        choices=DENSITY_CHOICES,
        default=DENSITY_COMFORTABLE
    )

    swimlane_attribute = models.CharField(
        max_length=20,
        choices=SWIMLANE_CHOICES,
        default=SWIMLANE_NONE
    )

    zoom_level = models.IntegerField(default=100)
    enable_glass = models.BooleanField(default=True)
    custom_accent_color = models.CharField(max_length=7, default="#7c5cff")

    show_owner = models.BooleanField(default=True)
    show_due_date = models.BooleanField(default=True)

    # JSON field for flexible column mapping or additional settings
    columns_config = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("project", "view_key")
