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
}
