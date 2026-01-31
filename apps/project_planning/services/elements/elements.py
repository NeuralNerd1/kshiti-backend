from rest_framework.exceptions import ValidationError

from apps.project_planning.models import Element
from apps.project_planning.services.test_case_guards import (
    ensure_can_create_test_cases,
)
from apps.project_planning.models import (
    Element,
    ElementLocator,
)
from django.db import transaction

def create_element(
    *,
    user,
    project,
    folder,
    name,
    page_url="",
):
    ensure_can_create_test_cases(user, project)

    if Element.objects.filter(
        project=project, name=name
    ).exists():
        raise ValidationError("Element already exists")

    return Element.objects.create(
        project=project,
        folder=folder,
        name=name,
        page_url=page_url,
    )


@transaction.atomic
@transaction.atomic
def update_element(
    *,
    user,
    element,
    name=None,
    page_url=None,
    locators_payload=None,
):
    """
    Update element metadata and locators.
    Duplicate element names are allowed.
    """

    ensure_can_create_test_cases(user, element.project)

    # ----------------------------
    # Update element fields
    # ----------------------------
    if name is not None:
        element.name = name

    if page_url is not None:
        element.page_url = page_url

    element.save()

    # ----------------------------
    # Locator updates
    # ----------------------------
    if not locators_payload:
        return element

    # UPDATE
    for item in locators_payload.get("update", []):
        locator = ElementLocator.objects.filter(
            id=item.get("id"),
            element=element,
        ).first()

        if not locator:
            continue

        if "selector_type" in item:
            locator.selector_type = item["selector_type"]

        if "selector_value" in item:
            locator.selector_value = item["selector_value"]

        locator.save()

    # CREATE
    for item in locators_payload.get("create", []):
        if item.get("selector_type") and item.get("selector_value"):
            ElementLocator.objects.create(
                element=element,
                selector_type=item["selector_type"],
                selector_value=item["selector_value"],
            )

    # DELETE
    delete_ids = locators_payload.get("delete", [])
    if delete_ids:
        ElementLocator.objects.filter(
            id__in=delete_ids,
            element=element,
        ).delete()

    return element


def delete_element(*, user, element):
    ensure_can_create_test_cases(user, element.project)
    element.delete()
