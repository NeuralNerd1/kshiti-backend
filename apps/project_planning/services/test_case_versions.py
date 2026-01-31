from django.core.exceptions import ValidationError
from django.db import transaction

from apps.project_planning.models import (
    TestCase,
    TestCaseVersion,
)


@transaction.atomic
def create_test_case_version(
    *,
    test_case: TestCase,
    pre_conditions,
    steps,
    expected_outcomes,
):
    """
    Create a new immutable test case version.
    """

    if test_case.status == TestCase.STATUS_ARCHIVED:
        raise ValidationError(
            "Cannot modify an archived test case"
        )

    # -----------------------------
    # STRUCTURE VALIDATION
    # -----------------------------

    if not isinstance(pre_conditions, list):
        raise ValidationError(
            "pre_conditions must be a list"
        )

    if not isinstance(steps, list):
        raise ValidationError(
            "steps must be a list"
        )

    if not isinstance(expected_outcomes, list):
        raise ValidationError(
            "expected_outcomes must be a list"
        )

    # -----------------------------
    # VERSION CALCULATION
    # -----------------------------

    latest = (
        TestCaseVersion.objects.filter(test_case=test_case)
        .order_by("-version_number")
        .first()
    )

    next_version = 1
    created_from = None

    if latest:
        next_version = latest.version_number + 1
        created_from = latest.version_number

    # -----------------------------
    # VERSION CREATION
    # -----------------------------

    version = TestCaseVersion.objects.create(
        test_case=test_case,
        version_number=next_version,
        pre_conditions_json=pre_conditions,
        steps_json=steps,
        expected_outcomes_json=expected_outcomes,
        created_from_version=created_from,
    )

    test_case.current_version = next_version
    test_case.status = TestCase.STATUS_SAVED
    test_case.save(
        update_fields=["current_version", "status"]
    )

    return version
