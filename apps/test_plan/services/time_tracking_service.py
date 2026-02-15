from django.db import transaction
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone

from apps.test_plan.models import (
    PlanningItem,
    TimeTrackingSession,
)

from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import require_project_permission
from apps.test_plan.services.guards import ensure_test_planning_enabled

@transaction.atomic
def start_time_tracking(*, item, user):

    project = item.project

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_track_time")

    # 1️⃣ Must be assigned user
    if not item.assigned_users.filter(id=project_user.id).exists():
        raise PermissionDenied("Only assigned users can track time.")

    rule = item.entity_type.time_tracking_rule

    if not rule:
        raise ValidationError("Time tracking rule not configured.")

    if rule.start_mode != "MANUAL":
        raise ValidationError("Manual start not allowed for this entity.")

    # 2️⃣ Prevent parallel sessions
    active_sessions = TimeTrackingSession.objects.filter(
        planning_item=item,
        user=project_user,
        ended_at__isnull=True,
    )

    if active_sessions.exists() and not rule.allow_multiple_sessions:
        raise ValidationError("Active time session already exists.")

    session = TimeTrackingSession.objects.create(
        planning_item=item,
        user=project_user,
        started_at=timezone.now(),
    )

    return session

@transaction.atomic
def stop_time_tracking(*, item, user):

    project = item.project

    ensure_test_planning_enabled(project)

    project_user = get_project_user(project, user)
    require_project_permission(project_user, "can_track_time")

    rule = item.entity_type.time_tracking_rule

    if not rule:
        raise ValidationError("Time tracking rule not configured.")

    if rule.stop_mode != "MANUAL":
        raise ValidationError("Manual stop not allowed for this entity.")

    session = TimeTrackingSession.objects.filter(
        planning_item=item,
        user=project_user,
        ended_at__isnull=True,
    ).order_by("-started_at").first()

    if not session:
        raise ValidationError("No active session found.")

    session.ended_at = timezone.now()
    session.duration_seconds = int(
        (session.ended_at - session.started_at).total_seconds()
    )
    session.save(update_fields=["ended_at", "duration_seconds"])

    return session

def list_time_sessions(*, item, user):

    project = item.project

    ensure_test_planning_enabled(project)

    get_project_user(project, user)

    return TimeTrackingSession.objects.filter(
        planning_item=item
    ).order_by("-started_at")
