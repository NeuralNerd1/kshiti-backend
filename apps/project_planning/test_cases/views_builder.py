from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from apps.project_planning.models import TestCase
from apps.project_planning.services.test_case_access import (
    enforce_test_case_access,
)

# ✅ Phase 8
from apps.common.api_responses import api_error


class SaveTestCaseBuilderAPI(APIView):

    def post(self, request, test_case_id):
        test_case = get_object_or_404(TestCase, id=test_case_id)
        project = test_case.project

        # ----------------------------------
        # Permission check
        # ----------------------------------
        try:
            enforce_test_case_access(
                project=project,
                user=request.user,
                permission_key="can_edit_test_cases",
            )
        except PermissionDenied as e:
            return api_error(
                code="PERMISSION_DENIED",
                message=str(e),
                status_code=403,
            )

        # ----------------------------------
        # Archive check
        # ----------------------------------
        if test_case.status == TestCase.STATUS_ARCHIVED:
            return api_error(
                code="TEST_CASE_ARCHIVED",
                message="Archived test case cannot be edited",
                status_code=409,
            )

        # ----------------------------------
        # Input validation
        # ----------------------------------
        section = request.data.get("section")
        section_steps = request.data.get("steps")

        if section not in (
            "pre_conditions",
            "steps",
            "expected_outcomes",
        ):
            return api_error(
                code="INVALID_SECTION",
                message="Invalid section",
                status_code=400,
            )

        if not isinstance(section_steps, list):
            return api_error(
                code="VALIDATION_ERROR",
                message="Steps must be an array",
                status_code=400,
            )

        # ----------------------------------
        # Fetch latest version
        # ----------------------------------
        latest = test_case.versions.order_by(
            "-version_number"
        ).first()

        if not latest:
            return api_error(
                code="VERSION_CONFLICT",
                message="No base version found",
                status_code=409,
            )

        # ----------------------------------
        # Copy previous data
        # ----------------------------------
        pre_conditions = latest.pre_conditions_json
        steps = latest.steps_json
        expected = latest.expected_outcomes_json

        # ----------------------------------
        # Replace edited section only
        # ----------------------------------
        if section == "pre_conditions":
            pre_conditions = section_steps
        elif section == "steps":
            steps = section_steps
        elif section == "expected_outcomes":
            expected = section_steps

        # ----------------------------------
        # Create new version
        # ----------------------------------
        new_version_number = latest.version_number + 1

        test_case.versions.create(
            version_number=new_version_number,
            pre_conditions_json=pre_conditions,
            steps_json=steps,
            expected_outcomes_json=expected,
            created_from_version=latest.version_number,
        )

        test_case.current_version = new_version_number
        test_case.save(update_fields=["current_version"])

        # ----------------------------------
        # Success response (UNCHANGED)
        # ----------------------------------
        return Response(
            {"version": new_version_number},
            status=status.HTTP_200_OK,
        )
