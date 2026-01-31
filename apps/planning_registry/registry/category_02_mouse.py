CATEGORY_02 = {
    "category": {
        "key": "mouse",
        "name": "Mouse Actions",
        "order": 2,
    },
    "actions": [
        {
            "action_key": "click",
            "action_name": "Click",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                },
                "optional": {
                    "button": {
                        "type": "string",
                        "allowed": ["left", "middle", "right"],
                    },
                    "click_count": {"type": "number"},
                    "delay_ms": {"type": "number"},
                    "force": {"type": "boolean"},
                },
            },
        },
        {
            "action_key": "double_click",
            "action_name": "Double Click",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                },
                "optional": {
                    "delay_ms": {"type": "number"},
                },
            },
        },
        {
            "action_key": "right_click",
            "action_name": "Right Click",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "click_if_visible",
            "action_name": "Click If Visible",
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
            "action_key": "force_click",
            "action_name": "Force Click",
            "is_risky": True,
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "hover",
            "action_name": "Hover",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                },
                "optional": {
                    "delay_ms": {"type": "number"},
                },
            },
        },
    ],
}
