CATEGORY_11 = {
    "category": {
        "key": "network",
        "name": "Network & API Observability",
        "order": 11,
    },
    "actions": [
        {
            "action_key": "wait_for_api_call",
            "action_name": "Wait for API Call",
            "schema": {
                "required": {
                    "url_pattern": {"type": "string"},
                },
                "optional": {
                    "method": {
                        "type": "string",
                        "allowed": ["GET", "POST", "PUT", "PATCH", "DELETE"],
                    },
                    "timeout_ms": {"type": "number"},
                },
            },
        },
        {
            "action_key": "assert_api_status",
            "action_name": "Assert API Status",
            "schema": {
                "required": {
                    "url_pattern": {"type": "string"},
                    "expected_status": {"type": "number"},
                },
                "optional": {
                    "method": {
                        "type": "string",
                        "allowed": ["GET", "POST", "PUT", "PATCH", "DELETE"],
                    },
                },
            },
        },
        {
            "action_key": "assert_api_response_value",
            "action_name": "Assert API Response Value",
            "schema": {
                "required": {
                    "url_pattern": {"type": "string"},
                    "json_path": {"type": "string"},
                    "expected_value": {"type": "string"},
                },
                "optional": {
                    "match_type": {
                        "type": "string",
                        "allowed": ["exact", "contains", "regex"],
                    },
                },
            },
        },
    ],
}
