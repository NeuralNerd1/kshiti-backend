from django.urls import path

from apps.project_planning.elements.views_folders import (
    CreateElementFolderAPI,
    ListElementFoldersAPI,
    RenameElementFolderAPI,
    DeleteElementFolderAPI,
)

from apps.project_planning.elements.views_elements import (
    CreateElementAPI,
    ListElementsAPI,
    ElementDetailAPI,
    UpdateElementAPI,
    DeleteElementAPI,
)

from apps.project_planning.elements.views_locators import (
    UpdateLocatorAPI,
    DeleteLocatorAPI,
)

urlpatterns = [
    # --------------------
    # FOLDERS
    # --------------------
    path("folders/", CreateElementFolderAPI.as_view()),
    path("folders/list/", ListElementFoldersAPI.as_view()),
    path("folders/<int:folder_id>/rename/", RenameElementFolderAPI.as_view()),
    path("folders/<int:folder_id>/delete/", DeleteElementFolderAPI.as_view()),

    # --------------------
    # ELEMENTS
    # --------------------
    path("", CreateElementAPI.as_view()),
    path("list/", ListElementsAPI.as_view()),
    path("<int:element_id>/", ElementDetailAPI.as_view()),
    path("<int:element_id>/edit/", UpdateElementAPI.as_view()),
    path("<int:element_id>/delete/", DeleteElementAPI.as_view()),

    # --------------------
    # LOCATORS
    # --------------------
    path(
        "locators/<int:locator_id>/",
        UpdateLocatorAPI.as_view(),
    ),
    path(
        "locators/<int:locator_id>/delete/",
        DeleteLocatorAPI.as_view(),
    ),
]
