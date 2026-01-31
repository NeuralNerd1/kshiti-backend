from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.project_planning.models import ElementLocator
from apps.project_planning.serializers.elements import (
    ElementLocatorSerializer,
)
from apps.project_planning.services.elements.locators import (
    update_locator,
    delete_locator,
)
from apps.common.api_responses import api_error
from rest_framework.exceptions import ValidationError


class UpdateLocatorAPI(APIView):

    def patch(self, request, locator_id):
        locator = get_object_or_404(ElementLocator, id=locator_id)

        try:
            locator = update_locator(
                user=request.user,
                locator=locator,
                **request.data,
            )
        except ValidationError as e:
            return api_error(
                code="UPDATE_FAILED",
                message=str(e),
                status_code=400,
            )

        return Response(
            ElementLocatorSerializer(locator).data
        )


class DeleteLocatorAPI(APIView):

    def delete(self, request, locator_id):
        locator = get_object_or_404(ElementLocator, id=locator_id)

        delete_locator(
            user=request.user,
            locator=locator,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
