from django.core.exceptions import PermissionDenied
from apps.company_operations.permissions import (
    CAN_VIEW_FLOWS,
    CAN_CREATE_FLOWS,
    CAN_EDIT_FLOWS,
)
from apps.company_operations.services.feature3_access import (
    enforce_feature3_permission,
)


def ensure_can_view_folders(user, project):
    enforce_feature3_permission(
        project=project,
        user=user,
        permission_key=CAN_VIEW_FLOWS,
    )


def ensure_can_create_folders(user, project):
    enforce_feature3_permission(
        project=project,
        user=user,
        permission_key=CAN_CREATE_FLOWS,
    )


def ensure_can_edit_folders(user, project):
    enforce_feature3_permission(
        project=project,
        user=user,
        permission_key=CAN_EDIT_FLOWS,
    )
