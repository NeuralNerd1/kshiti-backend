from django.db import transaction
from django.core.exceptions import ValidationError

from apps.test_plan.models import (
    ProcessTemplate,
    PlanningEntityType,
    EntityFieldDefinition,
    WorkflowDefinition,
    WorkflowState,
    WorkflowTransition,
    TimeTrackingRule,
)


@transaction.atomic
def clone_template_with_structure(*, template, user):
    """
    Deep clone template and all nested structure.
    Only allowed if template is CREATED and locked.
    """

    if template.status != ProcessTemplate.STATUS_CREATED:
        raise ValidationError("Only CREATED templates can be versioned.")

    if not template.is_locked:
        raise ValidationError("Template must be locked before cloning.")

    old_template_id = template.id

    # Clone template base
    template.pk = None
    template.version_number += 1
    template.status = ProcessTemplate.STATUS_DRAFT
    template.is_locked = False
    template.created_by = user.company_membership
    template.reviewer = None
    template.rejection_note = None
    template.save()

    new_template = template

    # Clone entity types
    old_entities = PlanningEntityType.objects.filter(template_id=old_template_id)
    entity_mapping = {}

    for entity in old_entities:
        old_entity_id = entity.id
        entity.pk = None
        entity.template = new_template
        entity.workflow = None  # will reassign later
        entity.save()
        entity_mapping[old_entity_id] = entity

    # Clone fields
    for old_entity_id, new_entity in entity_mapping.items():
        fields = EntityFieldDefinition.objects.filter(entity_type_id=old_entity_id)
        for field in fields:
            field.pk = None
            field.entity_type = new_entity
            field.save()

    # Clone workflows
    for old_entity_id, new_entity in entity_mapping.items():
        try:
            old_workflow = WorkflowDefinition.objects.get(entity_type_id=old_entity_id)
        except WorkflowDefinition.DoesNotExist:
            continue

        old_workflow_id = old_workflow.id

        old_workflow.pk = None
        old_workflow.entity_type = new_entity
        old_workflow.initial_state = None
        old_workflow.save()

        new_workflow = old_workflow
        new_entity.workflow = new_workflow
        new_entity.save(update_fields=["workflow"])

        state_mapping = {}

        # Clone states
        states = WorkflowState.objects.filter(workflow_id=old_workflow_id)
        for state in states:
            old_state_id = state.id
            state.pk = None
            state.workflow = new_workflow
            state.save()
            state_mapping[old_state_id] = state

        # Reassign initial state
        original_workflow = WorkflowDefinition.objects.get(id=old_workflow_id)
        if original_workflow.initial_state_id:
            new_workflow.initial_state = state_mapping.get(original_workflow.initial_state_id)
            new_workflow.save(update_fields=["initial_state"])

        # Clone transitions
        transitions = WorkflowTransition.objects.filter(workflow_id=old_workflow_id)
        for transition in transitions:
            transition.pk = None
            transition.workflow = new_workflow
            transition.from_state = state_mapping[transition.from_state_id]
            transition.to_state = state_mapping[transition.to_state_id]
            transition.save()

    # Clone time tracking rules
    for old_entity_id, new_entity in entity_mapping.items():
        try:
            old_rule = TimeTrackingRule.objects.get(entity_type_id=old_entity_id)
        except TimeTrackingRule.DoesNotExist:
            continue

        old_rule.pk = None
        old_rule.entity_type = new_entity
        old_rule.save()

    return new_template
