from django.core.exceptions import ValidationError
from django.db import transaction

from apps.project_planning.models import TestCaseFolder


# --------------------------------------------------
# CREATE
# --------------------------------------------------

def create_test_case_folder(*, project, name, parent=None):
    if parent:
        if parent.project_id != project.id:
            raise ValidationError(
                "Folder project mismatch"
            )

        if parent.status == TestCaseFolder.STATUS_ARCHIVED:
            raise ValidationError(
                "Cannot create folder under archived folder"
            )

        path = f"{parent.path}/{name}"
    else:
        path = name

    return TestCaseFolder.objects.create(
        project=project,
        parent=parent,
        name=name,
        path=path,
    )


# --------------------------------------------------
# RENAME
# --------------------------------------------------

@transaction.atomic
def rename_test_case_folder(*, folder, new_name):
    if folder.status == TestCaseFolder.STATUS_ARCHIVED:
        raise ValidationError(
            "Cannot rename archived folder"
        )

    old_path = folder.path
    parent_path = (
        folder.parent.path if folder.parent else None
    )

    new_path = (
        f"{parent_path}/{new_name}"
        if parent_path
        else new_name
    )

    folder.name = new_name
    folder.path = new_path
    folder.save(update_fields=["name", "path"])

    descendants = TestCaseFolder.objects.filter(
        path__startswith=f"{old_path}/"
    )

    for child in descendants:
        child.path = child.path.replace(
            old_path,
            new_path,
            1,
        )
        child.save(update_fields=["path"])


# --------------------------------------------------
# MOVE
# --------------------------------------------------

@transaction.atomic
def move_test_case_folder(*, folder, new_parent):
    if folder.status == TestCaseFolder.STATUS_ARCHIVED:
        raise ValidationError(
            "Cannot move archived folder"
        )

    if new_parent.project_id != folder.project_id:
        raise ValidationError(
            "Target folder project mismatch"
        )

    if new_parent.status == TestCaseFolder.STATUS_ARCHIVED:
        raise ValidationError(
            "Cannot move under archived folder"
        )

    old_path = folder.path
    new_path = f"{new_parent.path}/{folder.name}"

    folder.parent = new_parent
    folder.path = new_path
    folder.save(update_fields=["parent", "path"])

    descendants = TestCaseFolder.objects.filter(
        path__startswith=f"{old_path}/"
    )

    for child in descendants:
        child.path = child.path.replace(
            old_path,
            new_path,
            1,
        )
        child.save(update_fields=["path"])


# --------------------------------------------------
# ARCHIVE (SOFT DELETE)
# --------------------------------------------------

def archive_test_case_folder(folder):
    if folder.children.exists():
        raise ValidationError(
            "Cannot archive folder with child folders"
        )

    if folder.test_cases.filter(
        status__in=["DRAFT", "SAVED"]
    ).exists():
        raise ValidationError(
            "Folder contains active test cases"
        )

    folder.archive()
