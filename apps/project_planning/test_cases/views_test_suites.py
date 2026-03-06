"""
Test Suite Views — CRUD for user-private test suites.
All queries are scoped to `request.user` (owner).
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.project_planning.models import TestSuite


class ListCreateTestSuiteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_id = request.query_params.get("project_id")
        if not project_id:
            return Response({"error": "project_id required"}, status=400)

        suites = TestSuite.objects.filter(
            project_id=project_id,
            owner=request.user,
        ).values(
            "id", "project_id", "name", "description", "tags",
            "test_case_ids", "status", "created_at", "updated_at",
        )
        return Response(list(suites))

    def post(self, request):
        project_id = request.data.get("project_id")
        if not project_id:
            return Response({"error": "project_id required"}, status=400)

        suite = TestSuite.objects.create(
            project_id=project_id,
            owner=request.user,
            name=request.data.get("name", ""),
            description=request.data.get("description", ""),
            tags=request.data.get("tags", []),
            test_case_ids=request.data.get("test_case_ids", []),
        )
        return Response({
            "id": suite.id,
            "name": suite.name,
            "description": suite.description,
            "tags": suite.tags,
            "test_case_ids": suite.test_case_ids,
            "status": suite.status,
            "created_at": suite.created_at.isoformat(),
            "updated_at": suite.updated_at.isoformat(),
        }, status=201)


class TestSuiteDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, suite_id):
        try:
            suite = TestSuite.objects.get(id=suite_id, owner=request.user)
        except TestSuite.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        return Response({
            "id": suite.id,
            "name": suite.name,
            "description": suite.description,
            "tags": suite.tags,
            "test_case_ids": suite.test_case_ids,
            "status": suite.status,
            "created_at": suite.created_at.isoformat(),
            "updated_at": suite.updated_at.isoformat(),
        })

    def put(self, request, suite_id):
        try:
            suite = TestSuite.objects.get(id=suite_id, owner=request.user)
        except TestSuite.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        if "name" in request.data:
            suite.name = request.data["name"]
        if "description" in request.data:
            suite.description = request.data["description"]
        if "tags" in request.data:
            suite.tags = request.data["tags"]
        if "test_case_ids" in request.data:
            suite.test_case_ids = request.data["test_case_ids"]

        suite.save()

        return Response({
            "id": suite.id,
            "name": suite.name,
            "description": suite.description,
            "tags": suite.tags,
            "test_case_ids": suite.test_case_ids,
            "status": suite.status,
            "created_at": suite.created_at.isoformat(),
            "updated_at": suite.updated_at.isoformat(),
        })

    def delete(self, request, suite_id):
        try:
            suite = TestSuite.objects.get(id=suite_id, owner=request.user)
        except TestSuite.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        suite.delete()
        return Response(status=204)
