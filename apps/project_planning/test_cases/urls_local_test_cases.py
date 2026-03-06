from django.urls import path
from apps.project_planning.test_cases.views_local_test_cases import (
    ListLocalTestCaseFoldersAPI,
    CreateLocalTestCaseFolderAPI,
    UpdateLocalTestCaseFolderAPI,
    CreateLocalTestCaseAPI,
    ListLocalTestCasesAPI,
    LocalTestCaseDetailAPI,
    ArchiveLocalTestCaseAPI,
    SaveLocalTestCaseBuilderAPI,
)

urlpatterns = [
    # ─── FOLDERS ───
    path("folders/", CreateLocalTestCaseFolderAPI.as_view()),
    path("folders/list/", ListLocalTestCaseFoldersAPI.as_view()),
    path("folders/<int:folder_id>/", UpdateLocalTestCaseFolderAPI.as_view()),

    # ─── LOCAL TEST CASES ───
    path("", CreateLocalTestCaseAPI.as_view()),
    path("list/", ListLocalTestCasesAPI.as_view()),
    path("<int:test_case_id>/", LocalTestCaseDetailAPI.as_view()),
    path("<int:test_case_id>/archive/", ArchiveLocalTestCaseAPI.as_view()),
    path("<int:test_case_id>/builder/save/", SaveLocalTestCaseBuilderAPI.as_view()),
]
