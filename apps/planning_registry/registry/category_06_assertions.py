CATEGORY_06 = {
    "category": {
        "key": "assertions",
        "name": "Assertions",
        "order": 6,
    },
    "actions": [
        # --------------------------------------------------
        # Visibility & Presence
        # --------------------------------------------------
        {
            "action_key": "assert_element_visible",
            "action_name": "Assert Element Visible",
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
            "action_key": "assert_element_hidden",
            "action_name": "Assert Element Hidden",
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
            "action_key": "assert_element_exists",
            "action_name": "Assert Element Exists",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "assert_element_not_exists",
            "action_name": "Assert Element Not Exists",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                },
                "optional": {},
            },
        },

        # --------------------------------------------------
        # Text Assertions
        # --------------------------------------------------
        {
            "action_key": "assert_text_equals",
            "action_name": "Assert Text Equals",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "expected_text": {"type": "string"},
                },
                "optional": {
                    "trim": {"type": "boolean"},
                    "case_sensitive": {"type": "boolean"},
                },
            },
        },
        {
            "action_key": "assert_text_contains",
            "action_name": "Assert Text Contains",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "expected_text": {"type": "string"},
                },
                "optional": {
                    "case_sensitive": {"type": "boolean"},
                },
            },
        },
        {
            "action_key": "assert_text_matches_regex",
            "action_name": "Assert Text Matches Regex",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "regex": {"type": "string"},
                },
                "optional": {},
            },
        },

        # --------------------------------------------------
        # Attribute & State Assertions
        # --------------------------------------------------
        {
            "action_key": "assert_attribute_value",
            "action_name": "Assert Attribute Value",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "attribute": {"type": "string"},
                    "expected_value": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "assert_input_value",
            "action_name": "Assert Input Value",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "expected_value": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "assert_checkbox_checked",
            "action_name": "Assert Checkbox Checked",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "assert_element_enabled",
            "action_name": "Assert Element Enabled",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "assert_element_disabled",
            "action_name": "Assert Element Disabled",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                },
                "optional": {},
            },
        },

        # --------------------------------------------------
        # Page-level Assertions
        # --------------------------------------------------
        {
            "action_key": "assert_url_equals",
            "action_name": "Assert URL Equals",
            "schema": {
                "required": {
                    "expected_url": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "assert_url_contains",
            "action_name": "Assert URL Contains",
            "schema": {
                "required": {
                    "expected_partial_url": {"type": "string"},
                },
                "optional": {},
            },
        },
        {
            "action_key": "assert_title",
            "action_name": "Assert Page Title",
            "schema": {
                "required": {
                    "expected_title": {"type": "string"},
                },
                "optional": {},
            },
        },
    ],
}
