from apps.project_planning.models import ElementLocator
from apps.project_planning.services.test_case_guards import (
    ensure_can_create_test_cases,
)


def create_locator(*, user, element, selector_type, selector_value, priority=0):
    ensure_can_create_test_cases(user, element.project)

    return ElementLocator.objects.create(
        element=element,
        selector_type=selector_type,
        selector_value=selector_value,
        priority=priority,
    )


def update_locator(*, user, locator, **fields):
    ensure_can_create_test_cases(user, locator.element.project)

    for key, value in fields.items():
        setattr(locator, key, value)

    locator.save()
    return locator


def delete_locator(*, user, locator):
    ensure_can_create_test_cases(user, locator.element.project)
    locator.delete()
