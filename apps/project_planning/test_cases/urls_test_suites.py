from django.urls import path
from apps.project_planning.test_cases.views_test_suites import (
    ListCreateTestSuiteAPI,
    TestSuiteDetailAPI,
)

urlpatterns = [
    path("", ListCreateTestSuiteAPI.as_view()),
    path("list/", ListCreateTestSuiteAPI.as_view()),
    path("<int:suite_id>/", TestSuiteDetailAPI.as_view()),
]
