"""
Local Test Case Views — CRUD for user-private local test cases.
All queries are scoped to `request.user` (owner).
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.project_planning.models import (
    LocalTestCase,
    LocalTestCaseFolder,
    LocalTestCaseVersion,
    TestCaseIdentity,
)


# ═══════════════════════════════════════════════════════════
# LOCAL TEST CASE FOLDERS
# ═══════════════════════════════════════════════════════════

class ListLocalTestCaseFoldersAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_id = request.query_params.get("project_id")
        if not project_id:
            return Response({"error": "project_id required"}, status=400)

        folders = LocalTestCaseFolder.objects.filter(
            project_id=project_id,
            owner=request.user,
            status=LocalTestCaseFolder.STATUS_ACTIVE,
        ).values("id", "name", "path", "parent_id", "status", "created_at")
        return Response(list(folders))


class CreateLocalTestCaseFolderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        project_id = request.data.get("project_id")
        name = request.data.get("name", "")
        parent_id = request.data.get("parent") or request.data.get("parent_id")

        if not project_id or not name:
            return Response({"error": "project_id and name required"}, status=400)

        # Build path
        if parent_id:
            try:
                parent = LocalTestCaseFolder.objects.get(
                    id=parent_id, owner=request.user
                )
                path = f"{parent.path}/{name}"
            except LocalTestCaseFolder.DoesNotExist:
                return Response({"error": "Parent folder not found"}, status=404)
        else:
            path = name

        folder = LocalTestCaseFolder.objects.create(
            project_id=project_id,
            owner=request.user,
            name=name,
            path=path,
            parent_id=parent_id,
        )
        return Response({
            "id": folder.id,
            "name": folder.name,
            "path": folder.path,
            "parent": folder.parent_id,
            "status": folder.status,
            "created_at": folder.created_at.isoformat(),
        }, status=201)


class UpdateLocalTestCaseFolderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, folder_id):
        try:
            folder = LocalTestCaseFolder.objects.get(
                id=folder_id, owner=request.user
            )
        except LocalTestCaseFolder.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        if "name" in request.data:
            folder.name = request.data["name"]
            # Rebuild path
            if folder.parent:
                folder.path = f"{folder.parent.path}/{folder.name}"
            else:
                folder.path = folder.name

        folder.save()
        return Response({
            "id": folder.id,
            "name": folder.name,
            "path": folder.path,
            "parent": folder.parent_id,
            "status": folder.status,
            "created_at": folder.created_at.isoformat(),
        })

    def delete(self, request, folder_id):
        try:
            folder = LocalTestCaseFolder.objects.get(
                id=folder_id, owner=request.user
            )
        except LocalTestCaseFolder.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        folder.delete()
        return Response(status=204)


# ═══════════════════════════════════════════════════════════
# LOCAL TEST CASES
# ═══════════════════════════════════════════════════════════

class CreateLocalTestCaseAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        folder_id = request.data.get("folder_id")
        name = request.data.get("name", "")
        description = request.data.get("description", "")
        tags = request.data.get("tags", [])

        if not folder_id or not name:
            return Response({"error": "folder_id and name required"}, status=400)

        try:
            folder = LocalTestCaseFolder.objects.get(
                id=folder_id, owner=request.user
            )
        except LocalTestCaseFolder.DoesNotExist:
            return Response({"error": "Folder not found"}, status=404)

        project = folder.project
        try:
            # Generate unified ID
            test_case_id = TestCaseIdentity.get_next_id(
                project, TestCaseIdentity.TYPE_LOCAL
            )

            tc = LocalTestCase.objects.create(
                id=test_case_id,
                project=project,
                owner=request.user,
                folder=folder,
                name=name,
                description=description,
                tags=tags,
                status=LocalTestCase.STATUS_DRAFT,
                current_version=1,
            )

        except Exception as e:
            return Response({"error": f"Failed to create test case: {e}"}, status=500)

        # 🔥 Auto-create local version 1 (to mirror global pattern)
        LocalTestCaseVersion.objects.create(
            test_case=tc,
            version_number=1,
            pre_conditions_json=[],
            steps_json=[],
            expected_outcomes_json=[],
            created_from_version=None,
        )

        return Response({
            "id": tc.id,
            "name": tc.name,
            "description": tc.description,
            "status": tc.status,
            "folder": tc.folder_id,
            "tags": tc.tags,
            "current_version": tc.current_version,
            "created_at": tc.created_at.isoformat(),
            "updated_at": tc.updated_at.isoformat(),
        }, status=201)


class ListLocalTestCasesAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_id = request.query_params.get("project_id")
        status_filter = request.query_params.get("status", "ALL")
        
        if not project_id:
            return Response({"error": "project_id required"}, status=400)

        test_cases = LocalTestCase.objects.filter(
            project_id=project_id,
            owner=request.user,
        )

        if status_filter != "ALL":
            test_cases = test_cases.filter(status=status_filter)

        test_cases = test_cases.values(
            "id", "name", "description", "status",
            "folder_id", "tags", "current_version",
            "created_at", "updated_at",
        )

        # Rename folder_id → folder for frontend compatibility
        result = []
        for tc in test_cases:
            tc["folder"] = tc.pop("folder_id")
            result.append(tc)

        return Response(result)


class LocalTestCaseDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, test_case_id):
        try:
            tc = LocalTestCase.objects.select_related("folder").get(
                id=test_case_id, owner=request.user
            )
        except LocalTestCase.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        versions = list(
            tc.versions.order_by("-version_number").values(
                "version_number",
                "pre_conditions_json",
                "steps_json",
                "expected_outcomes_json",
                "created_from_version",
                "created_at",
            )
        )

        return Response({
            "test_case": {
                "id": tc.id,
                "name": tc.name,
                "description": tc.description,
                "status": tc.status,
                "folder": tc.folder_id,
                "tags": tc.tags,
                "current_version": tc.current_version,
                "created_at": tc.created_at.isoformat(),
                "updated_at": tc.updated_at.isoformat(),
            },
            "folder": {
                "id": tc.folder.id,
                "name": tc.folder.name,
                "path": tc.folder.path,
                "parent": tc.folder.parent_id,
            },
            "versions": versions,
        })

    def put(self, request, test_case_id):
        try:
            tc = LocalTestCase.objects.get(
                id=test_case_id, owner=request.user
            )
        except LocalTestCase.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        if "name" in request.data:
            tc.name = request.data["name"]
        if "description" in request.data:
            tc.description = request.data["description"]

        tc.save()
        return Response({
            "id": tc.id,
            "name": tc.name,
            "description": tc.description,
            "status": tc.status,
            "folder": tc.folder_id,
            "tags": tc.tags,
            "current_version": tc.current_version,
            "created_at": tc.created_at.isoformat(),
            "updated_at": tc.updated_at.isoformat(),
        })


class ArchiveLocalTestCaseAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, test_case_id):
        try:
            tc = LocalTestCase.objects.get(
                id=test_case_id, owner=request.user
            )
        except LocalTestCase.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        tc.archive()
        return Response({"status": "archived"})


# ═══════════════════════════════════════════════════════════
# LOCAL TEST CASE BUILDER
# ═══════════════════════════════════════════════════════════

class SaveLocalTestCaseBuilderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, test_case_id):
        try:
            tc = LocalTestCase.objects.get(
                id=test_case_id, owner=request.user
            )
        except LocalTestCase.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        section = request.data.get("section")
        steps = request.data.get("steps", [])

        valid_sections = ["pre_conditions", "steps", "expected_outcomes"]
        if section not in valid_sections:
            return Response(
                {"error": f"section must be one of {valid_sections}"},
                status=400,
            )

        # Get or create version
        next_version = (tc.current_version or 0) + 1
        latest = tc.versions.order_by("-version_number").first()

        version_data = {
            "pre_conditions_json": latest.pre_conditions_json if latest else [],
            "steps_json": latest.steps_json if latest else [],
            "expected_outcomes_json": latest.expected_outcomes_json if latest else [],
        }

        # Map section name to JSON field
        section_field_map = {
            "pre_conditions": "pre_conditions_json",
            "steps": "steps_json",
            "expected_outcomes": "expected_outcomes_json",
        }
        version_data[section_field_map[section]] = steps

        LocalTestCaseVersion.objects.create(
            test_case=tc,
            version_number=next_version,
            created_from_version=tc.current_version,
            **version_data,
        )

        tc.current_version = next_version
        if next_version >= 1:
            tc.status = LocalTestCase.STATUS_SAVED
        tc.save(update_fields=["current_version", "status", "updated_at"])

        return Response({"version": next_version}, status=201)
