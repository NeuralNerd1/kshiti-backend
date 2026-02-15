from django.urls import path
from apps.test_plan.views.template import (
    TemplateCreateView,
    TemplateListView,
    TemplateDetailView,
    TemplateUpdateView,
    TemplateDeleteView,
)

from apps.test_plan.views.template_actions import (
    TemplateSubmitView,
    TemplateAssignReviewerView,
    TemplateApproveView,
    TemplateRejectView,
    TemplateCreateFinalView,
)

from apps.test_plan.views.entity_type import (
    EntityTypeCreateView,
    EntityTypeListView,
    EntityTypeUpdateView,
    EntityTypeDeleteView,
)

from apps.test_plan.views.field_definition import (
    FieldDefinitionCreateView,
    FieldDefinitionUpdateView,
    FieldDefinitionDeleteView,
    FieldDefinitionListView,
)

from apps.test_plan.views.workflow import (
    WorkflowCreateView,
    WorkflowUpdateView,
    WorkflowDeleteView,
    WorkflowStateCreateView,
    WorkflowStateUpdateView,
    WorkflowStateDeleteView,
    WorkflowTransitionCreateView,
    WorkflowTransitionUpdateView,
    WorkflowTransitionDeleteView,
    WorkflowListView,
    WorkflowDetailView,
)

from apps.test_plan.views.time_tracking_rule import (
    TimeTrackingRuleCreateView,
    TimeTrackingRuleUpdateView,
    TimeTrackingRuleDeleteView,
)

from apps.test_plan.views.project_planning_config import (
    ProjectPlanningConfigDetailView,
    ProjectPlanningConfigUpdateView,
)

from apps.test_plan.views.template_activation import ActivateTemplateView
from apps.test_plan.views.kanban import KanbanBoardConfigView

from apps.test_plan.views.planning_item import (
    PlanningItemCreateView,
    PlanningItemListView,
    PlanningItemDetailView,
    PlanningItemUpdateView,
    PlanningItemDeleteView,
)

from apps.test_plan.views.workflow_transition import (
    PlanningItemTransitionView,
)

from apps.test_plan.views.dependency import (
    PlanningItemDependencyCreateView,
    PlanningDependencyDeleteView,
)

from apps.test_plan.views.time_tracking import (
    PlanningItemStartTimeView,
    PlanningItemStopTimeView,
    PlanningItemTimeSessionsView,
)

from apps.test_plan.views.execution_binding import (
    PlanningItemBindExecutionView,
    ExecutionBindingDeleteView,
)

from apps.test_plan.views.template_bootstrap import TemplateBootstrapView

from apps.test_plan.views.entity_schema import EntitySchemaView

from apps.test_plan.views.pending_reviews import PendingReviewsView

urlpatterns = [

    # ==========================================
    # TEMPLATE CRUD (PROJECT SCOPED)
    # ==========================================

    # POST  /projects/<project_id>/templates/
    path(
        "projects/<int:project_id>/templates/",
        TemplateCreateView.as_view(),
        name="template-create",
    ),

    # GET  /projects/<project_id>/templates/
    path(
        "projects/<int:project_id>/templates/list/",
        TemplateListView.as_view(),
        name="template-list",
    ),

    # GET  /projects/<project_id>/templates/<template_id>/
    path(
        "projects/<int:project_id>/templates/<int:template_id>/",
        TemplateDetailView.as_view(),
        name="template-detail",
    ),

    # PUT  /projects/<project_id>/templates/<template_id>/
    path(
        "projects/<int:project_id>/templates/<int:template_id>/update/",
        TemplateUpdateView.as_view(),
        name="template-update",
    ),

    # DELETE  /projects/<project_id>/templates/<template_id>/
    path(
        "projects/<int:project_id>/templates/<int:template_id>/delete/",
        TemplateDeleteView.as_view(),
        name="template-delete",
    ),

    path(
        "projects/<int:project_id>/templates/<int:template_id>/submit/",
        TemplateSubmitView.as_view(),
        name="template-submit",
    ),

    path(
        "projects/<int:project_id>/templates/<int:template_id>/assign-reviewer/",
        TemplateAssignReviewerView.as_view(),
        name="template-assign-reviewer",
    ),

    path(
        "projects/<int:project_id>/templates/<int:template_id>/approve/",
        TemplateApproveView.as_view(),
        name="template-approve",
    ),

    path(
        "projects/<int:project_id>/templates/<int:template_id>/reject/",
        TemplateRejectView.as_view(),
        name="template-reject",
    ),

    path(
        "projects/<int:project_id>/templates/<int:template_id>/create/",
        TemplateCreateFinalView.as_view(),
        name="template-create-final",
    ),

    path(
        "projects/<int:project_id>/templates/<int:template_id>/entity-types/",
        EntityTypeCreateView.as_view(),
        name="entity-type-create",
    ),

    path(
        "projects/<int:project_id>/templates/<int:template_id>/entity-types/list/",
        EntityTypeListView.as_view(),
        name="entity-type-list",
    ),

    path(
        "projects/<int:project_id>/entity-types/<int:entity_type_id>/update/",
        EntityTypeUpdateView.as_view(),
        name="entity-type-update",
    ),

    path(
        "projects/<int:project_id>/entity-types/<int:entity_type_id>/delete/",
        EntityTypeDeleteView.as_view(),
        name="entity-type-delete",
    ),

    path(
        "projects/<int:project_id>/entity-types/<int:entity_type_id>/fields/",
        FieldDefinitionCreateView.as_view(),
        name="field-create",
    ),

    path(
        "projects/<int:project_id>/fields/<int:field_id>/update/",
        FieldDefinitionUpdateView.as_view(),
        name="field-update",
    ),

    path(
        "projects/<int:project_id>/fields/<int:field_id>/delete/",
        FieldDefinitionDeleteView.as_view(),
        name="field-delete",
    ),

    path(
    "projects/<int:project_id>/entity-types/<int:entity_type_id>/fields/list/",
    FieldDefinitionListView.as_view(),
    name="field-list",
    ),
    path(
        "projects/<int:project_id>/entity-types/<int:entity_type_id>/workflow/",
        WorkflowCreateView.as_view(),
        name="workflow-create",
    ),
    path(
        "projects/<int:project_id>/workflow/<int:workflow_id>/update/",
        WorkflowUpdateView.as_view(),
        name="workflow-update",
    ),
    path(
        "projects/<int:project_id>/workflow/<int:workflow_id>/delete/",
        WorkflowDeleteView.as_view(),
        name="workflow-delete",
    ),

    # States
    path(
        "projects/<int:project_id>/workflow/<int:workflow_id>/states/",
        WorkflowStateCreateView.as_view(),
        name="workflow-state-create",
    ),
    path(
        "projects/<int:project_id>/states/<int:state_id>/update/",
        WorkflowStateUpdateView.as_view(),
        name="workflow-state-update",
    ),
    path(
        "projects/<int:project_id>/states/<int:state_id>/delete/",
        WorkflowStateDeleteView.as_view(),
        name="workflow-state-delete",
    ),

    # Transitions
    path(
        "projects/<int:project_id>/workflow/<int:workflow_id>/transitions/",
        WorkflowTransitionCreateView.as_view(),
        name="workflow-transition-create",
    ),
    path(
        "projects/<int:project_id>/transitions/<int:transition_id>/update/",
        WorkflowTransitionUpdateView.as_view(),
        name="workflow-transition-update",
    ),
    path(
        "projects/<int:project_id>/transitions/<int:transition_id>/delete/",
        WorkflowTransitionDeleteView.as_view(),
        name="workflow-transition-delete",
    ),

    path(
        "projects/<int:project_id>/entity-types/<int:entity_type_id>/time-rule/",
        TimeTrackingRuleCreateView.as_view(),
        name="time-rule-create",
    ),

    path(
        "projects/<int:project_id>/time-rule/<int:rule_id>/update/",
        TimeTrackingRuleUpdateView.as_view(),
        name="time-rule-update",
    ),

    path(
        "projects/<int:project_id>/time-rule/<int:rule_id>/delete/",
        TimeTrackingRuleDeleteView.as_view(),
        name="time-rule-delete",
    ),

    path(
        "projects/<int:project_id>/kanban-config/",
        KanbanBoardConfigView.as_view(),
        name="kanban-config",
    ),
    path(
        "projects/<int:project_id>/planning-config/",
        ProjectPlanningConfigDetailView.as_view(),
        name="planning-config-detail",
    ),

    path(
        "projects/<int:project_id>/planning-config/update/",
        ProjectPlanningConfigUpdateView.as_view(),
        name="planning-config-update",
    ),

    path(
        "projects/<int:project_id>/activate-template/<int:template_id>/",
        ActivateTemplateView.as_view(),
        name="activate-template",
    ),

    path(
        "projects/<int:project_id>/planning-items/",
        PlanningItemCreateView.as_view(),
        name="planning-item-create",
    ),

    path(
        "projects/<int:project_id>/planning-items/list/",
        PlanningItemListView.as_view(),
        name="planning-item-list",
    ),

    path(
        "planning-items/<int:item_id>/",
        PlanningItemDetailView.as_view(),
        name="planning-item-detail",
    ),

    path(
        "planning-items/<int:item_id>/update/",
        PlanningItemUpdateView.as_view(),
        name="planning-item-update",
    ),

    path(
        "planning-items/<int:item_id>/delete/",
        PlanningItemDeleteView.as_view(),
        name="planning-item-delete",
    ),

    path(
        "planning-items/<int:item_id>/transition/",
        PlanningItemTransitionView.as_view(),
        name="planning-item-transition",
    ),

    path(
        "planning-items/<int:item_id>/dependencies/",
        PlanningItemDependencyCreateView.as_view(),
        name="planning-item-dependency-create",
    ),

    path(
        "dependencies/<int:dependency_id>/delete/",
        PlanningDependencyDeleteView.as_view(),
        name="planning-dependency-delete",
    ),

    path(
        "planning-items/<int:item_id>/start-time/",
        PlanningItemStartTimeView.as_view(),
        name="planning-item-start-time",
    ),

    path(
        "planning-items/<int:item_id>/stop-time/",
        PlanningItemStopTimeView.as_view(),
        name="planning-item-stop-time",
    ),

    path(
        "planning-items/<int:item_id>/time-sessions/",
        PlanningItemTimeSessionsView.as_view(),
        name="planning-item-time-sessions",
    ),

    path(
        "planning-items/<int:item_id>/bind-execution/",
        PlanningItemBindExecutionView.as_view(),
        name="planning-item-bind-execution",
    ),

    path(
        "execution-binding/<int:binding_id>/delete/",
        ExecutionBindingDeleteView.as_view(),
        name="execution-binding-delete",
    ),

    path(
    "projects/<int:project_id>/templates/<int:template_id>/bootstrap-default/",
    TemplateBootstrapView.as_view(),
    ),

    path(
    "projects/<int:project_id>/entity-types/<int:entity_type_id>/schema/",
    EntitySchemaView.as_view(),
),

path(
    "projects/<int:project_id>/entity-types/<int:entity_type_id>/workflows/",
    WorkflowListView.as_view(),
),

path(
    "projects/<int:project_id>/workflows/<int:workflow_id>/",
    WorkflowDetailView.as_view(),
),

path(
    "projects/<int:project_id>/templates/pending-reviews/",
    PendingReviewsView.as_view(),
    name="template-pending-reviews",
),


]
