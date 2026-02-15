from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.company_operations.models import Project
from apps.company_operations.services.project_users import get_project_user
from apps.test_plan.models import KanbanBoardConfig
from apps.test_plan.serializers.kanban import KanbanBoardConfigSerializer
from apps.test_plan.services.guards import ensure_test_planning_enabled

class KanbanBoardConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        view_key = request.query_params.get("view_key", "GLOBAL")
        config, _ = KanbanBoardConfig.objects.get_or_create(project=project, view_key=view_key)
        serializer = KanbanBoardConfigSerializer(config)
        return Response(serializer.data)

    def put(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        view_key = request.data.get("view_key", "GLOBAL")
        config, _ = KanbanBoardConfig.objects.get_or_create(project=project, view_key=view_key)
        serializer = KanbanBoardConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
