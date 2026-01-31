# apps/project_planning/services/_guards.py

from rest_framework.exceptions import PermissionDenied
from apps.company_operations.permissions import (
    CAN_CREATE_FLOWS,
    CAN_EDIT_FLOWS,
    CAN_VIEW_FLOWS,
)
from apps.company_operations.services.feature3_access import (
    enforce_feature3_permission,
)


def ensure_flows_enabled(project):
    if not project.flows_enabled:
        raise PermissionDenied("Flows are disabled for this project")


def ensure_can_create_flows(user, project):
    enforce_feature3_permission(
        project=project,
        user=user,
        permission_key=CAN_CREATE_FLOWS,
    )


def ensure_can_edit_flows(user, project):
    enforce_feature3_permission(
        project=project,
        user=user,
        permission_key=CAN_EDIT_FLOWS,
    )


def ensure_can_view_flows(user, project):
    enforce_feature3_permission(
        project=project,
        user=user,
        permission_key=CAN_VIEW_FLOWS,
    )
