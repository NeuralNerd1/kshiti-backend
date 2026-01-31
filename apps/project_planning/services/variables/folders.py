from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.project_planning.models import VariableFolder
from apps.project_planning.services.test_case_guards import (
    ensure_can_create_test_cases,
)


def _build_path(parent, name):
    return f"{parent.path}/{name}" if parent else name


@transaction.atomic
def create_variable_folder(*, user, project, name, parent=None):
    ensure_can_create_test_cases(user, project)

    path = _build_path(parent, name)

    if VariableFolder.objects.filter(
        project=project, path=path
    ).exists():
        raise ValidationError("Folder already exists")

    return VariableFolder.objects.create(
        project=project,
        parent=parent,
        name=name,
        path=path,
    )


@transaction.atomic
def rename_variable_folder(*, user, folder, new_name):
    ensure_can_create_test_cases(user, folder.project)

    old_path = folder.path
    new_path = _build_path(folder.parent, new_name)

    if VariableFolder.objects.filter(
        project=folder.project,
        path=new_path
    ).exclude(id=folder.id).exists():
        raise ValidationError("Folder already exists")

    folder.name = new_name
    folder.path = new_path
    folder.save(update_fields=["name", "path"])

    children = VariableFolder.objects.filter(
        path__startswith=f"{old_path}/"
    )

    for child in children:
        child.path = child.path.replace(old_path, new_path, 1)
        child.save(update_fields=["path"])


def delete_variable_folder(*, user, folder):
    ensure_can_create_test_cases(user, folder.project)

    if folder.children.exists():
        raise ValidationError("Folder not empty")

    if folder.variables.exists():
        raise ValidationError("Folder contains variables")

    folder.delete()
