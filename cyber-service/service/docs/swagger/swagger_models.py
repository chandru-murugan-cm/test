"""
Swagger models/schemas for API documentation
"""

# Common response models
success_response = {
    "type": "object",
    "properties": {
        "success": {
            "type": "string",
            "description": "Success message"
        },
        "data": {
            "type": "object",
            "description": "Response data"
        }
    },
    "required": ["success"]
}

error_response = {
    "type": "object",
    "properties": {
        "error": {
            "type": "string",
            "description": "Error message"
        }
    },
    "required": ["error"]
}

# Project models
project_model = {
    "type": "object",
    "properties": {
        "_id": {
            "type": "string",
            "description": "Project ID"
        },
        "name": {
            "type": "string",
            "description": "Project name"
        },
        "description": {
            "type": "string",
            "description": "Project description"
        },
        "organization": {
            "type": "string",
            "description": "Organization name"
        },
        "status": {
            "type": "string",
            "enum": ["init", "pending", "completed"],
            "description": "Project status"
        },
        "domain_value": {
            "type": "string",
            "description": "Primary domain for the project"
        },
        "created": {
            "type": "string",
            "format": "date-time",
            "description": "Creation timestamp"
        }
    },
    "required": ["name", "organization"]
}

# Scan models
scan_model = {
    "type": "object",
    "properties": {
        "scan_id": {
            "type": "string",
            "description": "Scan ID"
        },
        "project_id": {
            "type": "string",
            "description": "Project ID"
        },
        "status": {
            "type": "string",
            "enum": ["scheduled", "running", "completed", "error"],
            "description": "Scan status"
        },
        "scanner_name": {
            "type": "string",
            "description": "Scanner name"
        },
        "created": {
            "type": "string",
            "format": "date-time",
            "description": "Creation timestamp"
        }
    }
}

create_scan_request = {
    "type": "object",
    "properties": {
        "scheduler_response": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "Project ID to scan"
                },
                "scanner_type_ids_list": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of scanner type IDs to run"
                },
                "_id": {
                    "type": "string",
                    "description": "Scheduler ID"
                }
            },
            "required": ["project_id", "scanner_type_ids_list"]
        },
        "scan_status": {
            "type": "string",
            "enum": ["scheduled", "immediate"],
            "default": "scheduled",
            "description": "Scan execution mode"
        }
    },
    "required": ["scheduler_response"]
}