from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError, PermissionDenied

from apps.project_planning.models import TestCaseFolder
from apps.project_planning.services.test_case_access import (
    enforce_test_case_access,
)
from apps.project_planning.services.test_case_folders import (
    create_test_case_folder,
    rename_test_case_folder,
    move_test_case_folder,
    archive_test_case_folder,
)
from apps.project_planning.serializers_test_cases import (
    TestCaseFolderSerializer,
)
from apps.company_operations.models import Project

# ✅ PHASE 8
from apps.common.api_responses import api_error


# =====================================================
# CREATE FOLDER
# =====================================================

class CreateTestCaseFolderAPI(APIView):

    def post(self, request):
        project_id = request.data.get("project_id")
        name = request.data.get("name")
        parent_id = request.data.get("parent_id")

        project = get_object_or_404(Project, id=project_id)

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

        parent = None
        if parent_id:
            parent = get_object_or_404(
                TestCaseFolder,
                id=parent_id,
                project=project,
            )

        try:
            folder = create_test_case_folder(
                project=project,
                name=name,
                parent=parent,
            )
        except ValidationError as e:
            return api_error(
                code="FOLDER_CONFLICT",
                message=str(e),
                status_code=409,
            )

        return Response(
            TestCaseFolderSerializer(folder).data,
            status=status.HTTP_201_CREATED,
        )


# =====================================================
# LIST FOLDERS
# =====================================================

class ListTestCaseFoldersAPI(APIView):

    def get(self, request):
        project_id = request.query_params.get("project_id")

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

        folders = TestCaseFolder.objects.filter(
            project=project
        ).order_by("path")

        return Response(
            TestCaseFolderSerializer(folders, many=True).data
        )


# =====================================================
# RENAME FOLDER
# =====================================================

class RenameTestCaseFolderAPI(APIView):

    def patch(self, request, folder_id):
        new_name = request.data.get("name")

        folder = get_object_or_404(TestCaseFolder, id=folder_id)
        project = folder.project

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

        try:
            rename_test_case_folder(
                folder=folder,
                new_name=new_name,
            )
        except ValidationError as e:
            return api_error(
                code="FOLDER_CONFLICT",
                message=str(e),
                status_code=409,
            )

        return Response(
            TestCaseFolderSerializer(folder).data
        )


# =====================================================
# MOVE FOLDER
# =====================================================

class MoveTestCaseFolderAPI(APIView):

    def patch(self, request, folder_id):
        new_parent_id = request.data.get("parent_id")

        folder = get_object_or_404(TestCaseFolder, id=folder_id)
        project = folder.project

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

        new_parent = get_object_or_404(
            TestCaseFolder,
            id=new_parent_id,
            project=project,
        )

        try:
            move_test_case_folder(
                folder=folder,
                new_parent=new_parent,
            )
        except ValidationError as e:
            return api_error(
                code="FOLDER_CONFLICT",
                message=str(e),
                status_code=409,
            )

        return Response(
            TestCaseFolderSerializer(folder).data
        )


# =====================================================
# ARCHIVE FOLDER
# =====================================================

class ArchiveTestCaseFolderAPI(APIView):

    def post(self, request, folder_id):
        folder = get_object_or_404(TestCaseFolder, id=folder_id)
        project = folder.project

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

        try:
            archive_test_case_folder(folder)
        except ValidationError as e:
            return api_error(
                code="FOLDER_NOT_EMPTY",
                message=str(e),
                status_code=409,
            )

        return Response(
            {"status": "archived"},
            status=status.HTTP_200_OK,
        )
