from rest_framework.exceptions import ValidationError

from apps.project_planning.models import TestCase
from apps.project_planning.services.test_case_guards import (
    ensure_test_cases_enabled,
    ensure_can_edit_test_cases,
)


def archive_test_case(*, user, test_case: TestCase):
    """
    Archives a test case.

    Once archived:
    - no edits
    - no imports
    - no new versions
    - view only
    """

    ensure_test_cases_enabled(test_case.project)
    ensure_can_edit_test_cases(user, test_case.project)

    if test_case.status == TestCase.STATUS_ARCHIVED:
        raise ValidationError("Test case already archived")

    test_case.archive()

    return test_case
