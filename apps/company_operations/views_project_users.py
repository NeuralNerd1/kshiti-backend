from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.company_auth.utils import get_company_from_request
from apps.company_operations.models import Project, ProjectUser
from apps.company_operations.services.project_users import get_project_user
from apps.company_operations.services.project_permissions import (
    require_project_permission,
)
from apps.company_operations.serializers_project_users import (
    ProjectUserCreateSerializer,
    ProjectUserUpdateSerializer,
)


class ProjectUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        company = get_company_from_request(request)
        project = get_object_or_404(Project, id=project_id, company=company)

        requester = get_project_user(project, request.user)
        require_project_permission(
            requester, "can_manage_project_users"
        )

        members = ProjectUser.objects.filter(project=project)

        return Response(
            [
                {
                    "id": m.id,
                    "company_user_id": m.company_user_id,
                    "email": m.company_user.user.email,
                    "role": m.role.name,
                    "is_active": m.is_active,
                }
                for m in members
            ],
            status=status.HTTP_200_OK,
        )

    def post(self, request, project_id):
        company = get_company_from_request(request)
        project = get_object_or_404(Project, id=project_id, company=company)

        requester = get_project_user(project, request.user)
        require_project_permission(
            requester, "can_manage_project_users"
        )

        serializer = ProjectUserCreateSerializer(
            data=request.data,
            context={"project": project},
        )
        serializer.is_valid(raise_exception=True)

        ProjectUser.objects.create(
            project=project,
            company_user=serializer.validated_data["company_user"],
            role=serializer.validated_data["role"],
        )

        return Response(
            {"status": "user_added"},
            status=status.HTTP_201_CREATED,
        )


class ProjectUserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, project_id, member_id):
        company = get_company_from_request(request)
        project = get_object_or_404(Project, id=project_id, company=company)

        requester = get_project_user(project, request.user)
        require_project_permission(
            requester, "can_manage_project_users"
        )

        member = get_object_or_404(
            ProjectUser, id=member_id, project=project
        )

        serializer = ProjectUserUpdateSerializer(
            data=request.data,
            context={"project": project},
        )
        serializer.is_valid(raise_exception=True)

        member.role = serializer.validated_data["role"]
        member.save(update_fields=["role"])

        return Response({"status": "role_updated"})

    def delete(self, request, project_id, member_id):
        company = get_company_from_request(request)
        project = get_object_or_404(Project, id=project_id, company=company)

        requester = get_project_user(project, request.user)
        require_project_permission(
            requester, "can_manage_project_users"
        )

        member = get_object_or_404(
            ProjectUser, id=member_id, project=project
        )

        member.delete()
        return Response(
            {"status": "user_removed"},
            status=status.HTTP_204_NO_CONTENT,
        )
