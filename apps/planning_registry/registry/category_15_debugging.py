CATEGORY_15 = {
    "category": {
        "key": "debugging",
        "name": "Evidence & Debugging",
        "order": 15,
    },
    "actions": [
        {
            "action_key": "take_screenshot",
            "action_name": "Take Screenshot",
            "schema": {
                "required": {},
                "optional": {
                    "label": {"type": "string"},
                },
            },
        },
        {
            "action_key": "record_video",
            "action_name": "Record Video",
            "schema": {
                "required": {},
                "optional": {
                    "quality": {"type": "string"},
                },
            },
        },
        {
            "action_key": "capture_dom_snapshot",
            "action_name": "Capture DOM Snapshot",
            "schema": {
                "required": {},
                "optional": {},
            },
        },
        {
            "action_key": "log_message",
            "action_name": "Log Message",
            "schema": {
                "required": {
                    "message": {"type": "string"},
                },
                "optional": {
                    "log_level": {
                        "type": "string",
                        "allowed": ["debug", "info", "warn", "error"],
                    },
                },
            },
        },
    ],
}
