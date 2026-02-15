from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.company_operations.models import Project
from apps.company_operations.services.project_users import get_project_user

from apps.test_plan.models import ProcessTemplate
from apps.test_plan.serializers.template import (
    TemplateCreateSerializer,
    TemplateDetailSerializer,
)
from apps.test_plan.services.guards import ensure_test_planning_enabled
from apps.test_plan.services.template_crud import (
    create_template,
    update_template,
    delete_template,
)

class TemplateCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):

        project = get_object_or_404(
            Project.objects.select_related("company"),
            id=project_id,
        )

        ensure_test_planning_enabled(project)

        # Validate project membership
        get_project_user(project, request.user)

        serializer = TemplateCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        template = create_template(
            project=project,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(
            TemplateDetailSerializer(template).data,
            status=status.HTTP_201_CREATED,
        )

class TemplateListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):

        project = get_object_or_404(
            Project.objects.select_related("company"),
            id=project_id,
        )

        ensure_test_planning_enabled(project)

        get_project_user(project, request.user)

        templates = (
            ProcessTemplate.objects
    .filter(company=project.company)
    .select_related("created_by", "reviewer")
    .order_by("-created_at")
        )

        return Response(
            TemplateDetailSerializer(templates, many=True).data
        )

class TemplateDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, template_id):

        project = get_object_or_404(
            Project.objects.select_related("company"),
            id=project_id,
        )

        ensure_test_planning_enabled(project)

        get_project_user(project, request.user)

        template = get_object_or_404(
            ProcessTemplate.objects.select_related("company"),
            id=template_id,
            company=project.company,
        )

        return Response(
            TemplateDetailSerializer(template).data
        )

class TemplateUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, project_id, template_id):

        project = get_object_or_404(
            Project.objects.select_related("company"),
            id=project_id,
        )

        ensure_test_planning_enabled(project)

        get_project_user(project, request.user)

        template = get_object_or_404(
            ProcessTemplate.objects.select_related("company"),
            id=template_id,
            company=project.company,
        )

        serializer = TemplateCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        template = update_template(
            template=template,
            project=project,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(
            TemplateDetailSerializer(template).data
        )

class TemplateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, project_id, template_id):

        project = get_object_or_404(
            Project.objects.select_related("company"),
            id=project_id,
        )

        ensure_test_planning_enabled(project)

        get_project_user(project, request.user)

        template = get_object_or_404(
            ProcessTemplate.objects.select_related("company"),
            id=template_id,
            company=project.company,
        )

        delete_template(
            template=template,
            project=project,
            user=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

