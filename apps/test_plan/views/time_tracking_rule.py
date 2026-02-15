from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.company_operations.models import Project
from apps.company_operations.services.project_users import get_project_user
from apps.test_plan.services.guards import ensure_test_planning_enabled

from apps.test_plan.models import PlanningEntityType, TimeTrackingRule
from apps.test_plan.serializers.time_tracking_rule import TimeTrackingRuleSerializer


class TimeTrackingRuleCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id, entity_type_id):

        # 🔥 Lazy import to break circular dependency
        from apps.test_plan.services.time_tracking_rule_service import create_time_rule

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        entity_type = get_object_or_404(
            PlanningEntityType.objects.select_related("template"),
            id=entity_type_id,
            template__company=project.company,
        )

        serializer = TimeTrackingRuleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rule = create_time_rule(
            project=project,
            entity_type=entity_type,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(
            TimeTrackingRuleSerializer(rule).data,
            status=status.HTTP_201_CREATED,
        )


class TimeTrackingRuleUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, project_id, rule_id):

        # 🔥 Lazy import to break circular dependency
        from apps.test_plan.services.time_tracking_rule_service import update_time_rule

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        rule = get_object_or_404(
            TimeTrackingRule.objects.select_related("entity_type__template"),
            id=rule_id,
            entity_type__template__company=project.company,
        )

        serializer = TimeTrackingRuleSerializer(rule, data=request.data)
        serializer.is_valid(raise_exception=True)

        rule = update_time_rule(
            project=project,
            rule=rule,
            user=request.user,
            data=serializer.validated_data,
        )

        return Response(TimeTrackingRuleSerializer(rule).data)


class TimeTrackingRuleDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, project_id, rule_id):

        # 🔥 Lazy import to break circular dependency
        from apps.test_plan.services.time_tracking_rule_service import delete_time_rule

        project = get_object_or_404(Project, id=project_id)
        ensure_test_planning_enabled(project)
        get_project_user(project, request.user)

        rule = get_object_or_404(
            TimeTrackingRule.objects.select_related("entity_type__template"),
            id=rule_id,
            entity_type__template__company=project.company,
        )

        delete_time_rule(
            project=project,
            rule=rule,
            user=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
