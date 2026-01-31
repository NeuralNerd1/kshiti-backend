from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.project_planning.models import FlowFolder, Flow
from ._guards import (
    ensure_flows_enabled,
    ensure_can_create_flows,
    ensure_can_edit_flows,
)


def _build_path(parent, name):
    if parent:
        return f"{parent.path}/{name}"
    return name


@transaction.atomic
def create_folder(*, user, project, name, parent_id=None):
    ensure_flows_enabled(project)
    ensure_can_create_flows(user, project)

    parent = None
    if parent_id:
        try:
            parent = FlowFolder.objects.get(id=parent_id, project=project)
        except FlowFolder.DoesNotExist:
            raise ValidationError("Invalid parent folder")

    path = _build_path(parent, name)

    if FlowFolder.objects.filter(project=project, path=path).exists():
        raise ValidationError("Folder already exists at this level")

    return FlowFolder.objects.create(
        project=project,
        name=name,
        parent=parent,
        path=path,
    )


@transaction.atomic
def rename_folder(*, user, folder, new_name):
    ensure_flows_enabled(folder.project)
    ensure_can_edit_flows(user, folder.project)

    old_path = folder.path
    new_path = _build_path(folder.parent, new_name)

    if FlowFolder.objects.filter(
        project=folder.project, path=new_path
    ).exclude(id=folder.id).exists():
        raise ValidationError("Folder with this name already exists")

    folder.name = new_name
    folder.path = new_path
    folder.save(update_fields=["name", "path"])

    # Update child paths
    children = FlowFolder.objects.filter(path__startswith=f"{old_path}/")
    for child in children:
        child.path = child.path.replace(old_path, new_path, 1)
        child.save(update_fields=["path"])

    return folder


@transaction.atomic
def delete_folder(*, user, folder):
    ensure_flows_enabled(folder.project)
    ensure_can_edit_flows(user, folder.project)

    if folder.children.exists():
        raise ValidationError("Folder is not empty")

    if Flow.objects.filter(folder=folder).exists():
        raise ValidationError("Folder contains flows")

    folder.delete()
