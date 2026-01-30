from flask import Blueprint, request
from controllers.FindingMasterController import FindingMasterController
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response

finding_master_blueprint = Blueprint(
    'finding_master_blueprint', __name__)
finding_master_controller = FindingMasterController()


@finding_master_blueprint.route('/crscan/finding_master', methods=['POST'])
def add_finding_master():
    if request.data:
        return finding_master_controller.add_entity(request)
    return {'error': 'Missing Finding Master details'}, 400


@finding_master_blueprint.route('/crscan/finding_master', methods=['GET'])
def get_finding_masterk():
    fields = {}
    if 'finding_id' in request.args:
        fields['_id'] = request.args.get('finding_id')
    return finding_master_controller.fetch_all(request, fields)


@finding_master_blueprint.route('/crscan/finding_master/<project_id>', methods=['GET'])
@swag_from({
    'tags': ['Findings'],
    'summary': 'Get security findings by project ID',
    'description': 'Retrieve all security findings discovered for a specific project',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'name': 'project_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'ID of the project to get findings for'
        }
    ],
    'responses': {
        200: {
            'description': 'Findings retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                '_id': {'type': 'string', 'example': '507f1f77bcf86cd799439011'},
                                'project_id': {'type': 'string'},
                                'title': {'type': 'string', 'example': 'SQL Injection Vulnerability'},
                                'description': {'type': 'string', 'example': 'SQL injection found in login form'},
                                'severity': {'type': 'string', 'example': 'high', 'enum': ['low', 'medium', 'high', 'critical']},
                                'status': {'type': 'string', 'example': 'open', 'enum': ['open', 'resolved', 'false_positive', 'accepted_risk']},
                                'scanner_type': {'type': 'string', 'example': 'zap'},
                                'target_type': {'type': 'string', 'example': 'web_application'},
                                'found_at': {'type': 'string', 'format': 'date-time'},
                                'cvss_score': {'type': 'number', 'example': 8.5},
                                'cve_ids': {
                                    'type': 'array',
                                    'items': {'type': 'string'},
                                    'example': ['CVE-2023-1234']
                                }
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Project not found or no findings available',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized - Invalid or missing JWT token',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def get_finding_master_by_project_id(project_id=None):
    fields = {}
    if project_id:
        fields['project_id'] = project_id
        return finding_master_controller.fetch_by_project_id(fields)
    

@finding_master_blueprint.route('/crscan/finding_master/<finding_id>/status', methods=['PATCH'])
def update_finding_master_status(finding_id):
    return finding_master_controller.update_status(finding_id, request)


@finding_master_blueprint.route('/crscan/finding_master/counts/<project_id>', methods=['GET'])
@swag_from({
    'tags': ['Findings'],
    'summary': 'Get finding counts by severity for a project',
    'description': 'Retrieve summary statistics of security findings grouped by severity level',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'name': 'project_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'ID of the project to get finding counts for'
        }
    ],
    'responses': {
        200: {
            'description': 'Finding counts retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'total_findings': {'type': 'integer', 'example': 25},
                            'by_severity': {
                                'type': 'object',
                                'properties': {
                                    'critical': {'type': 'integer', 'example': 2},
                                    'high': {'type': 'integer', 'example': 5},
                                    'medium': {'type': 'integer', 'example': 10},
                                    'low': {'type': 'integer', 'example': 8}
                                }
                            },
                            'by_status': {
                                'type': 'object',
                                'properties': {
                                    'open': {'type': 'integer', 'example': 15},
                                    'resolved': {'type': 'integer', 'example': 8},
                                    'false_positive': {'type': 'integer', 'example': 2}
                                }
                            },
                            'by_scanner': {
                                'type': 'object',
                                'properties': {
                                    'zap': {'type': 'integer', 'example': 12},
                                    'trivy': {'type': 'integer', 'example': 8},
                                    'slither': {'type': 'integer', 'example': 5}
                                }
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Project not found',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized - Invalid or missing JWT token',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def get_finding_master_counts(project_id):
    return finding_master_controller.get_finding_master_counts(project_id)


@finding_master_blueprint.route('/crscan/finding_master/<finding_id>/extended_details', methods=['GET'])
def get_extended_finding_details(finding_id):
    return finding_master_controller.get_extended_finding_details(finding_id)


@finding_master_blueprint.route('/crscan/finding_master/has_findings_bulk', methods=['POST'])
def has_findings_bulk():
    """
    Checks if any findings exist for multiple target IDs.
    """
    return finding_master_controller.has_findings_bulk(request)

