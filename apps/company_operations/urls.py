# apps/company_operations/urls.py

from django.urls import path
from .views import CompanyUsersView, ProjectsView
from .views import (
    ProjectListView,
    ProjectCreateView,
    ProjectArchiveView,
    ProjectDetailView
)
from apps.company_operations.views_project_users import (
    ProjectUsersView,
    ProjectUserDetailView,
)

from .views import RoleListView
urlpatterns = [
    path("projects/", ProjectsView.as_view()),
    path("projects/<int:project_id>/archive/", ProjectArchiveView.as_view()),
    path("users/", CompanyUsersView.as_view()),
    path("projects/", ProjectListView.as_view()),
    path("projects/create/", ProjectCreateView.as_view()),
    path("roles/", RoleListView.as_view()),
    path(
        "projects/<int:project_id>/users/",
        ProjectUsersView.as_view(),
    ),
    path(
        "projects/<int:project_id>/users/<int:member_id>/",
        ProjectUserDetailView.as_view(),
    ),
    path("projects/<int:project_id>/", ProjectDetailView.as_view()),

]

