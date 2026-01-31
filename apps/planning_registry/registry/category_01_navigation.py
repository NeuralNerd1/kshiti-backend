CATEGORY_01 = {
    "category": {
        "key": "navigation",
        "name": "Navigation & Page Control",
        "order": 1,
    },
    "actions": [
        {
            "action_key": "goto_url",
            "action_name": "Go to URL",
            "is_risky": False,
            "schema": {
                "required": {
                    "url": {"type": "string"},
                },
                "optional": {
                    "wait_until": {
                        "type": "string",
                        "allowed": ["domcontentloaded", "load", "networkidle"],
                    },
                    "timeout_ms": {"type": "number"},
                    "headers": {"type": "object"},
                    "auth_state": {"type": "string"},
                },
            },
        },
        {
            "action_key": "reload_page",
            "action_name": "Reload Page",
            "schema": {
                "required": {},
                "optional": {
                    "wait_until": {
                        "type": "string",
                        "allowed": ["domcontentloaded", "load", "networkidle"],
                    },
                    "timeout_ms": {"type": "number"},
                },
            },
        },
        {
            "action_key": "go_back",
            "action_name": "Go Back",
            "schema": {
                "required": {},
                "optional": {
                    "timeout_ms": {"type": "number"},
                },
            },
        },
        {
            "action_key": "go_forward",
            "action_name": "Go Forward",
            "schema": {
                "required": {},
                "optional": {
                    "timeout_ms": {"type": "number"},
                },
            },
        },
        {
            "action_key": "wait_for_navigation",
            "action_name": "Wait for Navigation",
            "schema": {
                "required": {
                    "url_match_type": {
                        "type": "string",
                        "allowed": ["contains", "equals", "regex"],
                    },
                },
                "optional": {
                    "expected_url": {"type": "string"},
                    "timeout_ms": {"type": "number"},
                },
            },
        },
        {
            "action_key": "wait_for_load_state",
            "action_name": "Wait for Load State",
            "schema": {
                "required": {
                    "load_state": {
                        "type": "string",
                        "allowed": ["dom", "networkidle"],
                    },
                },
                "optional": {
                    "timeout_ms": {"type": "number"},
                },
            },
        },
    ],
}
