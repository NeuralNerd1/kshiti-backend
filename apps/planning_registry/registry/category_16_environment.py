CATEGORY_16 = {
    "category": {
        "key": "environment",
        "name": "Environment & Session Control",
        "order": 16,
    },
    "actions": [
        {
            "action_key": "clear_cookies",
            "action_name": "Clear Cookies",
            "schema": {
                "required": {},
                "optional": {
                    "domain": {"type": "string"},
                },
            },
        },
        {
            "action_key": "clear_local_storage",
            "action_name": "Clear Local Storage",
            "schema": {
                "required": {},
                "optional": {},
            },
        },
        {
            "action_key": "set_cookie",
            "action_name": "Set Cookie",
            "is_risky": True,
            "schema": {
                "required": {
                    "name": {"type": "string"},
                    "value": {"type": "string"},
                    "domain": {"type": "string"},
                },
                "optional": {
                    "expiry": {"type": "number"},
                    "path": {"type": "string"},
                    "secure": {"type": "boolean"},
                },
            },
        },
        {
            "action_key": "set_local_storage",
            "action_name": "Set Local Storage",
            "is_risky": True,
            "schema": {
                "required": {
                    "key": {"type": "string"},
                    "value": {"type": "string"},
                },
                "optional": {},
            },
        },
    ],
}
