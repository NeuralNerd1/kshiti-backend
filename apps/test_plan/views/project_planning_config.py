from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.company_operations.models import Project
from apps.company_operations.services.project_users import get_project_user
from apps.test_plan.services.guards import ensure_test_planning_enabled
from apps.test_plan.serializers.project_planning_config import (
    ProjectPlanningConfigSerializer,
)


class ProjectPlanningConfigDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):

        # 🔥 Lazy import to break circular dependency
        from apps.test_plan.services.project_planning_config_service import (
            get_or_create_planning_config,
        )

        project = get_object_or_404(Project, id=project_id)

        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        config = get_or_create_planning_config(
            project=project,
            user=request.user,
        )

        return Response(
            ProjectPlanningConfigSerializer(config).data
        )


class ProjectPlanningConfigUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, project_id):

        # 🔥 Lazy import to break circular dependency
        from apps.test_plan.services.project_planning_config_service import (
            update_planning_config,
        )

        project = get_object_or_404(Project, id=project_id)

        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        serializer = ProjectPlanningConfigSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        config = update_planning_config(
            project=project,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(
            ProjectPlanningConfigSerializer(config).data
        )
