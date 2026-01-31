from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError, PermissionDenied

from apps.project_planning.models import (
    TestCase,
    TestCaseFolder,
    TestCaseVersion,
)

from apps.project_planning.services.test_case_access import (
    enforce_test_case_access,
)

from apps.project_planning.serializers_test_cases import (
    TestCaseSerializer,
    TestCaseVersionSerializer,
    TestCaseFolderSerializer,
)

from apps.project_planning.services.test_cases import (
    archive_test_case,
)

# ✅ Phase 8
from apps.common.api_responses import api_error


# =====================================================
# CREATE TEST CASE
# =====================================================

class CreateTestCaseAPI(APIView):

    def post(self, request):
        folder_id = request.data.get("folder_id")
        name = request.data.get("name")
        description = request.data.get("description", "")

        folder = get_object_or_404(TestCaseFolder, id=folder_id)
        project = folder.project

        try:
            enforce_test_case_access(
                project=project,
                user=request.user,
                permission_key="can_create_test_cases",
            )
        except PermissionDenied as e:
            return api_error(
                code="PERMISSION_DENIED",
                message=str(e),
                status_code=403,
            )

        try:
            test_case = TestCase.objects.create(
                project=project,
                folder=folder,
                name=name,
                description=description,
                status=TestCase.STATUS_SAVED,
                current_version=1,
            )

            # 🔥 Auto-create version 1
            TestCaseVersion.objects.create(
                test_case=test_case,
                version_number=1,
                pre_conditions_json=[],
                steps_json=[],
                expected_outcomes_json=[],
                created_from_version=None,
            )

        except ValidationError as e:
            return api_error(
                code="VALIDATION_ERROR",
                message=str(e),
                status_code=400,
            )

        return Response(
            TestCaseSerializer(test_case).data,
            status=status.HTTP_201_CREATED,
        )


# =====================================================
# LIST TEST CASES
# =====================================================

class ListTestCasesAPI(APIView):

    def get(self, request):
        project_id = request.query_params.get("project_id")

        from apps.company_operations.models import Project
        project = get_object_or_404(Project, id=project_id)

        try:
            enforce_test_case_access(
                project=project,
                user=request.user,
                permission_key="can_view_test_cases",
            )
        except PermissionDenied as e:
            return api_error(
                code="PERMISSION_DENIED",
                message=str(e),
                status_code=403,
            )

        test_cases = TestCase.objects.filter(
            project=project
        ).select_related("folder")

        return Response(
            TestCaseSerializer(test_cases, many=True).data
        )


# =====================================================
# TEST CASE DETAIL
# =====================================================

class TestCaseDetailAPI(APIView):

    def get(self, request, test_case_id):
        test_case = get_object_or_404(TestCase, id=test_case_id)
        project = test_case.project

        try:
            enforce_test_case_access(
                project=project,
                user=request.user,
                permission_key="can_view_test_cases",
            )
        except PermissionDenied as e:
            return api_error(
                code="PERMISSION_DENIED",
                message=str(e),
                status_code=403,
            )

        versions = test_case.versions.all()

        return Response({
            "test_case": TestCaseSerializer(test_case).data,
            "folder": TestCaseFolderSerializer(
                test_case.folder
            ).data,
            "versions": TestCaseVersionSerializer(
                versions, many=True
            ).data,
        })


# =====================================================
# SAVE TEST CASE (NEW VERSION)
# =====================================================

class SaveTestCaseAPI(APIView):

    def post(self, request, test_case_id):
        test_case = get_object_or_404(TestCase, id=test_case_id)
        project = test_case.project

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

        if test_case.status == TestCase.STATUS_ARCHIVED:
            return api_error(
                code="TEST_CASE_ARCHIVED",
                message="Archived test case cannot be modified",
                status_code=409,
            )

        pre_conditions = request.data.get("pre_conditions", [])
        steps = request.data.get("steps", [])
        expected = request.data.get("expected_outcomes", [])

        latest = test_case.versions.order_by(
            "-version_number"
        ).first()

        if not latest:
            return api_error(
                code="VERSION_CONFLICT",
                message="No base version found",
                status_code=409,
            )

        new_version = latest.version_number + 1

        TestCaseVersion.objects.create(
            test_case=test_case,
            version_number=new_version,
            pre_conditions_json=pre_conditions,
            steps_json=steps,
            expected_outcomes_json=expected,
            created_from_version=latest.version_number,
        )

        test_case.current_version = new_version
        test_case.save(update_fields=["current_version"])

        return Response(
            {"version": new_version},
            status=status.HTTP_200_OK,
        )


# =====================================================
# ARCHIVE TEST CASE
# =====================================================

class ArchiveTestCaseAPI(APIView):

    def post(self, request, test_case_id):
        test_case = get_object_or_404(TestCase, id=test_case_id)

        try:
            archive_test_case(
                user=request.user,
                test_case=test_case,
            )
        except ValidationError as e:
            return api_error(
                code="TEST_CASE_ARCHIVED",
                message=str(e),
                status_code=409,
            )

        return Response(
            {"status": "archived"},
            status=status.HTTP_200_OK,
        )
