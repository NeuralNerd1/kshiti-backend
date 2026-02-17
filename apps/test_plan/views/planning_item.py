from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.company_operations.models import Project
from apps.test_plan.models import PlanningItem
from apps.test_plan.serializers.planning_item import (
    PlanningItemSerializer,
    PlanningItemCreateSerializer,
)

from apps.test_plan.services.planning_item_service import (
    create_planning_item,
    update_planning_item,
    delete_planning_item,
)

class PlanningItemCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):

        project = get_object_or_404(Project, id=project_id)

        serializer = PlanningItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = create_planning_item(
            project=project,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(
            PlanningItemSerializer(item).data,
            status=status.HTTP_201_CREATED,
        )

class PlanningItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):

        project = get_object_or_404(Project, id=project_id)

        items = PlanningItem.objects.filter(project=project)

        return Response(
            PlanningItemSerializer(items, many=True).data
        )

class PlanningItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, item_id):

        item = get_object_or_404(PlanningItem, id=item_id)

        return Response(
            PlanningItemSerializer(item).data
        )
    
class PlanningItemUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, item_id):

        item = get_object_or_404(PlanningItem, id=item_id)

        serializer = PlanningItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item = update_planning_item(
            project=item.project,
            item=item,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(
            PlanningItemSerializer(item).data
        )


class PlanningItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):

        item = get_object_or_404(PlanningItem, id=item_id)

        delete_planning_item(
            project=item.project,
            item=item,
            user=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)



