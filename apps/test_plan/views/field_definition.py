from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.company_operations.models import Project
from apps.company_operations.services.project_users import get_project_user

from apps.test_plan.models import PlanningEntityType, EntityFieldDefinition
from apps.test_plan.serializers.field_definition import FieldDefinitionSerializer
from apps.test_plan.services.field_definition_service import (
    create_field_definition,
    update_field_definition,
    delete_field_definition,
)
from apps.test_plan.services.guards import ensure_test_planning_enabled

class FieldDefinitionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id, entity_type_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        entity_type = get_object_or_404(
            PlanningEntityType.objects.select_related("template"),
            id=entity_type_id,
            template__company=project.company,
        )

        serializer = FieldDefinitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        field = create_field_definition(
            project=project,
            entity_type=entity_type,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(
            FieldDefinitionSerializer(field).data,
            status=status.HTTP_201_CREATED,
        )

class FieldDefinitionUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, project_id, field_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        field = get_object_or_404(
            EntityFieldDefinition.objects.select_related("entity_type__template"),
            id=field_id,
            entity_type__template__company=project.company,
        )

        serializer = FieldDefinitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        field = update_field_definition(
            project=project,
            field=field,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(FieldDefinitionSerializer(field).data)

class FieldDefinitionDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, project_id, field_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        field = get_object_or_404(
            EntityFieldDefinition.objects.select_related("entity_type__template"),
            id=field_id,
            entity_type__template__company=project.company,
        )

        delete_field_definition(
            project=project,
            field=field,
            user=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

class FieldDefinitionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, entity_type_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        entity_type = get_object_or_404(
            PlanningEntityType.objects.select_related("template"),
            id=entity_type_id,
            template__company=project.company,
        )

        fields = (
            EntityFieldDefinition.objects
            .filter(entity_type=entity_type)
            .order_by("order")
        )

        return Response(
            FieldDefinitionSerializer(fields, many=True).data
        )
