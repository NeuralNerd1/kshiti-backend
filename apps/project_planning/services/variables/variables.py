from rest_framework.exceptions import ValidationError

from apps.project_planning.models import Variable
from apps.project_planning.services.test_case_guards import (
    ensure_can_create_test_cases,
)


def create_variable(
    *,
    user,
    project,
    folder,
    key,
    value,
    description="",
):
    ensure_can_create_test_cases(user, project)

    if Variable.objects.filter(
        project=project, key=key
    ).exists():
        raise ValidationError("Variable already exists")

    return Variable.objects.create(
        project=project,
        folder=folder,
        key=key,
        value=value,
        description=description,
    )


def update_variable(*, user, variable, value, description=None):
    ensure_can_create_test_cases(user, variable.project)

    variable.value = value
    if description is not None:
        variable.description = description

    variable.save(update_fields=["value", "description", "updated_at"])
    return variable


def delete_variable(*, user, variable):
    ensure_can_create_test_cases(user, variable.project)
    variable.delete()
