
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db import transaction

from apps.planning_registry.models import ActionCategory, ActionDefinition

from apps.planning_registry.registry.category_01_navigation import CATEGORY_01
from apps.planning_registry.registry.category_02_mouse import CATEGORY_02
from apps.planning_registry.registry.category_03_keyboard import CATEGORY_03
from apps.planning_registry.registry.category_04_forms import CATEGORY_04
from apps.planning_registry.registry.category_05_waits import CATEGORY_05
from apps.planning_registry.registry.category_06_assertions import CATEGORY_06
from apps.planning_registry.registry.category_07_files import CATEGORY_07
from apps.planning_registry.registry.category_08_browser import CATEGORY_08
from apps.planning_registry.registry.category_09_scroll import CATEGORY_09
from apps.planning_registry.registry.category_10_frames import CATEGORY_10
from apps.planning_registry.registry.category_11_network import CATEGORY_11
from apps.planning_registry.registry.category_12_variables import CATEGORY_12
from apps.planning_registry.registry.category_13_conditionals import CATEGORY_13
from apps.planning_registry.registry.category_14_flow_control import CATEGORY_14
from apps.planning_registry.registry.category_15_debugging import CATEGORY_15
from apps.planning_registry.registry.category_16_environment import CATEGORY_16


ACTION_REGISTRY = [
    CATEGORY_01,
    CATEGORY_02,
    CATEGORY_03,
    CATEGORY_04,
    CATEGORY_05,
    CATEGORY_06,
    CATEGORY_07,
    CATEGORY_08,
    CATEGORY_09,
    CATEGORY_10,
    CATEGORY_11,
    CATEGORY_12,
    CATEGORY_13,
    CATEGORY_14,
    CATEGORY_15,
    CATEGORY_16,
]

class Command(BaseCommand):
    help = "Seed global Action Registry"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding Action Registry...")

        for block in ACTION_REGISTRY:
            cat_data = block["category"]

            category, _ = ActionCategory.objects.update_or_create(
                key=cat_data["key"],
                defaults={
                    "name": cat_data["name"],
                    "order": cat_data["order"],
                },
            )

            for action in block["actions"]:
                ActionDefinition.objects.update_or_create(
                    action_key=action["action_key"],
                    defaults={
                        "action_name": action["action_name"],
                        "category": category,
                        "is_risky": action.get("is_risky", False),
                        "parameter_schema": action["schema"],
                    },
                )

        self.stdout.write(
            self.style.SUCCESS("Action Registry seeded successfully.")
        )

