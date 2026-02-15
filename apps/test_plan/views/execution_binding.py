from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.test_plan.models import PlanningItem, ExecutionBinding
from apps.project_planning.models import Flow, TestCase

from apps.test_plan.services.execution_binding_service import (
    bind_execution,
    delete_execution_binding,
)

from apps.test_plan.serializers.execution_binding import (
    ExecutionBindingCreateSerializer,
    ExecutionBindingSerializer,
)

class PlanningItemBindExecutionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):

        item = get_object_or_404(PlanningItem, id=item_id)

        serializer = ExecutionBindingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        flow = None
        test_case = None

        if serializer.validated_data.get("flow_id"):
            flow = get_object_or_404(
                Flow,
                id=serializer.validated_data["flow_id"],
            )

        if serializer.validated_data.get("test_case_id"):
            test_case = get_object_or_404(
                TestCase,
                id=serializer.validated_data["test_case_id"],
            )

        binding = bind_execution(
            item=item,
            user=request.user,
            flow=flow,
            test_case=test_case,
            execution_mode=serializer.validated_data.get("execution_mode"),
            auto_trigger=serializer.validated_data.get("auto_trigger", False),
        )

        return Response(
            ExecutionBindingSerializer(binding).data,
            status=status.HTTP_200_OK,
        )

class ExecutionBindingDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, binding_id):

        binding = get_object_or_404(
            ExecutionBinding,
            id=binding_id,
        )

        delete_execution_binding(
            binding=binding,
            user=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

