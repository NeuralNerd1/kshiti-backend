from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.project_planning.models import VariableFolder
from apps.company_operations.models import Project
from apps.project_planning.serializers.variables import (
    VariableFolderSerializer,
)
from apps.project_planning.services.variables.folders import (
    create_variable_folder,
    rename_variable_folder,
    delete_variable_folder,
)
from apps.common.api_responses import api_error
from rest_framework.exceptions import ValidationError


class CreateVariableFolderAPI(APIView):

    def post(self, request):
        project_id = request.data.get("project_id")
        name = request.data.get("name")
        parent_id = request.data.get("parent_id")

        project = get_object_or_404(Project, id=project_id)

        parent = None
        if parent_id:
            parent = get_object_or_404(
                VariableFolder,
                id=parent_id,
                project=project,
            )

        try:
            folder = create_variable_folder(
                user=request.user,
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
            VariableFolderSerializer(folder).data,
            status=201,
        )


class ListVariableFoldersAPI(APIView):

    def get(self, request):
        project_id = request.query_params.get("project_id")

        folders = VariableFolder.objects.filter(
            project_id=project_id
        ).order_by("path")

        return Response(
            VariableFolderSerializer(folders, many=True).data
        )


class RenameVariableFolderAPI(APIView):

    def patch(self, request, folder_id):
        name = request.data.get("name")
        folder = get_object_or_404(VariableFolder, id=folder_id)

        try:
            rename_variable_folder(
                user=request.user,
                folder=folder,
                new_name=name,
            )
        except ValidationError as e:
            return api_error(
                code="FOLDER_CONFLICT",
                message=str(e),
                status_code=409,
            )

        return Response(
            VariableFolderSerializer(folder).data
        )


class DeleteVariableFolderAPI(APIView):

    def delete(self, request, folder_id):
        folder = get_object_or_404(VariableFolder, id=folder_id)

        try:
            delete_variable_folder(
                user=request.user,
                folder=folder,
            )
        except ValidationError as e:
            return api_error(
                code="FOLDER_NOT_EMPTY",
                message=str(e),
                status_code=409,
            )

        return Response(status=204)
