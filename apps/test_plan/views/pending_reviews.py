from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.company_operations.models import Project
from apps.company_operations.services.project_users import get_project_user
from apps.test_plan.models import ProcessTemplate
from apps.test_plan.serializers.template import TemplateDetailSerializer
from apps.test_plan.services.guards import ensure_test_planning_enabled


class PendingReviewsView(APIView):
    """
    GET /test-plan/projects/<project_id>/templates/pending-reviews/

    Returns templates assigned to the current user for review
    (status = APPROVAL_PENDING, reviewer = current user's company_user).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(
            Project.objects.select_related("company"),
            id=project_id,
        )

        ensure_test_planning_enabled(project)

        project_user = get_project_user(project, request.user)

        templates = (
            ProcessTemplate.objects
            .filter(
                company=project.company,
                status=ProcessTemplate.STATUS_APPROVAL_PENDING,
                reviewer=project_user.company_user,
            )
            .select_related("created_by", "reviewer")
            .order_by("-updated_at")
        )

        return Response(
            TemplateDetailSerializer(templates, many=True).data
        )
