# =====================================================
# FEATURE 3 — PROJECT-LEVEL PERMISSIONS
# =====================================================

# ---- PROJECT VISIBILITY & MANAGEMENT ----
CAN_VIEW_PROJECT = "can_view_project"
CAN_EDIT_PROJECT = "can_edit_project"
CAN_MANAGE_PROJECT_USERS = "can_manage_project_users"

# ---- PLANNING / FLOWS ----
CAN_VIEW_FLOWS = "can_view_flows"
CAN_CREATE_FLOWS = "can_create_flows"
CAN_EDIT_FLOWS = "can_edit_flows"

# ---- TEST CASES (✅ ADD THIS) ----
CAN_VIEW_TEST_CASES = "can_view_test_cases"
CAN_CREATE_TEST_CASES = "can_create_test_cases"
CAN_EDIT_TEST_CASES = "can_edit_test_cases"

# ---- BUILDER / EXECUTION ----
CAN_USE_BUILDER = "can_use_builder"
CAN_EXECUTE_TESTS = "can_execute_tests"

# ---- REPORTS ----
CAN_VIEW_REPORTS = "can_view_reports"

# ---- ELEMENTS ----
CAN_CAPTURE_ELEMENTS = "can_capture_elements"

# =====================================================
# FEATURE 4 — TEST PLAN PERMISSIONS
# =====================================================

CAN_CREATE_TEMPLATES = "can_create_templates"
CAN_EDIT_TEMPLATES = "can_edit_templates"
CAN_SUBMIT_TEMPLATES = "can_submit_templates"
CAN_APPROVE_TEMPLATES = "can_approve_templates"

CAN_CREATE_PLANNING_ITEMS = "can_create_planning_items"
CAN_EDIT_PLANNING_ITEMS = "can_edit_planning_items"
CAN_REVIEW_PLANNING_ITEMS = "can_review_planning_items"
CAN_BIND_EXECUTION = "can_bind_execution"
CAN_TRACK_TIME = "can_track_time"


# =====================================================
# CANONICAL PROJECT PERMISSION SET
# =====================================================

PROJECT_PERMISSION_KEYS = {
    # project
    CAN_VIEW_PROJECT,
    CAN_EDIT_PROJECT,
    CAN_MANAGE_PROJECT_USERS,

    # flows
    CAN_VIEW_FLOWS,
    CAN_CREATE_FLOWS,
    CAN_EDIT_FLOWS,

    # ✅ test cases
    CAN_VIEW_TEST_CASES,
    CAN_CREATE_TEST_CASES,
    CAN_EDIT_TEST_CASES,

    # builder
    CAN_USE_BUILDER,
    CAN_EXECUTE_TESTS,

    # reports
    CAN_VIEW_REPORTS,

    CAN_CAPTURE_ELEMENTS,

    CAN_CREATE_TEMPLATES,
    CAN_EDIT_TEMPLATES,
    CAN_SUBMIT_TEMPLATES,
    CAN_APPROVE_TEMPLATES,
    CAN_CREATE_PLANNING_ITEMS,
    CAN_EDIT_PLANNING_ITEMS,
    CAN_REVIEW_PLANNING_ITEMS,
    CAN_BIND_EXECUTION,
    CAN_TRACK_TIME,
}
