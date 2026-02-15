from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.company_operations.models import Project
from apps.company_operations.services.project_users import get_project_user
from apps.test_plan.services.guards import ensure_test_planning_enabled

from apps.test_plan.models import PlanningItem
from apps.test_plan.serializers.planning_item import PlanningItemSerializer
from apps.test_plan.services.planning_item_service import (
    create_planning_item,
    update_planning_item,
)

class PlanningItemCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)

        get_project_user(project, request.user)

        serializer = PlanningItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = create_planning_item(
            project=project,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response({"id": item.id}, status=status.HTTP_201_CREATED)

class PlanningItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)

        get_project_user(project, request.user)

        items = PlanningItem.objects.filter(project=project)\
            .select_related("entity_type", "status", "owner")\
            .prefetch_related("assigned_users")

        return Response(
            PlanningItemSerializer(items, many=True).data
        )

class PlanningItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, item_id):

        item = get_object_or_404(
            PlanningItem.objects.select_related("project"),
            id=item_id
        )

        ensure_test_planning_enabled(item.project)
        get_project_user(item.project, request.user)

        return Response(
            PlanningItemSerializer(item).data
        )

class PlanningItemUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, item_id):

        item = get_object_or_404(
            PlanningItem.objects.select_related("project"),
            id=item_id
        )

        ensure_test_planning_enabled(item.project)
        get_project_user(item.project, request.user)

        serializer = PlanningItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = update_planning_item(
            item=item,
            data=serializer.validated_data,
        )

        return Response({"id": item.id})

class PlanningItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):

        item = get_object_or_404(
            PlanningItem.objects.select_related("project"),
            id=item_id
        )

        ensure_test_planning_enabled(item.project)
        get_project_user(item.project, request.user)

        item.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

