from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.project_planning.models import Variable, VariableFolder
from apps.project_planning.serializers.variables import VariableSerializer
from apps.project_planning.services.variables.variables import (
    create_variable,
    update_variable,
    delete_variable,
)
from apps.common.api_responses import api_error
from rest_framework.exceptions import ValidationError


class CreateVariableAPI(APIView):

    def post(self, request):
        folder_id = request.data.get("folder_id")
        key = request.data.get("key")
        value = request.data.get("value")
        description = request.data.get("description", "")

        folder = get_object_or_404(VariableFolder, id=folder_id)

        try:
            variable = create_variable(
                user=request.user,
                project=folder.project,
                folder=folder,
                key=key,
                value=value,
                description=description,
            )
        except ValidationError as e:
            return api_error(
                code="VARIABLE_CONFLICT",
                message=str(e),
                status_code=409,
            )

        return Response(
            VariableSerializer(variable).data,
            status=201,
        )


class ListVariablesAPI(APIView):

    def get(self, request):
        project_id = request.query_params.get("project_id")
        folder_id = request.query_params.get("folder_id")

        if not project_id:
            return api_error(
                code="PROJECT_ID_REQUIRED",
                message="project_id is required",
                status_code=400,
            )

        variables = Variable.objects.filter(
            project_id=project_id
        )

        # ✅ FIX: apply folder filtering
        if folder_id:
            variables = variables.filter(
                folder_id=folder_id
            )

        variables = variables.select_related("folder")

        return Response(
            VariableSerializer(variables, many=True).data
        )



class UpdateVariableAPI(APIView):

    def patch(self, request, variable_id):
        variable = get_object_or_404(Variable, id=variable_id)

        try:
            variable = update_variable(
                user=request.user,
                variable=variable,
                value=request.data.get("value"),
                description=request.data.get("description"),
            )
        except ValidationError as e:
            return api_error(
                code="UPDATE_FAILED",
                message=str(e),
                status_code=400,
            )

        return Response(
            VariableSerializer(variable).data
        )


class DeleteVariableAPI(APIView):

    def delete(self, request, variable_id):
        variable = get_object_or_404(Variable, id=variable_id)

        delete_variable(
            user=request.user,
            variable=variable,
        )

        return Response(status=204)
