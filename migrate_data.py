"""
Migrate data from SQLite to PostgreSQL (Supabase).

Uses Django's ORM with both databases configured before django.setup().
"""
import os
import sys

# MUST set settings module FIRST
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.local"

# Patch the settings BEFORE django.setup()
# We import the module and inject the SQLite database config
import importlib
settings_mod = importlib.import_module("config.settings.local")

SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite3")

# We need to add the sqlite_old database BEFORE django.setup()
# So we monkey-patch the DATABASES dict in the settings module
if not hasattr(settings_mod, "DATABASES"):
    print("FATAL: DATABASES not found in settings")
    sys.exit(1)

settings_mod.DATABASES["sqlite_old"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": SQLITE_PATH,
}

import django
django.setup()

from django.apps import apps
from django.db import connections
from django.core import serializers

# Define the order to respect foreign key dependencies
APP_ORDER = [
    ("auth", "Group"),
    ("auth", "User"),
    ("company_auth", "Company"),
    ("company_operations", "Role"),
    ("company_auth", "CompanyUser"),
    ("company_auth", "AuthAuditLog"),
    ("company_auth", "UserProfile"),
    ("company_operations", "Project"),
    ("company_operations", "ProjectRole"),
    ("company_operations", "ProjectUser"),
    ("planning_registry", "ActionCategory"),
    ("planning_registry", "ActionDefinition"),
    ("project_planning", "FlowFolder"),
    ("project_planning", "Flow"),
    ("project_planning", "FlowVersion"),
    ("project_planning", "TestCaseFolder"),
    ("project_planning", "TestCase"),
    ("project_planning", "TestCaseVersion"),
    ("project_planning", "TestSuite"),
    ("project_planning", "LocalTestCaseFolder"),
    ("project_planning", "LocalTestCase"),
    ("project_planning", "LocalTestCaseVersion"),
    ("project_planning", "VariableFolder"),
    ("project_planning", "Variable"),
    ("project_planning", "ElementFolder"),
    ("project_planning", "Element"),
    ("project_planning", "ElementLocator"),
    ("project_planning", "TestCaseIdentity"),
    ("test_plan", "ProcessTemplate"),
    ("test_plan", "PlanningEntityType"),
    ("test_plan", "EntityFieldDefinition"),
    ("test_plan", "WorkflowDefinition"),
    ("test_plan", "WorkflowState"),
    ("test_plan", "WorkflowTransition"),
    ("test_plan", "PlanningDependency"),
    ("test_plan", "TimeTrackingRule"),
    ("test_plan", "PlanningItem"),
    ("test_plan", "PlanningItemFieldValue"),
    ("test_plan", "TimeTrackingSession"),
    ("test_plan", "ExecutionBinding"),
    ("test_plan", "ProjectPlanningConfig"),
    ("test_plan", "ProjectTemplateBinding"),
    ("test_plan", "KanbanBoardConfig"),
]


def migrate_data():
    total = 0
    errors = []

    for app_label, model_name in APP_ORDER:
        try:
            Model = apps.get_model(app_label, model_name)
        except LookupError:
            print(f"  SKIP  {app_label}.{model_name} — not found")
            continue

        try:
            objs = list(Model.objects.using("sqlite_old").all())
            count = len(objs)
            if count == 0:
                print(f"  EMPTY {app_label}.{model_name}")
                continue

            data = serializers.serialize("json", objs)

            for deserialized in serializers.deserialize("json", data, using="default"):
                deserialized.save(using="default")

            total += count
            print(f"  OK    {app_label}.{model_name}: {count} objects")
            sys.stdout.flush()

        except Exception as e:
            msg = f"  ERROR {app_label}.{model_name}: {e}"
            print(msg)
            errors.append(msg)
            sys.stdout.flush()

    # M2M: PlanningItem.assigned_users
    try:
        PlanningItem = apps.get_model("test_plan", "PlanningItem")
        items = PlanningItem.objects.using("sqlite_old").filter(
            assigned_users__isnull=False
        ).distinct()
        m2m = 0
        for item in items:
            ids = list(
                item.assigned_users.using("sqlite_old").values_list("id", flat=True)
            )
            if ids:
                target = PlanningItem.objects.using("default").get(pk=item.pk)
                target.assigned_users.set(ids)
                m2m += len(ids)
        print(f"  {'OK' if m2m else 'EMPTY'}    M2M assigned_users: {m2m} relations")
    except Exception as e:
        print(f"  ERROR M2M: {e}")

    print(f"\n{'='*50}")
    print(f"Total migrated: {total}")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
    else:
        print("No errors!")


if __name__ == "__main__":
    print("=" * 50)
    print("SQLite -> Supabase PostgreSQL Data Migration")
    print("=" * 50)

    # Verify connections
    try:
        connections["default"].ensure_connection()
        print(f"PostgreSQL OK: {connections['default'].settings_dict['HOST']}")
    except Exception as e:
        print(f"FATAL PostgreSQL: {e}")
        sys.exit(1)

    try:
        connections["sqlite_old"].ensure_connection()
        print(f"SQLite OK: {SQLITE_PATH}")
    except Exception as e:
        print(f"FATAL SQLite: {e}")
        sys.exit(1)

    print()
    migrate_data()
