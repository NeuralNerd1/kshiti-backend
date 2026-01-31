from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.project_planning.models import Flow, FlowVersion
from apps.planning_registry.models import ActionDefinition
from ._guards import ensure_flows_enabled, ensure_can_edit_flows


def _validate_steps_against_registry(steps):
    """
    Validate action_key existence only.
    No parameter completeness checks.
    """

    action_keys = {step["action_key"] for step in steps}

    existing = set(
        ActionDefinition.objects.filter(
            action_key__in=action_keys
        ).values_list("action_key", flat=True)
    )

    missing = action_keys - existing
    if missing:
        raise ValidationError(
            f"Invalid action_key(s): {', '.join(missing)}"
        )


@transaction.atomic
def save_flow_version(*, user, flow, steps_json, created_from_version=None):
    """
    Create a new immutable FlowVersion.
    """

    ensure_flows_enabled(flow.project)
    ensure_can_edit_flows(user, flow.project)

    if flow.status == Flow.STATUS_ARCHIVED:
        raise ValidationError("Cannot modify archived flow")

    _validate_steps_against_registry(steps_json)

    next_version = flow.current_version + 1

    version = FlowVersion.objects.create(
        flow=flow,
        version_number=next_version,
        steps_json=steps_json,
        created_from_version = (
    created_from_version
    if created_from_version is not None
    else flow.current_version
)
    )

    flow.current_version = next_version
    flow.status = Flow.STATUS_SAVED
    flow.save(update_fields=["current_version", "status"])

    return version

@transaction.atomic
def rollback_flow_version(*, user, flow, source_version_number):
    """
    Roll back by copying an old version into a new one.
    """

    ensure_flows_enabled(flow.project)
    ensure_can_edit_flows(user, flow.project)

    try:
        source = flow.versions.get(
            version_number=source_version_number
        )
    except FlowVersion.DoesNotExist:
        raise ValidationError("Source version not found")

    return save_flow_version(
        user=user,
        flow=flow,
        steps_json=source.steps_json,
        created_from_version=source.version_number,
    )

