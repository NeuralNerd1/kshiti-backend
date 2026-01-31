from django.urls import path, include

# Flow views
from apps.project_planning.views.flows import (
    FlowListCreateView,
    FlowDetailView,
    FlowVersionCreateView,
    FlowRollbackView,
    FlowArchiveView,
    FlowUpdateView,
    FlowDeleteView,
)

# Folder views
from apps.project_planning.views.folders import (
    FolderListCreateView,
    FolderRenameView,
    FolderDeleteView,
)

urlpatterns = [
    # ---------------- FLOWS ----------------
    path(
        "projects/<int:project_id>/flows/",
        FlowListCreateView.as_view(),
        name="flow-list-create",
    ),
    path(
        "flows/<int:flow_id>/",
        FlowDetailView.as_view(),
        name="flow-detail",
    ),
    path(
        "flows/<int:flow_id>/versions/",
        FlowVersionCreateView.as_view(),
        name="flow-version-create",
    ),
    path(
        "flows/<int:flow_id>/versions/<int:version_number>/rollback/",
        FlowRollbackView.as_view(),
        name="flow-version-rollback",
    ),
    path(
        "flows/<int:flow_id>/archive/",
        FlowArchiveView.as_view(),
        name="flow-archive",
    ),
    path(
        "flows/<int:flow_id>/edit/",
        FlowUpdateView.as_view(),
        name="flow-edit",
    ),
    path(
        "flows/<int:flow_id>/delete/",
        FlowDeleteView.as_view(),
        name="flow-delete",
    ),

    # ---------------- FOLDERS ----------------
    path(
        "projects/<int:project_id>/folders/",
        FolderListCreateView.as_view(),
        name="folder-list-create",
    ),
    path(
        "folders/<int:folder_id>/rename/",
        FolderRenameView.as_view(),
        name="folder-rename",
    ),
    path(
        "folders/<int:folder_id>/delete/",
        FolderDeleteView.as_view(),
        name="folder-delete",
    ),
    path(
        "test-cases/",
        include("apps.project_planning.test_cases.urls"),
    ),
    path(
    "variables/",
    include("apps.project_planning.variables.urls"),
),
path(
    "elements/",
    include("apps.project_planning.elements.urls"),
),

]
