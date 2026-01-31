from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from apps.company_auth.models import Company




User = settings.AUTH_USER_MODEL


class Role(models.Model):
    """
    Role defines a permission bundle.
    System roles have company = NULL.
    Company roles are scoped to a single company.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # IMPORTANT: Correct app label reference
    company = models.ForeignKey(
        "company_auth.Company",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="roles",
    )

    is_system_role = models.BooleanField(default=False)
    permissions_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("company", "name")

    def clean(self):
        from .permissions import ALL_PERMISSION_KEYS

        invalid_keys = set(self.permissions_json.keys()) - ALL_PERMISSION_KEYS
        if invalid_keys:
            raise ValidationError(
                f"Invalid permission keys: {', '.join(invalid_keys)}"
            )

    def delete(self, *args, **kwargs):
        if self.is_system_role:
            raise ValidationError("System roles cannot be deleted.")
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name




class Project(models.Model):
    STATUS_ACTIVE = "ACTIVE"
    STATUS_ARCHIVED = "ARCHIVED"

    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_ARCHIVED, "Archived"),
    )

    company = models.ForeignKey(
        "company_auth.Company",
        on_delete=models.CASCADE,
        related_name="projects",
    )
    max_team_members = models.PositiveIntegerField(default=1)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    project_admin = models.ForeignKey(
    "company_auth.CompanyUser",
    on_delete=models.PROTECT,
    related_name="admin_projects",
)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )

        # =====================================================
    # FEATURE 3 — PLANNING / BUILDER / EXECUTION FLAGS
    # (DECLARATIVE ONLY — NOT ENFORCED YET)
    # =====================================================

    flows_enabled = models.BooleanField(default=False)
    test_cases_enabled = models.BooleanField(default=False)

    builder_enabled = models.BooleanField(default=False)

    execution_enabled = models.BooleanField(default=False)

    reports_enabled = models.BooleanField(default=False)

    can_configure_processes = models.BooleanField(default=False)

    element_capture_enabled = models.BooleanField(default=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["company", "status"]),
        ]
        unique_together = ("company", "name")

    def clean(self):
        if self.max_team_members <= 0:
           raise ValidationError("max_team_members must be greater than zero.")


        if not self.project_admin:
           raise ValidationError("Project admin is required.")

        if self.project_admin.company_id != self.company_id:
           raise ValidationError("Project admin must belong to the same company.")

    def archive(self):
        self.status = self.STATUS_ARCHIVED
        self.save(update_fields=["status", "updated_at"])

    def __str__(self):
        return self.name
    

# =====================================================
# FEATURE 3 — PROJECT-LEVEL ROLE (NEW, ADDITIVE)
# =====================================================

class ProjectRole(models.Model):
    """
    Project-scoped role.
    Permissions apply ONLY within a single project.
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_roles",
    )

    name = models.CharField(max_length=100)
    permissions_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "name")

    def clean(self):
        from .project_permissions import PROJECT_PERMISSION_KEYS

        invalid = set(self.permissions_json.keys()) - PROJECT_PERMISSION_KEYS
        if invalid:
            raise ValidationError(
                f"Invalid project permission keys: {', '.join(invalid)}"
            )

    def __str__(self):
        return f"{self.project.name} — {self.name}"

# =====================================================
# FEATURE 3 — PROJECT MEMBERSHIP (NEW, ADDITIVE)
# =====================================================

class ProjectUser(models.Model):
    """
    Explicit membership of a CompanyUser in a Project.
    This is the ONLY source of truth for Feature-3 access.
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="members",
    )

    company_user = models.ForeignKey(
        "company_auth.CompanyUser",
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )

    role = models.ForeignKey(
        ProjectRole,
        on_delete=models.PROTECT,
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("project", "company_user")

    def __str__(self):
        return f"{self.company_user.user.email} → {self.project.name}"

