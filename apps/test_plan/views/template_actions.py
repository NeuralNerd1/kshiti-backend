from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.company_operations.models import Project
from apps.company_operations.services.project_users import get_project_user

from apps.test_plan.models import ProcessTemplate
from apps.test_plan.services.template_status_service import (
    transition_template_status,
)
from apps.test_plan.services.guards import ensure_test_planning_enabled
from apps.test_plan.serializers.template import TemplateDetailSerializer

class TemplateActionBaseView(APIView):
    permission_classes = [IsAuthenticated]

    action = None

    def post(self, request, project_id, template_id):

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

        template = transition_template_status(
            template=template,
            project=project,
            user=request.user,
            action=self.action,
            reviewer_id=request.data.get("reviewer_id"),
            rejection_note=request.data.get("note"),
        )

        return Response(
            TemplateDetailSerializer(template).data,
            status=status.HTTP_200_OK,
        )
class TemplateSubmitView(TemplateActionBaseView):
    action = "submit"


class TemplateAssignReviewerView(TemplateActionBaseView):
    action = "assign_reviewer"


class TemplateApproveView(TemplateActionBaseView):
    action = "approve"


class TemplateRejectView(TemplateActionBaseView):
    action = "reject"


class TemplateCreateFinalView(TemplateActionBaseView):
    action = "create"
