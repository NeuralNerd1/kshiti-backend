CATEGORY_14 = {
    "category": {
        "key": "flow_control",
        "name": "Test Flow Control",
        "order": 14,
    },
    "actions": [
        {
            "action_key": "stop_test",
            "action_name": "Stop Test",
            "schema": {
                "required": {
                    "reason": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "skip_step",
            "action_name": "Skip Step",
            "schema": {
                "required": {
                    "step_id": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "retry_step",
            "action_name": "Retry Step",
            "schema": {
                "required": {
                    "step_id": {"type": "string"},
                    "retry_count": {"type": "number"},
                },
                "optional": {
                    "delay_ms": {"type": "number"},
                },
            },
        },
        {
            "action_key": "mark_step_optional",
            "action_name": "Mark Step Optional",
            "schema": {
                "required": {
                    "step_id": {"type": "string"},
                },
                "optional": {},
            },
        },
    ],
}
