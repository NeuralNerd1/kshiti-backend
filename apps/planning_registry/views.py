# apps/planning_registry/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services import get_action_registry
from .models import ActionCategory
from .serializers import ActionCategorySerializer


class ActionRegistryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = ActionCategory.objects.prefetch_related(
            "actions"
        ).all()

        serializer = ActionCategorySerializer(categories, many=True)
        return Response(serializer.data)
    

