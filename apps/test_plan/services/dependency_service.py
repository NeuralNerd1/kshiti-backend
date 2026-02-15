from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied

from apps.test_plan.models import (
    PlanningDependency,
    PlanningItem,
)

from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import require_project_permission
from apps.test_plan.services.guards import ensure_test_planning_enabled

@transaction.atomic
def create_dependency(*, source_item, target_item, dependency_type, user):

    project = source_item.project

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_planning_items")

    # 1️⃣ Cross project prevention
    if target_item.project_id != project.id:
        raise ValidationError("Cannot create cross-project dependency.")

    # 2️⃣ Self dependency prevention
    if source_item.id == target_item.id:
        raise ValidationError("Item cannot depend on itself.")

    # 3️⃣ Prevent duplicates
    if PlanningDependency.objects.filter(
        source_item=source_item,
        target_item=target_item,
    ).exists():
        raise ValidationError("Dependency already exists.")

    # 4️⃣ Circular detection
    if _creates_circular_dependency(source_item, target_item):
        raise ValidationError("Circular dependency detected.")

    return PlanningDependency.objects.create(
        source_item=source_item,
        target_item=target_item,
        dependency_type=dependency_type,
    )

@transaction.atomic
def delete_dependency(*, dependency, user):

    project = dependency.source_item.project

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_edit_planning_items")

    dependency.delete()

def _creates_circular_dependency(source_item, target_item):

    visited = set()

    def dfs(item):
        if item.id in visited:
            return False

        visited.add(item.id)

        if item.id == source_item.id:
            return True

        dependencies = PlanningDependency.objects.filter(
            source_item=item
        ).values_list("target_item_id", flat=True)

        for target_id in dependencies:
            next_item = PlanningItem.objects.filter(id=target_id).first()
            if next_item and dfs(next_item):
                return True

        return False

    return dfs(target_item)
