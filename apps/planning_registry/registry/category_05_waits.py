CATEGORY_05 = {
    "category": {
        "key": "waits",
        "name": "Wait & Timing Controls",
        "order": 5,
    },
    "actions": [
        {
            "action_key": "wait_for_element_visible",
            "action_name": "Wait for Element Visible",
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
            "action_key": "wait_for_element_hidden",
            "action_name": "Wait for Element Hidden",
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
            "action_key": "wait_for_timeout",
            "action_name": "Wait for Timeout",
            "is_risky": True,
            "schema": {
                "required": {
                    "duration_ms": {"type": "number"},
                    "reason": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "wait_for_text",
            "action_name": "Wait for Text",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "text": {"type": "string"},
                },
                "optional": {
                    "match_type": {
                        "type": "string",
                        "allowed": ["exact", "contains", "regex"],
                    },
                    "timeout_ms": {"type": "number"},
                },
            },
        },
        {
            "action_key": "wait_for_url",
            "action_name": "Wait for URL",
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
                # Runtime-only rule (same pattern as Category 1)
                "conditional_required": [
                    {
                        "if": {
                            "field": "url_match_type",
                            "operator": "in",
                            "value": ["contains", "equals"],
                        },
                        "then_require": ["expected_url"],
                    }
                ],
            },
        },
    ],
}
