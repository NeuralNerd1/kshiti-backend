from django.core.exceptions import ValidationError
from apps.test_plan.models import ProcessTemplate
from apps.test_plan.services.template_versioning import clone_template_with_structure


def update_template(*, template, user, data):
    """
    Safe template update:
    - If template is CREATED → clone first.
    - If template is DRAFT/REJECTED → edit directly.
    """

    if template.status == ProcessTemplate.STATUS_CREATED:
        template = clone_template_with_structure(template=template, user=user)

    if template.is_locked:
        raise ValidationError("Locked template cannot be edited.")

    # Apply allowed updates only
    allowed_fields = ["name", "description"]
    for field in allowed_fields:
        if field in data:
            setattr(template, field, data[field])

    template.save()

    return template
