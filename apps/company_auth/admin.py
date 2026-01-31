from django.contrib import admin
from django.contrib.auth.models import User
from .models import Company, CompanyUser, AuthAuditLog
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Q

from .models import CompanyUser
from apps.company_operations.models import Role

admin.site.unregister(User)

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Use email as the main identifier
    ordering = ("email",)
    list_display = ("email", "is_active", "is_staff", "is_superuser")
    search_fields = ("email",)

    # Hide username from admin forms
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )

    def save_model(self, request, obj, form, change):
        # Auto-fill username from email if empty
        if not obj.username:
            obj.username = obj.email
        super().save_model(request, obj, form, change)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "status",
        "is_login_allowed",
        "session_version",
        "created_at",
    )
    readonly_fields = ("session_version", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("status", "is_login_allowed")


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "role")
    list_filter = ("company",)
    search_fields = ("user__email", "user__username")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Show:
        - System roles
        - Company-specific roles for the selected company
        """
        if db_field.name == "role":
            try:
                # When editing an existing CompanyUser
                object_id = request.resolver_match.kwargs.get("object_id")
                if object_id:
                    company_user = CompanyUser.objects.filter(
                        pk=object_id
                    ).first()
                    if company_user:
                        kwargs["queryset"] = Role.objects.filter(
                            Q(is_system_role=True)
                            | Q(company=company_user.company)
                        )
                else:
                    # Add form: show system roles by default
                    kwargs["queryset"] = Role.objects.filter(
        Q(is_system_role=True) | Q(company__isnull=False)
    )
            except Exception:
                kwargs["queryset"] = Role.objects.filter(
                    is_system_role=True
                )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(AuthAuditLog)
class AuthAuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "company", "user", "timestamp")
    readonly_fields = ("action", "company", "user", "timestamp", "metadata")
