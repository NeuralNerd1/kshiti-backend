# apps/planning_registry/models.py

from django.db import models
from django.core.exceptions import ValidationError


class ActionCategory(models.Model):
    """
    UI + semantic grouping for actions.
    Example: Navigation, Mouse, Assertions, etc.
    """
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class ActionDefinition(models.Model):
    """
    Global immutable definition of an action.
    Used by Flows, Test Cases, Builder, Execution (future).
    """
    action_key = models.CharField(max_length=100, unique=True)
    action_name = models.CharField(max_length=150)

    category = models.ForeignKey(
        ActionCategory,
        on_delete=models.PROTECT,
        related_name="actions",
    )

    description = models.TextField(blank=True)
    is_risky = models.BooleanField(default=False)

    # Core: parameter schema (required vs optional)
    parameter_schema = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["action_key"]

    def clean(self):
        """
        Validate schema shape, NOT completeness.
        """
        schema = self.parameter_schema or {}

        if not isinstance(schema, dict):
            raise ValidationError("parameter_schema must be an object")

        required = schema.get("required", {})
        optional = schema.get("optional", {})

        if not isinstance(required, dict):
            raise ValidationError("schema.required must be an object")

        if not isinstance(optional, dict):
            raise ValidationError("schema.optional must be an object")

        overlap = set(required.keys()) & set(optional.keys())
        if overlap:
            raise ValidationError(
                f"Fields cannot be both required and optional: {overlap}"
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # enforce validation always
        super().save(*args, **kwargs)

    def __str__(self):
        return self.action_key
