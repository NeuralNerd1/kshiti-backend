CATEGORY_14 = {
    "category": {
        "key": "flow_control",
        "name": "Test Flow Control",
        "order": 14,
    },
    "actions": [
        {
            "action_key": "loop_block",
            "action_name": "Loop Block",
            "description": "Repeat actions based on UI conditions or element lists",
            "is_risky": True,
            "schema": {
                "required": {
                    "loop_type": {
                        "type": "string",
                        "allowed": ["while_condition", "repeat_until_condition", "for_each_element"],
                        "description": "Type of loop: while, repeat_until, or for_each",
                    },
                    "max_iterations": {
                        "type": "number",
                        "description": "Maximum number of iterations (safety limit)",
                    },
                    "actions": {
                        "type": "array",
                        "description": "Actions to execute inside the loop",
                    },
                },
                "optional": {
                    "condition": {
                        "type": "object",
                        "description": "UI condition for while/repeat_until loops",
                    },
                    "element_selector": {
                        "type": "object",
                        "description": "Element selector for for_each_element loop type",
                    },
                    "loop_timeout_ms": {
                        "type": "number",
                        "description": "Maximum time to run the loop in milliseconds",
                    },
                    "break_on_error": {
                        "type": "boolean",
                        "description": "Stop loop execution if an error occurs",
                    },
                    "fail_if_condition_never_met": {
                        "type": "boolean",
                        "description": "Fail the step if condition is never met (for repeat_until)",
                    },
                },
            },
        },
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
