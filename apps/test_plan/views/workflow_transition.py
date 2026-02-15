from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.test_plan.models import PlanningItem
from apps.test_plan.serializers.workflow_transition import (
    WorkflowTransitionRequestSerializer,
)
from apps.test_plan.serializers.planning_item import PlanningItemSerializer
from apps.test_plan.services.workflow_transition_engine import (
    transition_planning_item,
)

class PlanningItemTransitionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):

        item = get_object_or_404(
            PlanningItem.objects.select_related(
                "entity_type",
                "status",
                "project",
            ),
            id=item_id,
        )

        serializer = WorkflowTransitionRequestSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        item = transition_planning_item(
            item=item,
            user=request.user,
            target_state_id=serializer.validated_data["target_state_id"],
        )

        return Response(
            PlanningItemSerializer(item).data,
            status=status.HTTP_200_OK,
        )

