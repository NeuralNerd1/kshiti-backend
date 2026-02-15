from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.test_plan.models import PlanningItem, PlanningDependency
from apps.test_plan.serializers.dependency import (
    DependencyCreateSerializer,
    DependencySerializer,
)
from apps.test_plan.services.dependency_service import (
    create_dependency,
    delete_dependency,
)

class PlanningItemDependencyCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):

        source_item = get_object_or_404(PlanningItem, id=item_id)

        serializer = DependencyCreateSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        target_item = get_object_or_404(
            PlanningItem,
            id=serializer.validated_data["target_item_id"],
        )

        dependency = create_dependency(
            source_item=source_item,
            target_item=target_item,
            dependency_type=serializer.validated_data["dependency_type"],
            user=request.user,
        )

        return Response(
            DependencySerializer(dependency).data,
            status=status.HTTP_201_CREATED,
        )

class PlanningDependencyDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, dependency_id):

        dependency = get_object_or_404(
            PlanningDependency,
            id=dependency_id,
        )

        delete_dependency(
            dependency=dependency,
            user=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
