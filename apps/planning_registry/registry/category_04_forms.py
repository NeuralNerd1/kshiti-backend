CATEGORY_04 = {
    "category": {
        "key": "forms",
        "name": "Form & Input Controls",
        "order": 4,
    },
    "actions": [
        {
            "action_key": "select_dropdown_value",
            "action_name": "Select Dropdown Value",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "option_value": {"type": "string"},
                },
                "optional": {
                    "match_type": {
                        "type": "string",
                        "allowed": ["exact", "contains"],
                    },
                },
            },
        },
        {
            "action_key": "select_dropdown_index",
            "action_name": "Select Dropdown Index",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "index": {"type": "number"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "select_radio",
            "action_name": "Select Radio",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "toggle_checkbox",
            "action_name": "Toggle Checkbox",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "state": {
                        "type": "string",
                        "allowed": ["on", "off"],
                    },
                },
                "optional": {},
            },
        },
        {
            "action_key": "submit_form",
            "action_name": "Submit Form",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                },
                "optional": {
                    "wait_for_navigation": {"type": "boolean"},
                },
            },
        },
        {
            "action_key": "reset_form",
            "action_name": "Reset Form",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                },
                "optional": {},
            },
        },
    ],
}
