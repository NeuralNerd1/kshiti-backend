"""
Bridge Views
============

Call 1: POST /bridge/auth/verify/
    Validates JWT or API key — returns full user identity,
    company, all projects, permissions, and feature flags.

Call 2: GET  /bridge/project-snapshot/<project_id>/
    Returns the complete project data snapshot:
    team, action registry, variables, elements (with locators),
    flows (with latest version steps), test cases (with latest version),
    and execution bindings.

Both endpoints support:
- JWT auth (standard user session, e.g. frontend sharing its token)
- X-Bridge-Api-Key header (machine-to-machine, server-to-server)
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.company_auth.models import CompanyUser
from apps.company_operations.models import Project, ProjectUser
from apps.project_planning.models import (
    Flow, FlowVersion,
    Variable, VariableFolder,
    Element, ElementFolder, ElementLocator,
    TestCase, TestCaseVersion,
    TestSuite, LocalTestCase, LocalTestCaseVersion,
    TestCaseIdentity,
)
from apps.planning_registry.models import ActionCategory, ActionDefinition
from apps.test_plan.models import PlanningItem, ExecutionBinding

from .auth import authenticate_bridge_request


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _serialize_user(user):
    profile = getattr(user, "profile", None)
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "display_name": profile.display_name if profile else "",
        "avatar_url": profile.avatar.url if (profile and profile.avatar) else None,
    }


def _serialize_company(company):
    return {
        "id": company.id,
        "name": company.name,
        "slug": company.slug,
        "status": company.status,
        "features": {
            "can_create_projects": company.can_create_projects,
            "custom_roles_enabled": company.custom_roles_enabled,
            "max_projects": company.max_projects,
        },
    }


def _serialize_project_for_user(project, project_user):
    role = project_user.role
    permissions = role.permissions_json if role else {}
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "role": role.name if role else None,
        "permissions": permissions,
        "feature_flags": {
            "flows_enabled": project.flows_enabled,
            "test_cases_enabled": project.test_cases_enabled,
            "builder_enabled": project.builder_enabled,
            "execution_enabled": project.execution_enabled,
            "reports_enabled": project.reports_enabled,
            "element_capture_enabled": project.element_capture_enabled,
            "test_planning_enabled": project.test_planning_enabled,
            "can_configure_processes": project.can_configure_processes,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# CALL 1 — POST /bridge/auth/verify/
# ─────────────────────────────────────────────────────────────────────────────

class BridgeAuthVerifyView(APIView):
    """
    Call 1: Validates JWT or API key.

    JWT mode:
        Authorization: Bearer <jwt_token>
        Returns: full user identity + all projects they are a member of.

    API key mode (machine-to-machine, no user context):
        X-Bridge-Api-Key: <key>
        Body: { "user_id": <int> }   ← optional, look up a specific user
        Returns: same as JWT mode for that user, or a service-level token ack.
    """

    authentication_classes = []   # Handle auth manually below
    permission_classes = [AllowAny]

    def post(self, request):
        # Custom dual-mode auth
        from rest_framework_simplejwt.authentication import JWTAuthentication
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

        user = None
        error = None

        # ── Mode 1: Try JWT first ──────────────────────────────────────────
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                jwt_auth = JWTAuthentication()
                validated = jwt_auth.get_validated_token(
                    jwt_auth.get_raw_token(
                        jwt_auth.get_header(request)
                    )
                )
                user = jwt_auth.get_user(validated)
            except (InvalidToken, TokenError) as e:
                return Response({"error": f"Invalid JWT: {e}"}, status=401)

        # ── Mode 2: API key ────────────────────────────────────────────────
        if user is None:
            _user, error = authenticate_bridge_request(request)
            if error:
                return Response(error, status=401)

            # API key auth — look up user by ID from body
            user_id = request.data.get("user_id")
            if user_id:
                from django.contrib.auth.models import User as DjangoUser
                try:
                    user = DjangoUser.objects.get(id=user_id, is_active=True)
                except DjangoUser.DoesNotExist:
                    return Response({"error": "User not found."}, status=404)
            else:
                # Pure M2M call — return service-level ack (no user context)
                return Response({
                    "authenticated": True,
                    "mode": "api_key",
                    "user": None,
                    "message": "Valid API key. Provide user_id in body for user context.",
                })

        # ── Build full identity response ───────────────────────────────────
        try:
            company_user = user.company_membership
        except CompanyUser.DoesNotExist:
            return Response({"error": "User has no company membership."}, status=403)

        company = company_user.company

        # All active project memberships for this user
        memberships = (
            ProjectUser.objects
            .filter(company_user=company_user, is_active=True)
            .select_related("project", "role")
        )

        projects = [
            _serialize_project_for_user(m.project, m)
            for m in memberships
            if m.project.status == Project.STATUS_ACTIVE
        ]

        return Response({
            "authenticated": True,
            "mode": "jwt" if auth_header.startswith("Bearer ") else "api_key",
            "user": _serialize_user(user),
            "company": _serialize_company(company),
            "projects": projects,
        })


# ─────────────────────────────────────────────────────────────────────────────
# CALL 2 — GET /bridge/project-snapshot/<project_id>/
# ─────────────────────────────────────────────────────────────────────────────

class BridgeProjectSnapshotView(APIView):
    """
    Call 2: Returns the complete project data snapshot for an external app.

    Includes:
    - team (ProjectUser → CompanyUser → User)
    - action_registry (ActionCategory + ActionDefinition with parameter_schema)
    - variables (Variable with folder paths)
    - elements (Element with all ElementLocators)
    - flows (Flow metadata + latest FlowVersion steps_json)
    - test_cases (TestCase + latest TestCaseVersion: pre_conditions, steps, expected_outcomes)
    - test_suites (TestSuite metadata + selected test_case_ids)
    - local_test_cases (LocalTestCase + latest LocalTestCaseVersion: pre_conditions, steps, expected_outcomes)
    - execution_bindings (PlanningItem → Flow/TestCase linkage)
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, project_id):
        # Authenticate
        from rest_framework_simplejwt.authentication import JWTAuthentication
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

        user = None
        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            try:
                jwt_auth = JWTAuthentication()
                validated = jwt_auth.get_validated_token(
                    jwt_auth.get_raw_token(jwt_auth.get_header(request))
                )
                user = jwt_auth.get_user(validated)
            except (InvalidToken, TokenError) as e:
                return Response({"error": f"Invalid JWT: {e}"}, status=401)

        if user is None:
            _user, error = authenticate_bridge_request(request)
            if error:
                return Response(error, status=401)
                
            # Allow M2M requests to specify the user context via query param
            user_id = request.query_params.get("user_id")
            if user_id:
                from django.contrib.auth.models import User as DjangoUser
                try:
                    user = DjangoUser.objects.get(id=user_id, is_active=True)
                except DjangoUser.DoesNotExist:
                    pass

        # Validate project exists
        try:
            project = Project.objects.select_related("company").get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=404)

        # Lazy backfill check (One-time sync for existing data)
        # If identities are missing for this project, trigger a backfill
        tc_count = TestCase.objects.filter(project=project).count()
        ltc_count = LocalTestCase.objects.filter(project=project).count()
        ident_count = TestCaseIdentity.objects.filter(project=project).count()
        
        if ident_count < (tc_count + ltc_count):
            TestCaseIdentity.perform_backfill(project)

        # If JWT user — verify they are a project member
        if user:
            try:
                cu = user.company_membership
                membership = ProjectUser.objects.get(
                    project=project, company_user=cu, is_active=True
                )
            except (CompanyUser.DoesNotExist, ProjectUser.DoesNotExist):
                return Response({"error": "Access denied."}, status=403)

        # ── 1. TEAM ───────────────────────────────────────────────────────
        members = (
            ProjectUser.objects
            .filter(project=project, is_active=True)
            .select_related("company_user__user", "company_user__user__profile", "role")
        )

        team = [
            {
                "project_user_id": m.id,
                "user": _serialize_user(m.company_user.user),
                "role": m.role.name if m.role else None,
                "permissions": m.role.permissions_json if m.role else {},
            }
            for m in members
        ]

        # ── 2. ACTION REGISTRY ────────────────────────────────────────────
        categories = ActionCategory.objects.prefetch_related("actions").order_by("order")
        action_registry = {
            "categories": [
                {"key": c.key, "name": c.name, "order": c.order}
                for c in categories
            ],
            "actions": [
                {
                    "action_key": a.action_key,
                    "action_name": a.action_name,
                    "category": a.category.key,
                    "description": a.description,
                    "is_risky": a.is_risky,
                    "parameter_schema": a.parameter_schema,
                }
                for c in categories
                for a in c.actions.all()
            ],
        }

        # ── 3. VARIABLES ──────────────────────────────────────────────────
        variables_qs = (
            Variable.objects
            .filter(project=project)
            .select_related("folder")
            .order_by("folder__path", "key")
        )
        variables = [
            {
                "id": v.id,
                "key": v.key,
                "value": v.value,
                "description": v.description,
                "folder": v.folder.path if v.folder else None,
            }
            for v in variables_qs
        ]

        # ── 4. ELEMENTS (Object Repository) ───────────────────────────────
        elements_qs = (
            Element.objects
            .filter(project=project)
            .select_related("folder")
            .prefetch_related("locators")
            .order_by("folder__path", "name")
        )
        elements = [
            {
                "id": e.id,
                "name": e.name,
                "page_url": e.page_url,
                "folder": e.folder.path if e.folder else None,
                "locators": [
                    {
                        "selector_type": loc.selector_type,
                        "selector_value": loc.selector_value,
                        "priority": loc.priority,
                        "is_active": loc.is_active,
                    }
                    for loc in sorted(e.locators.all(), key=lambda l: l.priority)
                    if loc.is_active
                ],
            }
            for e in elements_qs
        ]

        # ── 5. FLOWS ──────────────────────────────────────────────────────
        flows_qs = (
            Flow.objects
            .filter(project=project, status=Flow.STATUS_SAVED)
            .select_related("folder")
            .order_by("folder__path", "name")
        )
        flow_ids = [f.id for f in flows_qs]
        
        from django.db.models import F
        latest_flow_versions = {}
        if flow_ids:
            f_vers = FlowVersion.objects.filter(
                flow_id__in=flow_ids,
                version_number=F('flow__current_version')
            ).values('flow_id', 'steps_json')
            for fv in f_vers:
                latest_flow_versions[fv['flow_id']] = fv['steps_json']

        flows = []
        for f in flows_qs:
            flows.append({
                "id": f.id,
                "name": f.name,
                "description": f.description,
                "folder": f.folder.path if f.folder else None,
                "status": f.status,
                "current_version": f.current_version,
                "steps": latest_flow_versions.get(f.id, []),
            })

        # ── 6. TEST CASES ─────────────────────────────────────────────────
        test_cases_qs = (
            TestCase.objects
            .filter(project=project, status__in=[TestCase.STATUS_SAVED, TestCase.STATUS_DRAFT])
            .select_related("folder")
            .order_by("folder__path", "name")
        )
        tc_ids = [tc.id for tc in test_cases_qs]
        latest_tc_versions = {}
        if tc_ids:
            tc_vers = TestCaseVersion.objects.filter(
                test_case_id__in=tc_ids,
                version_number=F('test_case__current_version')
            ).values('test_case_id', 'pre_conditions_json', 'steps_json', 'expected_outcomes_json')
            for tv in tc_vers:
                latest_tc_versions[tv['test_case_id']] = tv

        test_cases = []
        for tc in test_cases_qs:
            tv = latest_tc_versions.get(tc.id, {})
            test_cases.append({
                "id": tc.id,
                "name": tc.name,
                "description": tc.description,
                "folder": tc.folder.path if tc.folder else None,
                "status": tc.status,
                "tags": tc.tags,
                "current_version": tc.current_version,
                "pre_conditions": tv.get("pre_conditions_json", []),
                "steps": tv.get("steps_json", []),
                "expected_outcomes": tv.get("expected_outcomes_json", []),
            })

        # ── 7. TEST SUITES ────────────────────────────────────────────────
        test_suites = []
        if user:
            ts_qs = (
                TestSuite.objects
                .filter(project=project, owner=user, status=TestSuite.STATUS_ACTIVE)
                .order_by("-created_at")
            )
            
            # Map test case IDs to types using TestCaseIdentity for this project
            # Ensure keys are integers for reliable lookup
            identities = TestCaseIdentity.objects.filter(project=project).values_list('id', 'type')
            id_to_type_map = {int(tc_id): tc_type for tc_id, tc_type in identities}
            
            for ts in ts_qs:
                enriched_ids = []
                # test_case_ids is a list from JSONField, could contain strings or ints
                raw_ids = ts.test_case_ids if isinstance(ts.test_case_ids, list) else []
                
                for tc_id in raw_ids:
                    try:
                        clean_id = int(tc_id)
                        # Fallback to GLOBAL if not found (for legacy data)
                        tc_type = id_to_type_map.get(clean_id, "GLOBAL")
                    except (ValueError, TypeError):
                        clean_id = tc_id
                        tc_type = "UNKNOWN"
                        
                    enriched_ids.append({"id": clean_id, "type": tc_type})
                
                test_suites.append({
                    "id": ts.id,
                    "name": ts.name,
                    "description": ts.description,
                    "tags": ts.tags,
                    "test_case_ids": enriched_ids,
                    "status": ts.status,
                    "created_at": ts.created_at.isoformat(),
                })

        # ── 8. LOCAL TEST CASES ───────────────────────────────────────────
        local_test_cases = []
        if user:
            ltc_qs = (
                LocalTestCase.objects
                .filter(project=project, owner=user, status__in=[LocalTestCase.STATUS_SAVED, LocalTestCase.STATUS_DRAFT])
                .select_related("folder")
                .order_by("folder__path", "-created_at")
            )
            ltc_ids = [ltc.id for ltc in ltc_qs]
            latest_ltc_versions = {}
            if ltc_ids:
                ltc_vers = LocalTestCaseVersion.objects.filter(
                    test_case_id__in=ltc_ids,
                    version_number=F('test_case__current_version')
                ).values('test_case_id', 'pre_conditions_json', 'steps_json', 'expected_outcomes_json')
                for ltv in ltc_vers:
                    latest_ltc_versions[ltv['test_case_id']] = ltv

            for ltc in ltc_qs:
                ltv = latest_ltc_versions.get(ltc.id, {})
                local_test_cases.append({
                    "id": ltc.id,
                    "name": ltc.name,
                    "description": ltc.description,
                    "folder": ltc.folder.path if ltc.folder else None,
                    "status": ltc.status,
                    "tags": ltc.tags,
                    "current_version": ltc.current_version,
                    "pre_conditions": ltv.get("pre_conditions_json", []),
                    "steps": ltv.get("steps_json", []),
                    "expected_outcomes": ltv.get("expected_outcomes_json", []),
                })

        # ── 9. EXECUTION BINDINGS ─────────────────────────────────────────
        bindings_qs = (
            ExecutionBinding.objects
            .filter(planning_item__project=project)
            .select_related(
                "planning_item",
                "planning_item__entity_type",
                "planning_item__status",
                "flow",
                "test_case",
            )
        )
        execution_bindings = [
            {
                "planning_item_id": b.planning_item.id,
                "planning_item_path": b.planning_item.path,
                "entity_type": b.planning_item.entity_type.display_name if b.planning_item.entity_type else None,
                "current_status": b.planning_item.status.name if b.planning_item.status else None,
                "bound_flow_id": b.flow_id,
                "bound_flow_name": b.flow.name if b.flow else None,
                "bound_test_case_id": b.test_case_id,
                "bound_test_case_name": b.test_case.name if b.test_case else None,
                "execution_mode": b.execution_mode,
                "auto_trigger": b.auto_trigger,
            }
            for b in bindings_qs
        ]

        return Response({
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "company": _serialize_company(project.company),
                "feature_flags": {
                    "flows_enabled": project.flows_enabled,
                    "test_cases_enabled": project.test_cases_enabled,
                    "builder_enabled": project.builder_enabled,
                    "execution_enabled": project.execution_enabled,
                    "reports_enabled": project.reports_enabled,
                    "element_capture_enabled": project.element_capture_enabled,
                    "test_planning_enabled": project.test_planning_enabled,
                },
            },
            "team": team,
            "action_registry": action_registry,
            "variables": variables,
            "elements": elements,
            "flows": flows,
            "test_cases": test_cases,
            "test_suites": test_suites,
            "local_test_cases": local_test_cases,
            "execution_bindings": execution_bindings,
        })
