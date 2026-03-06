from django.urls import path
from .views import BridgeAuthVerifyView, BridgeProjectSnapshotView

urlpatterns = [
    # Call 1 — identity + permissions
    path("auth/verify/", BridgeAuthVerifyView.as_view()),

    # Call 2 — complete project snapshot
    path("project-snapshot/<int:project_id>/", BridgeProjectSnapshotView.as_view()),
]
