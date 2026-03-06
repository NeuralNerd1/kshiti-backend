"""Verify data counts in Supabase PostgreSQL."""
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.local"
import django
django.setup()
from django.apps import apps

models_to_check = [
    "auth.User",
    "company_auth.Company", "company_auth.CompanyUser", "company_auth.AuthAuditLog", "company_auth.UserProfile",
    "company_operations.Role", "company_operations.Project", "company_operations.ProjectRole", "company_operations.ProjectUser",
    "planning_registry.ActionCategory", "planning_registry.ActionDefinition",
    "project_planning.FlowFolder", "project_planning.Flow", "project_planning.FlowVersion",
    "project_planning.TestCaseFolder", "project_planning.TestCase", "project_planning.TestCaseVersion",
    "project_planning.TestSuite", "project_planning.LocalTestCaseFolder", "project_planning.LocalTestCase",
    "project_planning.LocalTestCaseVersion",
    "project_planning.VariableFolder", "project_planning.Variable",
    "project_planning.ElementFolder", "project_planning.Element", "project_planning.ElementLocator",
    "project_planning.TestCaseIdentity",
    "test_plan.ProcessTemplate", "test_plan.PlanningEntityType", "test_plan.EntityFieldDefinition",
    "test_plan.WorkflowDefinition", "test_plan.WorkflowState", "test_plan.WorkflowTransition",
    "test_plan.PlanningItem", "test_plan.PlanningItemFieldValue",
    "test_plan.ProjectPlanningConfig", "test_plan.ProjectTemplateBinding", "test_plan.KanbanBoardConfig",
]

print("MODEL".ljust(50) + "COUNT")
print("-" * 58)
total = 0
for label in models_to_check:
    try:
        M = apps.get_model(label)
        c = M.objects.count()
        total += c
        print(label.ljust(50) + str(c).rjust(6))
    except Exception as e:
        print(label.ljust(50) + "ERR: " + str(e)[:40])

print("-" * 58)
print("TOTAL".ljust(50) + str(total).rjust(6))
