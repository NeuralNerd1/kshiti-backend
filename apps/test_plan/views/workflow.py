from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.company_operations.models import Project
from apps.company_operations.services.project_users import get_project_user
from apps.test_plan.services.guards import ensure_test_planning_enabled

from apps.test_plan.models import (
    PlanningEntityType,
    WorkflowDefinition,
    WorkflowState,
    WorkflowTransition,
)

from apps.test_plan.serializers.workflow import (
    WorkflowSerializer,
    WorkflowStateSerializer,
    WorkflowTransitionSerializer,
)

from apps.test_plan.services.workflow_service import (
    create_workflow,
    update_workflow,
    delete_workflow,
    create_state,
    update_state,
    delete_state,
    create_transition,
    update_transition,
    delete_transition,
)

class WorkflowCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id, entity_type_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        entity_type = get_object_or_404(
            PlanningEntityType.objects.select_related("template"),
            id=entity_type_id,
            template__company=project.company,
        )

        workflow = create_workflow(
            project=project,
            entity_type=entity_type,
            user=request.user,
        )

        return Response(
            WorkflowSerializer(workflow).data,
            status=status.HTTP_201_CREATED,
        )

class WorkflowUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, project_id, workflow_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        workflow = get_object_or_404(
            WorkflowDefinition.objects.select_related("entity_type__template"),
            id=workflow_id,
            entity_type__template__company=project.company,
        )

        serializer = WorkflowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workflow = update_workflow(
            project=project,
            workflow=workflow,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(WorkflowSerializer(workflow).data)

class WorkflowDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, project_id, workflow_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        workflow = get_object_or_404(
            WorkflowDefinition.objects.select_related("entity_type__template"),
            id=workflow_id,
            entity_type__template__company=project.company,
        )

        delete_workflow(
            project=project,
            workflow=workflow,
            user=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

class WorkflowStateCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id, workflow_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        workflow = get_object_or_404(
            WorkflowDefinition.objects.select_related("entity_type__template"),
            id=workflow_id,
            entity_type__template__company=project.company,
        )

        serializer = WorkflowStateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        state = create_state(
            project=project,
            workflow=workflow,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(
            WorkflowStateSerializer(state).data,
            status=status.HTTP_201_CREATED,
        )

class WorkflowStateUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, project_id, state_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        state = get_object_or_404(
            WorkflowState.objects.select_related("workflow__entity_type__template"),
            id=state_id,
            workflow__entity_type__template__company=project.company,
        )

        serializer = WorkflowStateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        state = update_state(
            project=project,
            state=state,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(WorkflowStateSerializer(state).data)

class WorkflowStateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, project_id, state_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        state = get_object_or_404(
            WorkflowState.objects.select_related("workflow__entity_type__template"),
            id=state_id,
            workflow__entity_type__template__company=project.company,
        )

        delete_state(
            project=project,
            state=state,
            user=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

class WorkflowTransitionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id, workflow_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        workflow = get_object_or_404(
            WorkflowDefinition.objects.select_related("entity_type__template"),
            id=workflow_id,
            entity_type__template__company=project.company,
        )

        serializer = WorkflowTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transition = create_transition(
            project=project,
            workflow=workflow,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(
            WorkflowTransitionSerializer(transition).data,
            status=status.HTTP_201_CREATED,
        )

class WorkflowTransitionUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, project_id, transition_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        transition = get_object_or_404(
            WorkflowTransition.objects.select_related("workflow__entity_type__template"),
            id=transition_id,
            workflow__entity_type__template__company=project.company,
        )

        serializer = WorkflowTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transition = update_transition(
            project=project,
            transition=transition,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(
            WorkflowTransitionSerializer(transition).data
        )

class WorkflowTransitionDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, project_id, transition_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        transition = get_object_or_404(
            WorkflowTransition.objects.select_related("workflow__entity_type__template"),
            id=transition_id,
            workflow__entity_type__template__company=project.company,
        )

        delete_transition(
            project=project,
            transition=transition,
            user=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
class WorkflowListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, entity_type_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        entity_type = get_object_or_404(
            PlanningEntityType.objects.select_related("template"),
            id=entity_type_id,
            template__company=project.company,
        )

        workflows = WorkflowDefinition.objects.filter(
            entity_type=entity_type
        )

        return Response(
            WorkflowSerializer(workflows, many=True).data
        )

class WorkflowDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, workflow_id):

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        workflow = get_object_or_404(
            WorkflowDefinition.objects.select_related("entity_type__template"),
            id=workflow_id,
            entity_type__template__company=project.company,
        )

        states = WorkflowState.objects.filter(workflow=workflow)
        transitions = WorkflowTransition.objects.filter(workflow=workflow)

        return Response({
            "workflow": WorkflowSerializer(workflow).data,
            "states": WorkflowStateSerializer(states, many=True).data,
            "transitions": WorkflowTransitionSerializer(transitions, many=True).data,
        })
