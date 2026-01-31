CATEGORY_09 = {
    "category": {
        "key": "scroll",
        "name": "Scroll & Viewport",
        "order": 9,
    },
    "actions": [
        {
            "action_key": "scroll_to_element",
            "action_name": "Scroll to Element",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "scroll_by_pixels",
            "action_name": "Scroll by Pixels",
            "schema": {
                "required": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "scroll_to_top",
            "action_name": "Scroll to Top",
            "schema": {
                "required": {},
                "optional": {},
            },
        },
        {
            "action_key": "scroll_to_bottom",
            "action_name": "Scroll to Bottom",
            "schema": {
                "required": {},
                "optional": {},
            },
        },
    ],
}
