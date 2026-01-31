CATEGORY_10 = {
    "category": {
        "key": "frames_modals",
        "name": "Frames, Modals & Popups",
        "order": 10,
    },
    "actions": [
        {
            "action_key": "switch_iframe",
            "action_name": "Switch Iframe",
            "schema": {
                "required": {
                    "iframe_selector": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "exit_iframe",
            "action_name": "Exit Iframe",
            "schema": {
                "required": {},
                "optional": {},
            },
        },
        {
            "action_key": "handle_alert_accept",
            "action_name": "Handle Alert Accept",
            "schema": {
                "required": {},
                "optional": {
                    "expected_text": {"type": "string"},
                },
            },
        },
        {
            "action_key": "handle_alert_dismiss",
            "action_name": "Handle Alert Dismiss",
            "schema": {
                "required": {},
                "optional": {
                    "expected_text": {"type": "string"},
                },
            },
        },
        {
            "action_key": "assert_alert_text",
            "action_name": "Assert Alert Text",
            "schema": {
                "required": {
                    "expected_text": {"type": "string"},
                },
                "optional": {},
            },
        },
    ],
}
