from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.company_auth.models import CompanyUser
from .models import Project
from .serializers import ProjectSerializer
from .services.permissions import require_permission
from apps.company_auth.utils import (
    get_company_from_request,
    get_company_user,

)
from apps.company_operations.services.project_users import get_project_user

from apps.company_operations.services.permissions import has_permission
from apps.company_operations.services.permissions import require_permission
from apps.company_operations.services.projects import create_project
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from apps.company_operations.models import Role
from apps.company_operations.serializers import RoleSerializer
from django.db.models import Q






class ProjectListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = get_company_from_request(request)
        company_user = get_company_user(request, company)

        if has_permission(company_user, "can_view_all_projects"):
            queryset = Project.objects.filter(company=company)
        else:
            queryset = Project.objects.filter(
                company=company,
                project_admin=company_user,
            )

        queryset = queryset.order_by("-created_at")

        return Response(
            ProjectSerializer(queryset, many=True).data,
            status=status.HTTP_200_OK,
        )

class CompanyUsersView(APIView):
    """
    List & add users within a company.
    Accessible only to company admins.
    """

    def get(self, request):
        company = get_company_from_request(request)
        cu = get_company_user(request, company)

        require_permission(cu, "can_manage_users")

        users = CompanyUser.objects.filter(company=company)

        return Response(
            [
                {
                    "id": u.id,
                    "user_id": u.user_id,
                    "email": u.user.email,
                    "role_id": u.role_id,
                    "is_active": u.is_active,
                }
                for u in users
            ]
        )

    def post(self, request):
        company = get_company_from_request(request)
        cu = get_company_user(request, company)

        require_permission(cu, "can_manage_users")

        user_id = request.data.get("user_id")
        role_id = request.data.get("role_id")

        if not user_id or not role_id:
            return Response(
                {"error": "user_id and role_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_cu = CompanyUser.objects.create(
            company=company,
            user_id=user_id,
            role_id=role_id,
        )

        return Response(
            {
                "id": new_cu.id,
                "user_id": new_cu.user_id,
                "role_id": new_cu.role_id,
                "is_active": new_cu.is_active,
            },
            status=status.HTTP_201_CREATED,
        )


class ProjectsView(APIView):
    """
    List & create projects for a company.
    """

    def get(self, request):
        company = get_company_from_request(request)
        cu = get_company_user(request, company)

        # Admins see all projects
        require_permission(cu, "can_view_all_projects")

        projects = Project.objects.filter(
            company=company,
            status=Project.STATUS_ACTIVE,
        )

        return Response(ProjectSerializer(projects, many=True).data)

    def post(self, request):
        company = get_company_from_request(request)
        cu = get_company_user(request, company)

        require_permission(cu, "can_create_project")

        if not company.can_create_projects:
            return Response(
                {"error": company.project_creation_disabled_reason},
                status=status.HTTP_403_FORBIDDEN,
            )

        active_count = Project.objects.filter(
            company=company,
            status=Project.STATUS_ACTIVE,
        ).count()

        if active_count >= company.max_projects:
            return Response(
                {"error": "Project limit reached"},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = ProjectSerializer(
            data={**request.data, "company": company.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(company=company)


        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectArchiveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id: int):
        company = get_company_from_request(request)
        company_user = get_company_user(request, company)

        project = get_object_or_404(
            Project,
            id=project_id,
            company=company,
        )

        if (
            project.project_admin != company_user
            and not has_permission(company_user, "can_manage_project_users")
        ):
            return Response(
                {"error": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        project.archive()

        return Response(
            {"status": "archived"},
            status=status.HTTP_200_OK,
        )
    
class ProjectCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company = get_company_from_request(request)
        company_user = get_company_user(request, company)

        require_permission(company_user, "can_create_project")

        serializer = ProjectSerializer(
            data=request.data,
            context={"company": company},
        )
        serializer.is_valid(raise_exception=True)

        project = create_project(
            company=company,
            data=serializer.validated_data,
        )

        return Response(
            ProjectSerializer(project).data,
            status=status.HTTP_201_CREATED,
        )

class RoleListView(APIView):
    """
    Read-only role visibility for company admins.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = get_company_from_request(request)
        company_user = get_company_user(request, company)

        # Admin-only
        require_permission(company_user, "can_manage_roles")

        roles = Role.objects.filter(
            Q(is_system_role=True) | Q(company=company)
        ).order_by("is_system_role", "name")

        return Response(
            RoleSerializer(roles, many=True).data,
            status=status.HTTP_200_OK,
        )


class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        company = get_company_from_request(request)

        project = get_object_or_404(
            Project,
            id=project_id,
            company=company,
            status=Project.STATUS_ACTIVE,
        )

        # 🔑 CAPTURE project membership (this was missing)
        project_user = get_project_user(project, request.user)

        return Response(
            {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status,

                # Feature flags (sidebar visibility)
                "flows_enabled": project.flows_enabled,
                "test_cases_enabled": project.test_cases_enabled,
                "builder_enabled": project.builder_enabled,
                "execution_enabled": project.execution_enabled,
                "reports_enabled": project.reports_enabled,
                "test_planning_enabled": project.test_planning_enabled,
                "template_needs_approval": project.template_needs_approval,

                # Project-scoped permissions (UI authority)
                "permissions": project_user.role.permissions_json,
                "project_role": project_user.role.name,
            },
            status=200,
        )
