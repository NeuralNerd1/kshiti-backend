from django.urls import path

from apps.project_planning.test_cases.views_folders import (
    CreateTestCaseFolderAPI,
    ListTestCaseFoldersAPI,
    RenameTestCaseFolderAPI,
    MoveTestCaseFolderAPI,
    ArchiveTestCaseFolderAPI,
)
from apps.project_planning.test_cases.views_test_cases import (
    CreateTestCaseAPI,
    ListTestCasesAPI,
    TestCaseDetailAPI,
    SaveTestCaseAPI,
    ArchiveTestCaseAPI,
)
from apps.project_planning.test_cases.views_builder import (
    SaveTestCaseBuilderAPI,
)
from apps.project_planning.test_cases.views_import_flow import (
    ImportFlowIntoTestCaseAPI,
)

urlpatterns = [
    # ----------------------
    # FOLDERS
    # ----------------------
    path("folders/", CreateTestCaseFolderAPI.as_view()),
    path("folders/list/", ListTestCaseFoldersAPI.as_view()),

    path(
        "folders/<int:folder_id>/rename/",
        RenameTestCaseFolderAPI.as_view(),
    ),
    path(
        "folders/<int:folder_id>/move/",
        MoveTestCaseFolderAPI.as_view(),
    ),
    path(
        "folders/<int:folder_id>/archive/",
        ArchiveTestCaseFolderAPI.as_view(),
    ),

    # ----------------------
    # TEST CASES
    # ----------------------
    path("", CreateTestCaseAPI.as_view()),
    path("list/", ListTestCasesAPI.as_view()),
    path("<int:test_case_id>/", TestCaseDetailAPI.as_view()),
    path("<int:test_case_id>/archive/", ArchiveTestCaseAPI.as_view()),

    # ----------------------
    # BUILDER
    # ----------------------
    path(
        "<int:test_case_id>/builder/save/",
        SaveTestCaseBuilderAPI.as_view(),
    ),

    # ----------------------
    # IMPORT FLOW
    # ----------------------
    path(
        "<int:test_case_id>/import-flow/",
        ImportFlowIntoTestCaseAPI.as_view(),
    ),
]

