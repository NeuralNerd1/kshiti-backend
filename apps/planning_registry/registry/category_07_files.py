CATEGORY_07 = {
    "category": {
        "key": "files",
        "name": "File Uploads & Downloads",
        "order": 7,
    },
    "actions": [
        {
            "action_key": "upload_file",
            "action_name": "Upload File",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "file_path": {"type": "string"},
                },
                "optional": {
                    "mime_type": {"type": "string"},
                },
            },
        },
        {
            "action_key": "upload_multiple_files",
            "action_name": "Upload Multiple Files",
            "schema": {
                "required": {
                    "selector_type": {"type": "string"},
                    "selector_value": {"type": "string"},
                    "file_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "optional": {},
            },
        },
        {
            "action_key": "assert_file_downloaded",
            "action_name": "Assert File Downloaded",
            "schema": {
                "required": {
                    "file_name": {"type": "string"},
                },
                "optional": {
                    "timeout_ms": {"type": "number"},
                    "download_path": {"type": "string"},
                },
            },
        },
        {
            "action_key": "assert_file_name",
            "action_name": "Assert File Name",
            "schema": {
                "required": {
                    "expected_file_name": {"type": "string"},
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
