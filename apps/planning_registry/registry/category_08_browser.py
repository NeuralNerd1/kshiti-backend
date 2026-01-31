CATEGORY_08 = {
    "category": {
        "key": "browser",
        "name": "Browser & Context Control",
        "order": 8,
    },
    "actions": [
        {
            "action_key": "open_new_tab",
            "action_name": "Open New Tab",
            "schema": {
                "required": {},
                "optional": {
                    "url": {"type": "string"},
                },
            },
        },
        {
            "action_key": "switch_tab",
    "action_name": "Switch Tab",
    "schema": {
        "required": {},
        "optional": {
            "tab_index": {"type": "number"},
            "tab_title": {"type": "string"},
        },
        # Runtime validation rule
        "conditional_any_required": [
            {
                "fields": ["tab_index", "tab_title"],
                "min_required": 1,
            }
        ],
    },
        },
        {
            "action_key": "close_tab",
            "action_name": "Close Tab",
            "schema": {
                "required": {},
                "optional": {
                    "tab_index": {"type": "number"},
                },
            },
        },
        {
            "action_key": "set_viewport",
            "action_name": "Set Viewport",
            "schema": {
                "required": {
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                },
                "optional": {
                    "device_profile": {"type": "string"},
                },
            },
        },
        {
            "action_key": "set_user_agent",
            "action_name": "Set User Agent",
            "schema": {
                "required": {
                    "user_agent_string": {"type": "string"},
                },
                "optional": {},
            },
        },
    ],
}
