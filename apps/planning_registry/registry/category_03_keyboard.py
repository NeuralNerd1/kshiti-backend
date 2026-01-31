CATEGORY_03 = {
    "category": {
        "key": "keyboard",
        "name": "Keyboard & Text Input",
        "order": 3,
    },
    "actions": [
        {
            "action_key": "fill_text",
            "action_name": "Fill Text",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "text": {"type": "string"},
                },
                "optional": {
                    "clear_before": {"type": "boolean"},
                    "mask_input": {"type": "boolean"},
                    "delay_ms": {"type": "number"},
                },
            },
        },
        {
            "action_key": "type_text",
            "action_name": "Type Text",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "text": {"type": "string"},
                },
                "optional": {
                    "typing_speed": {"type": "number"},
                    "delay_ms": {"type": "number"},
                },
            },
        },
        {
            "action_key": "clear_field",
            "action_name": "Clear Field",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "append_text",
            "action_name": "Append Text",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "text": {"type": "string"},
                },
                "optional": {
                    "delay_ms": {"type": "number"},
                },
            },
        },
        {
            "action_key": "press_key",
            "action_name": "Press Key",
            "schema": {
                "required": {
                    "key": {"type": "string"},
                },
                "optional": {
                    "delay_ms": {"type": "number"},
                },
            },
        },
        {
            "action_key": "key_down",
            "action_name": "Key Down",
            "schema": {
                "required": {
                    "key": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "key_up",
            "action_name": "Key Up",
            "schema": {
                "required": {
                    "key": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "keyboard_shortcut",
            "action_name": "Keyboard Shortcut",
            "schema": {
                "required": {
                    "keys": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "optional": {
                    "delay_ms": {"type": "number"},
                },
            },
        },
    ],
}
