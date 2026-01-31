from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.project_planning.models import (
    Element,
    ElementFolder,
)
from apps.project_planning.serializers.elements import (
    ElementSerializer,
)
from apps.project_planning.services.elements.elements import (
    create_element,
    update_element,
    delete_element,
)
from apps.project_planning.services.elements.locators import (
    create_locator,
)
from apps.common.api_responses import api_error


class CreateElementAPI(APIView):

    def post(self, request):
        folder_id = request.data.get("folder_id")
        name = request.data.get("name")
        page_url = request.data.get("page_url", "")
        locators = request.data.get("locators", [])

        folder = get_object_or_404(ElementFolder, id=folder_id)
        project = folder.project

        try:
            element = create_element(
                user=request.user,
                project=project,
                folder=folder,
                name=name,
                page_url=page_url,
            )

            for idx, locator in enumerate(locators):
                create_locator(
                    user=request.user,
                    element=element,
                    selector_type=locator.get("selector_type"),
                    selector_value=locator.get("selector_value"),
                    priority=idx,
                )

        except ValidationError as e:
            return api_error(
                code="ELEMENT_CONFLICT",
                message=str(e),
                status_code=409,
            )

        return Response(
            ElementSerializer(element).data,
            status=status.HTTP_201_CREATED,
        )


class ListElementsAPI(APIView):

    def get(self, request):
        project_id = request.query_params.get("project_id")
        folder_id = request.query_params.get("folder_id")

        if not project_id:
            return api_error(
                code="INVALID_PAYLOAD",
                message="project_id is required",
                status_code=400,
            )

        queryset = Element.objects.filter(
            project_id=project_id
        )

        # ---------------------------------
        # Optional folder filter
        # ---------------------------------
        if folder_id:
            folder = get_object_or_404(
                ElementFolder,
                id=folder_id,
                project_id=project_id,
            )

            queryset = queryset.filter(folder=folder)

        queryset = queryset.prefetch_related("locators")

        return Response(
            ElementSerializer(queryset, many=True).data
        )



class ElementDetailAPI(APIView):

    def get(self, request, element_id):
        element = get_object_or_404(Element, id=element_id)

        return Response(
            ElementSerializer(element).data
        )


class UpdateElementAPI(APIView):

    def patch(self, request, element_id):
        element = get_object_or_404(Element, id=element_id)

        try:
            element = update_element(
                user=request.user,
                element=element,
                name=request.data.get("name"),
                page_url=request.data.get("page_url"),
                locators_payload=request.data.get("locators"),
            )
        except ValidationError as e:
            return api_error(
                code="UPDATE_FAILED",
                message=str(e),
                status_code=400,
            )

        return Response(
            ElementSerializer(element).data
        )



class DeleteElementAPI(APIView):

    def delete(self, request, element_id):
        element = get_object_or_404(Element, id=element_id)

        delete_element(
            user=request.user,
            element=element,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
