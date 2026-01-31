from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import (
    Role,
    Project,
    ProjectUser,
    ProjectRole,
)

from apps.company_operations.services.project_bootstrap import (
    bootstrap_project_access,
)


# =====================================================
# COMPANY ROLES (UNCHANGED)
# =====================================================

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "is_system_role", "created_at")
    list_filter = ("is_system_role", "company")
    search_fields = ("name",)
    readonly_fields = ("created_at",)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_system_role:
            return False
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)


# =====================================================
# PROJECT-LEVEL ADMIN (NEW, ADDITIVE)
# =====================================================

class ProjectRoleInline(admin.TabularInline):
    """
    Project-scoped roles (Feature-3).
    """
    model = ProjectRole
    extra = 0
    fields = ("name", "permissions_json")
    show_change_link = True


class ProjectUserInline(admin.TabularInline):
    """
    Project members + their project roles (Feature-3).
    """
    model = ProjectUser
    extra = 0
    autocomplete_fields = ("company_user", "role")
    fields = ("company_user", "role", "is_active")
    show_change_link = True

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "status", "created_at")
    list_filter = ("status", "company")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    actions = ["archive_projects"]

    inlines = [ProjectRoleInline, ProjectUserInline]

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None

        super().save_model(request, obj, form, change)

        # 🔑 AUTO-BOOTSTRAP PROJECT ACCESS FOR ADMIN-CREATED PROJECTS
        if is_new:
            bootstrap_project_access(
                project=obj,
                creator_company_user=obj.project_admin,
            )

    def archive_projects(self, request, queryset):
        for project in queryset:
            project.archive()



# =====================================================
# OPTIONAL: STANDALONE ADMIN PAGES
# (safe to keep or remove)
# =====================================================

@admin.register(ProjectUser)
class ProjectUserAdmin(admin.ModelAdmin):
    list_display = ("project", "company_user", "role", "is_active")
    list_filter = ("project", "is_active")
    search_fields = ("company_user__user__email",)


@admin.register(ProjectRole)
class ProjectRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "project")
    search_fields = ("name",)
