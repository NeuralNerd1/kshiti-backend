from django.urls import path

from apps.project_planning.variables.views_folders import (
    CreateVariableFolderAPI,
    ListVariableFoldersAPI,
    RenameVariableFolderAPI,
    DeleteVariableFolderAPI,
)

from apps.project_planning.variables.views_variables import (
    CreateVariableAPI,
    ListVariablesAPI,
    UpdateVariableAPI,
    DeleteVariableAPI,
)

urlpatterns = [
    # folders
    path("folders/", CreateVariableFolderAPI.as_view()),
    path("folders/list/", ListVariableFoldersAPI.as_view()),
    path("folders/<int:folder_id>/rename/", RenameVariableFolderAPI.as_view()),
    path("folders/<int:folder_id>/delete/", DeleteVariableFolderAPI.as_view()),

    # variables
    path("", CreateVariableAPI.as_view()),
    path("list/", ListVariablesAPI.as_view()),
    path("<int:variable_id>/", UpdateVariableAPI.as_view()),
    path("<int:variable_id>/delete/", DeleteVariableAPI.as_view()),
]
