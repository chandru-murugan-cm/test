from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from controllers.ManualVaptUploadController import ManualVaptUploadController

manual_vapt_upload_blueprint = Blueprint('manual_vapt_upload_blueprint', __name__)
manual_vapt_upload_controller = ManualVaptUploadController()


@manual_vapt_upload_blueprint.route('/crscan/manual-vapt-upload', methods=['POST'])
@jwt_required()
def upload_manual_vapt():
    """
    API endpoint to upload manual VAPT findings via JSON file.

    Expected form data:
    - project_id: The project ID to associate findings with
    - user_id: The user ID for the upload
    - json_file: The JSON file containing findings

    JSON file format:
    {
        "findings": [
            {
                "finding_name": "SQL Injection",
                "finding_desc": "SQL injection vulnerability in login form",
                "severity": "high",
                "status": "open",
                "target_type": "domain"
            }
        ]
    }

    Valid values:
    - severity: critical, high, medium, low, informational
    - status: open, closed, ignored, false positive
    - target_type: repo, domain, container, cloud, web3, vm
    """
    return manual_vapt_upload_controller.upload_manual_vapt(request)


@manual_vapt_upload_blueprint.route('/crscan/manual-vapt-upload/validate', methods=['POST'])
@jwt_required()
def validate_json():
    """
    API endpoint to validate a JSON file without creating database entries.
    Useful for preview functionality before actual upload.

    Expected form data:
    - json_file: The JSON file to validate

    Returns:
    - valid: boolean indicating if JSON is valid
    - findings_count: number of findings in the file
    - preview: array of finding previews
    - errors: array of validation errors (if invalid)
    """
    return manual_vapt_upload_controller.validate_json(request)


@manual_vapt_upload_blueprint.route('/crscan/manual-vapt-upload/findings', methods=['GET'])
@jwt_required()
def get_manual_findings():
    """
    API endpoint to get all manual VAPT findings.

    Query parameters:
    - project_id: Filter by project
    - user_id: Filter by user
    - severity: Filter by severity (critical, high, medium, low, informational)
    - status: Filter by status (open, closed, ignored, false positive)
    - target_type: Filter by target type (repo, domain, container, cloud, web3, vm)

    Returns:
    - data: array of findings
    - total: total count
    """
    return manual_vapt_upload_controller.get_manual_findings(request)


@manual_vapt_upload_blueprint.route('/crscan/manual-vapt-upload/findings/<finding_id>', methods=['PUT'])
@jwt_required()
def update_finding(finding_id):
    """
    API endpoint to update a manual VAPT finding.

    Expected JSON body:
    - finding_name: Updated finding name
    - finding_desc: Updated finding description
    - severity: Updated severity
    - status: Updated status
    - target_type: Updated target type
    """
    return manual_vapt_upload_controller.update_finding(finding_id, request)


@manual_vapt_upload_blueprint.route('/crscan/manual-vapt-upload/findings/<finding_id>', methods=['DELETE'])
@jwt_required()
def delete_finding(finding_id):
    """
    API endpoint to delete a manual VAPT finding.
    """
    return manual_vapt_upload_controller.delete_finding(finding_id)
