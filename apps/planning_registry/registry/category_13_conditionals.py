CATEGORY_13 = {
    "category": {
        "key": "conditionals",
        "name": "Conditional Logic",
        "order": 13,
    },
    "actions": [
        {
            "action_key": "if_element_visible",
            "action_name": "If Element Visible",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                },
                "optional": {
                    "timeout_ms": {"type": "number"},
                },
            },
        },
        {
            "action_key": "if_text_equals",
            "action_name": "If Text Equals",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "expected_text": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "else_block",
            "action_name": "Else Block",
            "schema": {
                "required": {},
                "optional": {},
            },
        },
        {
            "action_key": "end_if",
            "action_name": "End If",
            "schema": {
                "required": {},
                "optional": {},
            },
        },
    ],
}
