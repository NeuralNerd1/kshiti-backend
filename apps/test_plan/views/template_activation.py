from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.company_operations.models import Project
from apps.test_plan.models import ProcessTemplate
from apps.test_plan.services.template_activation_service import (
    activate_template_for_project,
)
from apps.test_plan.serializers.template_activation import (
    ProjectTemplateBindingSerializer,
)
from apps.test_plan.services.guards import ensure_test_planning_enabled
from apps.company_operations.services.project_users import get_project_user

class ActivateTemplateView(APIView):
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

        binding = activate_template_for_project(
            project=project,
            template=template,
            user=request.user,
        )

        return Response(
            ProjectTemplateBindingSerializer(binding).data,
            status=status.HTTP_200_OK,
        )

