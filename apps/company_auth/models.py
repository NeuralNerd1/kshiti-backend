from django.db import models
from django.contrib.auth.models import User


# ADDITIVE — do not touch existing fields


class Company(models.Model):
    STATUS_CREATED = "CREATED"
    STATUS_ACTIVE = "ACTIVE"
    STATUS_SUSPENDED = "SUSPENDED"
    STATUS_EXPIRED = "EXPIRED"
    STATUS_DELETED = "DELETED"

    STATUS_CHOICES = [
        (STATUS_CREATED, "Created"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_SUSPENDED, "Suspended"),
        (STATUS_EXPIRED, "Expired"),
        (STATUS_DELETED, "Deleted"),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
    )

    can_create_projects = models.BooleanField(default=False)
    max_projects = models.PositiveIntegerField(default=0)
    custom_roles_enabled = models.BooleanField(default=False)
    project_creation_disabled_reason = models.TextField(
        null=True, blank=True
    )

    is_login_allowed = models.BooleanField(default=False)
    session_version = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CompanyUser(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="company_users",
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="company_membership",
    )

    role = models.ForeignKey(
        "company_operations.Role",
        on_delete=models.PROTECT,
        related_name="company_users",
    )

    is_active = models.BooleanField(default=True)

    def has_project_permission(self, project, permission_key: str) -> bool:
   
        return False





class AuthAuditLog(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True)
