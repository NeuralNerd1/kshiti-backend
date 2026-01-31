# =====================================================
# PERMISSION CONSTANTS (IMPORTABLE)
# =====================================================

# ---- FLOWS ----
CAN_CREATE_FLOWS = "can_create_flows"
CAN_EDIT_FLOWS = "can_edit_flows"
CAN_VIEW_FLOWS = "can_view_flows"

# ---- TEST CASES ----
CAN_CREATE_TEST_CASES = "can_create_test_cases"
CAN_EDIT_TEST_CASES = "can_edit_test_cases"
CAN_VIEW_TEST_CASES = "can_view_test_cases"

# ---- BUILDER / EXECUTION ----
CAN_USE_BUILDER = "can_use_builder"
CAN_EXECUTE_TESTS = "can_execute_tests"

# ---- REPORTS ----
CAN_VIEW_REPORTS = "can_view_reports"
CAN_DOWNLOAD_REPORTS = "can_download_reports"



# =====================================================
# COMPANY-LEVEL PERMISSIONS
# =====================================================

COMPANY_PERMISSIONS = {
    "can_manage_company",
    "can_manage_users",
    "can_manage_roles",
    "can_view_all_projects",
    "can_create_project",
}

# =====================================================
# PROJECT-LEVEL PERMISSIONS
# =====================================================

PROJECT_PERMISSIONS = {
    "can_edit_project",
    "can_manage_project_users",
    "can_view_project",
}

# =====================================================
# FEATURE-3 — PLANNING (FLOWS)
# =====================================================

FLOW_PERMISSIONS = {
    CAN_CREATE_FLOWS,
    CAN_EDIT_FLOWS,
    CAN_VIEW_FLOWS,
}


# =====================================================
# FEATURE-3 — TEST CASES
# =====================================================

TEST_CASE_PERMISSIONS = {
    CAN_CREATE_TEST_CASES,
    CAN_EDIT_TEST_CASES,
    CAN_VIEW_TEST_CASES,
}

# =====================================================
# FEATURE-3 — BUILDER & EXECUTION
# =====================================================

BUILDER_EXECUTION_PERMISSIONS = {
    CAN_USE_BUILDER,
    CAN_EXECUTE_TESTS,
}

# =====================================================
# FEATURE-3 — REPORTS
# =====================================================

REPORT_PERMISSIONS = {
    CAN_VIEW_REPORTS,
    CAN_DOWNLOAD_REPORTS,
}

# =====================================================
# CANONICAL PERMISSION SET
# =====================================================

ALL_PERMISSION_KEYS = (
    COMPANY_PERMISSIONS
    | PROJECT_PERMISSIONS
    | FLOW_PERMISSIONS
    | TEST_CASE_PERMISSIONS
    | BUILDER_EXECUTION_PERMISSIONS
    | REPORT_PERMISSIONS
)
