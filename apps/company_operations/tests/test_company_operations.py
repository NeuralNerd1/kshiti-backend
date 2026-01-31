from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from apps.company_auth.models import Company, CompanyUser
from apps.company_operations.models import Role, Project


class CompanyOperationsE2ETest(TestCase):
    """
    End-to-end tests for Company Operations
    Backend-aligned. Do NOT modify backend to satisfy tests.
    """

    def setUp(self):
        self.client = APIClient()

        # ---------- SYSTEM ROLES ----------
        self.admin_role = Role.objects.create(
            name="Admin",
            is_system_role=True,
            permissions_json={
                "can_manage_company": True,
                "can_manage_users": True,
                "can_create_project": True,
                "can_manage_roles": True,
                "can_view_all_projects": True,
            },
        )

        self.member_role = Role.objects.create(
            name="Member",
            is_system_role=True,
            permissions_json={
                "can_view_project": True,
            },
        )

        # ---------- COMPANY ----------
        self.company = Company.objects.create(
            name="Acme Corp",
            slug="acme",
            status=Company.STATUS_ACTIVE,
            is_login_allowed=True,
            max_projects=2,
            can_create_projects=True,
        )

        # ---------- COMPANY ROLE ----------
        self.project_admin_role = Role.objects.create(
            name="Project Admin",
            company=self.company,
            permissions_json={
                "can_view_project": True,
                "can_edit_project": True,
                "can_manage_project_users": True,
            },
        )

        # ---------- USERS ----------
        self.admin_user = User.objects.create_user(
            username="admin@acme.com",
            email="admin@acme.com",
            password="password",
        )

        self.pm_user = User.objects.create_user(
            username="pm@acme.com",
            email="pm@acme.com",
            password="password",
        )

        self.member_user = User.objects.create_user(
            username="member@acme.com",
            email="member@acme.com",
            password="password",
        )

        # ---------- COMPANY USERS ----------
        self.admin_cu = CompanyUser.objects.create(
            user=self.admin_user,
            company=self.company,
            role=self.admin_role,
            is_active=True,
        )

        self.pm_cu = CompanyUser.objects.create(
            user=self.pm_user,
            company=self.company,
            role=self.project_admin_role,
            is_active=True,
        )

        self.member_cu = CompanyUser.objects.create(
            user=self.member_user,
            company=self.company,
            role=self.member_role,
            is_active=True,
        )

    # ----------------------------------------------------
    # PROJECT CREATION
    # ----------------------------------------------------

    def test_admin_can_create_project(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.post(
            "/company/projects/",
            {
                "name": "Backend Revamp",
                "description": "Refactor backend",
                "max_team_members": 5,
                "project_admin": self.pm_cu.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)

    def test_member_cannot_create_project(self):
        self.client.force_authenticate(self.member_user)

        response = self.client.post(
            "/company/projects/",
            {
                "name": "Unauthorized Project",
                "description": "",
                "max_team_members": 3,
                "project_admin": self.pm_cu.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ----------------------------------------------------
    # PROJECT LIMIT
    # ----------------------------------------------------

    def test_project_limit_enforced(self):
        self.client.force_authenticate(self.admin_user)

        Project.objects.create(
            company=self.company,
            name="P1",
            description="",
            max_team_members=2,
            project_admin=self.pm_cu,
        )

        Project.objects.create(
            company=self.company,
            name="P2",
            description="",
            max_team_members=2,
            project_admin=self.pm_cu,
        )

        response = self.client.post(
            "/company/projects/",
            {
                "name": "P3",
                "description": "",
                "max_team_members": 2,
                "project_admin": self.pm_cu.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    # ----------------------------------------------------
    # ARCHIVING
    # ----------------------------------------------------

    def test_archived_project_not_counted(self):
        self.client.force_authenticate(self.admin_user)

        p = Project.objects.create(
            company=self.company,
            name="Old Project",
            description="",
            max_team_members=2,
            project_admin=self.pm_cu,
        )
        p.archive()

        response = self.client.post(
            "/company/projects/",
            {
                "name": "New Project",
                "description": "",
                "max_team_members": 2,
                "project_admin": self.pm_cu.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_archived_project_not_visible(self):
        self.client.force_authenticate(self.admin_user)

        p = Project.objects.create(
            company=self.company,
            name="Hidden Project",
            description="",
            max_team_members=2,
            project_admin=self.pm_cu,
        )
        p.archive()

        response = self.client.get("/company/projects/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    # ----------------------------------------------------
    # PERMISSIONS
    # ----------------------------------------------------

    def test_project_admin_cannot_view_all_projects(self):
        self.client.force_authenticate(self.pm_user)

        response = self.client.get("/company/projects/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_user_blocked(self):
        self.admin_cu.is_active = False
        self.admin_cu.save()

        self.client.force_authenticate(self.admin_user)

        response = self.client.get("/company/projects/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
