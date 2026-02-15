from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.company_operations.models import Project
from apps.company_operations.services.project_users import get_project_user

from apps.test_plan.models import ProcessTemplate, PlanningEntityType
from apps.test_plan.serializers.entity_type import EntityTypeSerializer
from apps.test_plan.services.entity_type_service import (
    create_entity_type,
    update_entity_type,
    delete_entity_type,
)
from apps.test_plan.services.guards import ensure_test_planning_enabled

class EntityTypeCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id, template_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        template = get_object_or_404(
            ProcessTemplate,
            id=template_id,
            company=project.company,
        )

        serializer = EntityTypeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        entity = create_entity_type(
            project=project,
            template=template,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(
            EntityTypeSerializer(entity).data,
            status=status.HTTP_201_CREATED,
        )

class EntityTypeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, template_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        template = get_object_or_404(
            ProcessTemplate,
            id=template_id,
            company=project.company,
        )

        entities = PlanningEntityType.objects.filter(
            template=template
        ).order_by("level_order")

        return Response(
            EntityTypeSerializer(entities, many=True).data
        )

class EntityTypeUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, project_id, entity_type_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        entity_type = get_object_or_404(
            PlanningEntityType.objects.select_related("template"),
            id=entity_type_id,
            template__company=project.company,
        )

        serializer = EntityTypeSerializer(
    entity_type,
    data=request.data,
    partial=True   # 🔥 THIS IS THE FIX
)
        serializer.is_valid(raise_exception=True)

        entity_type = update_entity_type(
            project=project,
            entity_type=entity_type,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(EntityTypeSerializer(entity_type).data)

class EntityTypeDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, project_id, entity_type_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        entity_type = get_object_or_404(
            PlanningEntityType.objects.select_related("template"),
            id=entity_type_id,
            template__company=project.company,
        )

        delete_entity_type(
            project=project,
            entity_type=entity_type,
            user=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
