from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.company_operations.models import Project
from apps.project_planning.models import ElementFolder
from apps.project_planning.serializers.elements import (
    ElementFolderSerializer,
)
from apps.project_planning.services.elements.folders import (
    create_element_folder,
    rename_element_folder,
    delete_element_folder,
)
from apps.common.api_responses import api_error


class CreateElementFolderAPI(APIView):

    def post(self, request):
        name = request.data.get("name")
        project_id = request.data.get("project_id")
        parent_id = request.data.get("parent_id")

        if not name:
            return api_error(
                code="INVALID_PAYLOAD",
                message="Folder name is required",
                status_code=400,
            )

        project = None
        parent = None

        # ---------------------------------
        # CASE 1: project_id is provided
        # ---------------------------------
        if project_id:
            project = get_object_or_404(Project, id=project_id)

            if parent_id:
                parent = get_object_or_404(
                    ElementFolder,
                    id=parent_id,
                    project=project,
                )

        # ---------------------------------
        # CASE 2: backward compatibility
        # (derive project from parent)
        # ---------------------------------
        elif parent_id:
            parent = get_object_or_404(ElementFolder, id=parent_id)
            project = parent.project

        # ---------------------------------
        # INVALID PAYLOAD
        # ---------------------------------
        else:
            return api_error(
                code="INVALID_PAYLOAD",
                message="Either project_id or parent_id must be provided",
                status_code=400,
            )

        try:
            folder = create_element_folder(
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
            ElementFolderSerializer(folder).data,
            status=status.HTTP_201_CREATED,
        )



class ListElementFoldersAPI(APIView):

    def get(self, request):
        project_id = request.query_params.get("project_id")

        folders = ElementFolder.objects.filter(
            project_id=project_id
        ).order_by("path")

        return Response(
            ElementFolderSerializer(folders, many=True).data
        )


class RenameElementFolderAPI(APIView):

    def patch(self, request, folder_id):
        new_name = request.data.get("name")

        folder = get_object_or_404(ElementFolder, id=folder_id)

        try:
            rename_element_folder(
                user=request.user,
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
            ElementFolderSerializer(folder).data
        )


class DeleteElementFolderAPI(APIView):

    def delete(self, request, folder_id):
        folder = get_object_or_404(ElementFolder, id=folder_id)

        try:
            delete_element_folder(
                user=request.user,
                folder=folder,
            )
        except ValidationError as e:
            return api_error(
                code="FOLDER_NOT_EMPTY",
                message=str(e),
                status_code=409,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
