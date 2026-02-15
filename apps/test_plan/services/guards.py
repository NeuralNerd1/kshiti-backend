from django.core.exceptions import PermissionDenied


def ensure_test_planning_enabled(project):
    """
    Global isolation guard for Test Plan module.
    """
    if not project.test_planning_enabled:
        raise PermissionDenied("Test planning is disabled for this project.")
