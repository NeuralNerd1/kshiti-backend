from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.project_planning.models import Flow, FlowFolder
from ._guards import (
    ensure_flows_enabled,
    ensure_can_create_flows,
    ensure_can_edit_flows,
)


@transaction.atomic
@transaction.atomic
def create_flow(
    *,
    user,
    project,
    name,
    description="",
    folder=None,
    folder_id=None,
):
    """
    Create a new Flow (metadata only).
    Folder is optional.
    Accepts either:
      - folder (FlowFolder instance) [preferred]
      - folder_id (legacy / external callers)
    """

    ensure_flows_enabled(project)
    ensure_can_create_flows(user, project)

    existing = Flow.objects.filter(
    project=project,
    name=name,
    folder=folder,
)

    if existing.exists():
        raise ValidationError(
            "Flow with this name already exists in this folder"
        )


    # Resolve folder safely
    if folder is not None:
        if folder.project_id != project.id:
            raise ValidationError("Folder does not belong to this project")

    elif folder_id is not None:
        try:
            folder = FlowFolder.objects.get(
                id=folder_id,
                project=project,
            )
        except FlowFolder.DoesNotExist:
            raise ValidationError("Invalid folder for this project")

    flow = Flow.objects.create(
        project=project,
        folder=folder,
        name=name,
        description=description,
        status=Flow.STATUS_DRAFT,
        current_version=1,
    )

    return flow


def update_flow_metadata(*, user, flow, name=None, description=None):
    ensure_flows_enabled(flow.project)
    ensure_can_edit_flows(user, flow.project)

    if flow.status == flow.STATUS_ARCHIVED:
        raise ValidationError("Cannot edit archived flow")

    if name:
        flow.name = name

    if description is not None:
        flow.description = description

    flow.save(update_fields=["name", "description", "updated_at"])
    return flow


def delete_flow(*, user, flow):
    ensure_flows_enabled(flow.project)
    ensure_can_edit_flows(user, flow.project)

    if flow.versions.exists():
        raise ValidationError(
            "Flow with versions cannot be deleted. Archive instead."
        )

    flow.delete()


def archive_flow(*, user, flow):
    ensure_flows_enabled(flow.project)
    ensure_can_edit_flows(user, flow.project)

    if flow.status == Flow.STATUS_ARCHIVED:
        raise ValidationError("Flow already archived")

    flow.archive()
    return flow


# =====================================================
# READ HELPERS (NON-MUTATING)
# =====================================================

def get_flows_for_folder_tree(*, folder):
    """
    Returns flows directly under a folder AND all its subfolders.
    Used for folder-scoped views.
    """
    return Flow.objects.filter(
        folder__path__startswith=folder.path
    )
