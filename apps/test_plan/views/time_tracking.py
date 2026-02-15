from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.test_plan.models import PlanningItem
from apps.test_plan.services.time_tracking_service import (
    start_time_tracking,
    stop_time_tracking,
    list_time_sessions,
)
from apps.test_plan.serializers.time_tracking_session import (
    TimeTrackingSessionSerializer,
)

class PlanningItemStartTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):

        item = get_object_or_404(PlanningItem, id=item_id)

        session = start_time_tracking(
            item=item,
            user=request.user,
        )

        return Response(
            TimeTrackingSessionSerializer(session).data,
            status=status.HTTP_201_CREATED,
        )

class PlanningItemStopTimeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):

        item = get_object_or_404(PlanningItem, id=item_id)

        session = stop_time_tracking(
            item=item,
            user=request.user,
        )

        return Response(
            TimeTrackingSessionSerializer(session).data,
            status=status.HTTP_200_OK,
        )

class PlanningItemTimeSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, item_id):

        item = get_object_or_404(PlanningItem, id=item_id)

        sessions = list_time_sessions(
            item=item,
            user=request.user,
        )

        return Response(
            TimeTrackingSessionSerializer(sessions, many=True).data
        )

