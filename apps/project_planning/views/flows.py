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

from apps.project_planning.models import FlowFolder, Flow
from apps.project_planning.serializers.flows import (
    FlowListSerializer,
    FlowCreateSerializer,
    FlowVersionCreateSerializer,
    FlowVersionSerializer,
    FlowUpdateSerializer,
)
from apps.project_planning.services.flows import (
    create_flow,
    archive_flow,
    update_flow_metadata,
    delete_flow,
    get_flows_for_folder_tree,
)
from apps.project_planning.services.versions import (
    save_flow_version,
    rollback_flow_version,
)


class FlowListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        """
        List flows for a project.
        Optional query param:
        - folder_id: list flows under a folder (recursive)
        """

        project = get_object_or_404(Project, id=project_id)

        # 🔐 FEATURE-3 ACCESS (VIEW)
        enforce_feature3_access(
            project=project,
            user=request.user,
            permission_key=CAN_VIEW_FLOWS,
        )

        folder_id = request.query_params.get("folder_id")

        if folder_id:
            folder = get_object_or_404(
                FlowFolder,
                id=folder_id,
                project=project,
            )
            flows = get_flows_for_folder_tree(folder=folder)
        else:
            flows = Flow.objects.filter(project=project)

        serializer = FlowListSerializer(flows, many=True)
        return Response(serializer.data)

    def post(self, request, project_id):
        serializer = FlowCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = get_object_or_404(Project, id=project_id)

        # 🔐 FEATURE-3 ACCESS (CREATE)
        enforce_feature3_access(
            project=project,
            user=request.user,
            permission_key=CAN_CREATE_FLOWS,
        )

        folder = None
        folder_id = serializer.validated_data.get("folder_id")

        if folder_id:
            folder = get_object_or_404(
                FlowFolder,
                id=folder_id,
                project=project,
            )

        flow = create_flow(
            user=request.user,
            project=project,
            folder=folder,
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
        )

        return Response(
            FlowListSerializer(flow).data,
            status=201,
        )


class FlowDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, flow_id):
        flow = get_object_or_404(Flow, id=flow_id)

        # 🔐 FEATURE-3 ACCESS (VIEW)
        enforce_feature3_access(
            project=flow.project,
            user=request.user,
            permission_key=CAN_VIEW_FLOWS,
        )

        versions = flow.versions.all()

        return Response(
            {
                "flow": FlowListSerializer(flow).data,
                "folder": {
                    "id": flow.folder.id if flow.folder else None,
                    "path": flow.folder.path if flow.folder else None,
                },
                "versions": FlowVersionSerializer(versions, many=True).data,
            }
        )


class FlowVersionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, flow_id):
        serializer = FlowVersionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        flow = get_object_or_404(Flow, id=flow_id)

        # 🔐 FEATURE-3 ACCESS (EDIT)
        enforce_feature3_access(
            project=flow.project,
            user=request.user,
            permission_key=CAN_EDIT_FLOWS,
        )

        version = save_flow_version(
            user=request.user,
            flow=flow,
            steps_json=serializer.validated_data["steps_json"],
            created_from_version=serializer.validated_data.get(
                "created_from_version"
            ),
        )

        return Response(
            FlowVersionSerializer(version).data,
            status=201,
        )


class FlowRollbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, flow_id, version_number):
        flow = get_object_or_404(Flow, id=flow_id)

        # 🔐 FEATURE-3 ACCESS (EDIT)
        enforce_feature3_access(
            project=flow.project,
            user=request.user,
            permission_key=CAN_EDIT_FLOWS,
        )

        version = rollback_flow_version(
            user=request.user,
            flow=flow,
            source_version_number=version_number,
        )

        return Response(
            FlowVersionSerializer(version).data,
            status=201,
        )


class FlowArchiveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, flow_id):
        flow = get_object_or_404(Flow, id=flow_id)

        # 🔐 FEATURE-3 ACCESS (EDIT)
        enforce_feature3_access(
            project=flow.project,
            user=request.user,
            permission_key=CAN_EDIT_FLOWS,
        )

        archive_flow(
            user=request.user,
            flow=flow,
        )

        return Response({"status": "archived"})


class FlowUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, flow_id):
        serializer = FlowUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        flow = get_object_or_404(Flow, id=flow_id)

        # 🔐 FEATURE-3 ACCESS (EDIT)
        enforce_feature3_access(
            project=flow.project,
            user=request.user,
            permission_key=CAN_EDIT_FLOWS,
        )

        flow = update_flow_metadata(
            user=request.user,
            flow=flow,
            **serializer.validated_data,
        )

        return Response(FlowListSerializer(flow).data)


class FlowDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, flow_id):
        flow = get_object_or_404(Flow, id=flow_id)

        # 🔐 FEATURE-3 ACCESS (EDIT)
        enforce_feature3_access(
            project=flow.project,
            user=request.user,
            permission_key=CAN_EDIT_FLOWS,
        )

        delete_flow(
            user=request.user,
            flow=flow,
        )

        return Response(status=204)
