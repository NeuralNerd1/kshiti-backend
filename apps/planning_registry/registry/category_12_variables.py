CATEGORY_12 = {
    "category": {
        "key": "variables",
        "name": "Data Handling & Variables",
        "order": 12,
    },
    "actions": [
        {
            "action_key": "store_text_as_variable",
            "action_name": "Store Text as Variable",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "variable_name": {"type": "string"},
                },
                "optional": {
                    "regex_extract": {"type": "string"},
                },
            },
        },
        {
            "action_key": "use_variable",
            "action_name": "Use Variable",
            "schema": {
                "required": {
                    "variable_name": {"type": "string"},
                },
                "optional": {
                    "fallback_value": {"type": "string"},
                },
            },
        },
        {
            "action_key": "generate_random_string",
            "action_name": "Generate Random String",
            "schema": {
                "required": {
                    "variable_name": {"type": "string"},
                },
                "optional": {
                    "length": {"type": "number"},
                    "charset": {"type": "string"},
                },
            },
        },
        {
            "action_key": "generate_timestamp",
            "action_name": "Generate Timestamp",
            "schema": {
                "required": {
                    "variable_name": {"type": "string"},
                },
                "optional": {
                    "format": {"type": "string"},
                },
            },
        },
    ],
}
