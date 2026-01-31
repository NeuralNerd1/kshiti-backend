# apps/planning_registry/services.py

from .models import ActionCategory
from django.core.cache import cache


ACTION_REGISTRY_CACHE_KEY = "action_registry_v1"
CACHE_TTL = 60 * 60  # 1 hour


def get_action_registry():
    """
    Returns the full action registry grouped by category.
    Safe to cache.
    """
    cached = cache.get(ACTION_REGISTRY_CACHE_KEY)
    if cached:
        return cached

    data = []

    categories = ActionCategory.objects.prefetch_related("actions").all()

    for category in categories:
        data.append(
            {
                "category_key": category.key,
                "category_name": category.name,
                "actions": [
                    {
                        "action_key": action.action_key,
                        "action_name": action.action_name,
                        "description": action.description,
                        "is_risky": action.is_risky,
                        "parameter_schema": action.parameter_schema,
                    }
                    for action in category.actions.all()
                ],
            }
        )

    cache.set(ACTION_REGISTRY_CACHE_KEY, data, CACHE_TTL)
    return data
