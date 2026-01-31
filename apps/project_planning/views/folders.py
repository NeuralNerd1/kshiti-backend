from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.company_operations.models import Project
from apps.company_operations.permissions import (
    CAN_VIEW_FLOWS,
    CAN_CREATE_FLOWS,
    CAN_EDIT_FLOWS,
)
from apps.company_operations.services.feature3_access import (
    enforce_feature3_permission,
)
from apps.company_operations.services.feature3_access import (
    enforce_feature3_access,
)

from apps.project_planning.models import FlowFolder
from apps.project_planning.serializers.folders import (
    FolderSerializer,
    FolderCreateSerializer,
    FolderRenameSerializer,
)
from apps.project_planning.services.folders import (
    create_folder,
    rename_folder,
    delete_folder,
)


class FolderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        """
        Returns all folders for a project, ordered by path
        so frontend can reconstruct the tree deterministically.
        """

        project = get_object_or_404(Project, id=project_id)

        # 🔐 FEATURE-3 ACCESS (VIEW)
        enforce_feature3_access(
    project=project,
    user=request.user,
    permission_key=CAN_VIEW_FLOWS,
)

        folders = FlowFolder.objects.filter(
            project_id=project_id
        ).order_by("path")

        return Response(FolderSerializer(folders, many=True).data)

    def post(self, request, project_id):
        serializer = FolderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = get_object_or_404(Project, id=project_id)

        # 🔐 FEATURE-3 ACCESS (CREATE)
        enforce_feature3_access(
    project=project,
    user=request.user,
    permission_key=CAN_CREATE_FLOWS,
)

        folder = create_folder(
            user=request.user,
            project=project,
            name=serializer.validated_data["name"],
            parent_id=serializer.validated_data.get("parent_id"),
        )

        return Response(FolderSerializer(folder).data, status=201)


class FolderRenameView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, folder_id):
        serializer = FolderRenameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        folder = get_object_or_404(
            FlowFolder,
            id=folder_id,
        )

        # 🔐 FEATURE-3 ACCESS (EDIT)
        enforce_feature3_access(
    project=folder.project,
    user=request.user,
    permission_key=CAN_EDIT_FLOWS,
)

        folder = rename_folder(
            user=request.user,
            folder=folder,
            new_name=serializer.validated_data["name"],
        )

        return Response(FolderSerializer(folder).data)


class FolderDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, folder_id):
        folder = get_object_or_404(
            FlowFolder,
            id=folder_id,
        )

        # 🔐 FEATURE-3 ACCESS (EDIT)
        enforce_feature3_access(
    project=folder.project,
    user=request.user,
    permission_key=CAN_EDIT_FLOWS,
)

        delete_folder(
            user=request.user,
            folder=folder,
        )

        return Response(status=204)
