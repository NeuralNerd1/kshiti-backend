CATEGORY_13 = {
    "category": {
        "key": "conditionals",
        "name": "Conditional Logic",
        "order": 13,
    },
    "actions": [
        {
            "action_key": "conditional_block",
            "action_name": "Conditional Block",
            "description": "Execute actions based on UI conditions with logical operators",
            "is_risky": False,
            "schema": {
                "required": {
                    "conditions": {
                        "type": "array",
                        "description": "Array of condition objects with logical operators",
                    },
                    "if_true_actions": {
                        "type": "array",
                        "description": "Actions to execute if conditions evaluate to true",
                    },
                },
                "optional": {
                    "else_actions": {
                        "type": "array",
                        "description": "Actions to execute if conditions evaluate to false (optional)",
                    },
                },
            },
        },
    ],
}
