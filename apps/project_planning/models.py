from django.db import models
from rest_framework.exceptions import ValidationError
from apps.company_operations.models import Project


# ---------------------------------------------------------
# FLOW FOLDER (TREE STRUCTURE)
# ---------------------------------------------------------

class FlowFolder(models.Model):
    """
    Folder structure for organizing flows inside a project.
    Purely organizational.
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="flow_folders",
    )

    name = models.CharField(max_length=255)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )

    # Materialized path for fast tree queries
    path = models.CharField(max_length=500, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "path")
        ordering = ["path"]

    def __str__(self):
        return f"{self.project_id}:{self.path}"

    def clean(self):
        """
        Enforce path correctness.
        """
        if self.parent:
            if not self.path.startswith(self.parent.path):
                raise ValidationError(
                    "Folder path must start with parent path"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# ---------------------------------------------------------
# FLOW (METADATA ONLY)
# ---------------------------------------------------------

class Flow(models.Model):
    """
    Logical flow entity.
    Contains NO steps directly.
    Steps live in FlowVersion.
    """

    STATUS_DRAFT = "DRAFT"
    STATUS_SAVED = "SAVED"
    STATUS_ARCHIVED = "ARCHIVED"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SAVED, "Saved"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="flows",
    )

    folder = models.ForeignKey(
        FlowFolder,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="flows",
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    current_version = models.PositiveIntegerField(default=1)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
        models.UniqueConstraint(
            fields=["project", "folder", "name"],
            name="uniq_flow_name_per_folder",
        )
    ]
    ordering = ["name"]


    def __str__(self):
        return f"{self.project_id}:{self.name}"

    def archive(self):
        if self.status == self.STATUS_ARCHIVED:
            raise ValidationError("Flow is already archived")
        self.status = self.STATUS_ARCHIVED
        self.save(update_fields=["status"])


# ---------------------------------------------------------
# FLOW VERSION (IMMUTABLE)
# ---------------------------------------------------------

class FlowVersion(models.Model):
    """
    Immutable snapshot of a flow at a point in time.
    """

    flow = models.ForeignKey(
        Flow,
        on_delete=models.CASCADE,
        related_name="versions",
    )

    version_number = models.PositiveIntegerField()

    # Steps are stored as intent-only JSON
    steps_json = models.JSONField()

    created_from_version = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Source version for rollback/copy",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("flow", "version_number")
        ordering = ["-version_number"]

    def __str__(self):
        return f"{self.flow_id}@v{self.version_number}"

    def clean(self):
        """
        Validate shape, NOT execution completeness.
        """
        if not isinstance(self.steps_json, list):
            raise ValidationError("steps_json must be a list")

        for idx, step in enumerate(self.steps_json):
            if not isinstance(step, dict):
                raise ValidationError(
                    f"Step at index {idx} must be an object"
                )

            if "action_key" not in step:
                raise ValidationError(
                    f"Step {idx} missing action_key"
                )

            if "execution_notes" not in step:
                raise ValidationError(
                    f"Step {idx} missing execution_notes"
                )

            if "parameters" not in step:
                raise ValidationError(
                    f"Step {idx} missing parameters"
                )

            if not isinstance(step["parameters"], dict):
                raise ValidationError(
                    f"Step {idx} parameters must be object"
                )

    def save(self, *args, **kwargs):
        # Block modification if parent flow is archived
        if self.flow.status == Flow.STATUS_ARCHIVED:
            raise ValidationError(
                "Cannot create or modify versions of archived flows"
            )

        self.full_clean()
        super().save(*args, **kwargs)


class TestCaseFolder(models.Model):
    STATUS_ACTIVE = "ACTIVE"
    STATUS_ARCHIVED = "ARCHIVED"

    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_ARCHIVED, "Archived"),
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="test_case_folders",
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )

    name = models.CharField(max_length=255)
    path = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["path"]
        unique_together = ("project", "path")

    def clean(self):
        if self.parent and self.parent.project_id != self.project_id:
            raise ValidationError(
                "Parent folder must belong to same project"
            )

        if self.parent and self.parent.status == self.STATUS_ARCHIVED:
            raise ValidationError(
                "Cannot create folder under archived folder"
            )

    def archive(self):
        self.status = self.STATUS_ARCHIVED
        self.save(update_fields=["status"])

    def __str__(self):
        return self.path
    
class TestCase(models.Model):
    STATUS_DRAFT = "DRAFT"
    STATUS_SAVED = "SAVED"
    STATUS_ARCHIVED = "ARCHIVED"

    STATUS_CHOICES = (
        (STATUS_DRAFT, "Draft"),
        (STATUS_SAVED, "Saved"),
        (STATUS_ARCHIVED, "Archived"),
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="test_cases",
    )

    folder = models.ForeignKey(
        TestCaseFolder,
        on_delete=models.PROTECT,
        related_name="test_cases",
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )

    current_version = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("project", "name")

    def archive(self):
        self.status = self.STATUS_ARCHIVED
        self.save(update_fields=["status", "updated_at"])

    def __str__(self):
        return self.name


class TestCaseVersion(models.Model):
    test_case = models.ForeignKey(
        TestCase,
        on_delete=models.CASCADE,
        related_name="versions",
    )

    version_number = models.PositiveIntegerField()

    pre_conditions_json = models.JSONField(default=list)
    steps_json = models.JSONField(default=list)
    expected_outcomes_json = models.JSONField(default=list)

    created_from_version = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-version_number"]
        unique_together = ("test_case", "version_number")

    def __str__(self):
        return f"{self.test_case.name} v{self.version_number}"

# apps/project_planning/models.py

class VariableFolder(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="variable_folders",
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )

    name = models.CharField(max_length=255)
    path = models.TextField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "path")
        ordering = ["path"]

    def __str__(self):
        return self.path
    
class Variable(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="variables",
    )

    folder = models.ForeignKey(
        VariableFolder,
        on_delete=models.PROTECT,
        related_name="variables",
    )

    key = models.CharField(max_length=255)
    value = models.TextField()
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("project", "key")

    def __str__(self):
        return self.key

# ---------------------------------------------------------
# ELEMENTS (OBJECT REPOSITORY)
# ---------------------------------------------------------

class ElementFolder(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="element_folders",
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )

    name = models.CharField(max_length=255)
    path = models.TextField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "path")
        ordering = ["path"]

    def __str__(self):
        return self.path


class Element(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="elements",
    )

    folder = models.ForeignKey(
        ElementFolder,
        on_delete=models.PROTECT,
        related_name="elements",
    )

    name = models.CharField(max_length=255)
    page_url = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.name



class ElementLocator(models.Model):
    element = models.ForeignKey(
        Element,
        on_delete=models.CASCADE,
        related_name="locators",
    )

    selector_type = models.CharField(max_length=50)
    selector_value = models.TextField()

    priority = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["priority", "id"]

    def __str__(self):
        return f"{self.selector_type}"

