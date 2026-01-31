from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.project_planning.models import (
    TestCase,
    Flow,
    FlowVersion,
)

# ----------------------------
# FLOW GUARDS (EXISTING)
# ----------------------------
from apps.project_planning.services._guards import (
    ensure_flows_enabled,
    ensure_can_edit_flows,
)

# ----------------------------
# TEST CASE GUARDS
# ----------------------------
from apps.project_planning.services.test_case_guards import (
    ensure_test_cases_enabled,
    ensure_can_edit_test_cases,
)

# ----------------------------
# PHASE 8 STANDARD ERRORS
# ----------------------------
from apps.common.api_responses import api_error


class ImportFlowIntoTestCaseAPI(APIView):
    """
    Imports the CURRENT VERSION of a Flow into
    a specific section of a Test Case.

    - Flow is NEVER modified
    - Test case ALWAYS creates a new version
    - Version history remains immutable
    """

    def post(self, request, test_case_id):

        # -------------------------------------------------
        # Fetch test case
        # -------------------------------------------------

        test_case = get_object_or_404(TestCase, id=test_case_id)
        project = test_case.project

        # -------------------------------------------------
        # Test case guards
        # -------------------------------------------------

        try:
            ensure_test_cases_enabled(project)
            ensure_can_edit_test_cases(request.user, project)
        except ValidationError as e:
            return api_error(
                code="PERMISSION_DENIED",
                message=str(e),
                status_code=403,
            )

        if test_case.status == TestCase.STATUS_ARCHIVED:
            return api_error(
                code="TEST_CASE_ARCHIVED",
                message="Archived test case cannot be modified",
                status_code=409,
            )

        # -------------------------------------------------
        # Input validation
        # -------------------------------------------------

        flow_id = request.data.get("flow_id")
        target_section = request.data.get("target_section")

        if not flow_id:
            return api_error(
                code="VALIDATION_ERROR",
                message="flow_id is required",
                status_code=400,
            )

        if target_section not in (
            "pre_conditions",
            "steps",
            "expected_outcomes",
        ):
            return api_error(
                code="INVALID_SECTION",
                message="Invalid target section",
                status_code=400,
            )

        # -------------------------------------------------
        # Fetch flow
        # -------------------------------------------------

        flow = get_object_or_404(Flow, id=flow_id)

        if flow.project_id != project.id:
            return api_error(
                code="FLOW_PROJECT_MISMATCH",
                message="Flow does not belong to this project",
                status_code=403,
            )

        # -------------------------------------------------
        # Flow guards
        # -------------------------------------------------

        try:
            ensure_flows_enabled(project)
            ensure_can_edit_flows(request.user, project)
        except ValidationError as e:
            return api_error(
                code="PERMISSION_DENIED",
                message=str(e),
                status_code=403,
            )

        if flow.current_version is None:
            return api_error(
                code="VERSION_CONFLICT",
                message="Flow has no active version",
                status_code=409,
            )

        # -------------------------------------------------
        # Fetch flow current version
        # -------------------------------------------------

        flow_version = FlowVersion.objects.filter(
            flow=flow,
            version_number=flow.current_version,
        ).first()

        if not flow_version:
            return api_error(
                code="VERSION_CONFLICT",
                message="Flow current version not found",
                status_code=409,
            )

        imported_steps = flow_version.steps_json

        # -------------------------------------------------
        # Fetch latest test case version
        # -------------------------------------------------

        latest_version = test_case.versions.order_by(
            "-version_number"
        ).first()

        if not latest_version:
            return api_error(
                code="VERSION_CONFLICT",
                message="Test case has no base version",
                status_code=409,
            )

        # -------------------------------------------------
        # Copy existing sections
        # -------------------------------------------------

        pre_conditions = latest_version.pre_conditions_json
        steps = latest_version.steps_json
        expected = latest_version.expected_outcomes_json

        # -------------------------------------------------
        # Replace target section
        # -------------------------------------------------

        if target_section == "pre_conditions":
            pre_conditions = imported_steps
        elif target_section == "steps":
            steps = imported_steps
        elif target_section == "expected_outcomes":
            expected = imported_steps

        # -------------------------------------------------
        # Create new test case version
        # -------------------------------------------------

        new_version_number = latest_version.version_number + 1

        test_case.versions.create(
            version_number=new_version_number,
            pre_conditions_json=pre_conditions,
            steps_json=steps,
            expected_outcomes_json=expected,
            created_from_version=latest_version.version_number,
        )

        test_case.current_version = new_version_number
        test_case.save(update_fields=["current_version"])

        # -------------------------------------------------
        # Response (UNCHANGED)
        # -------------------------------------------------

        return Response(
            {
                "imported_from_flow": flow.id,
                "new_version": new_version_number,
            },
            status=status.HTTP_200_OK,
        )
