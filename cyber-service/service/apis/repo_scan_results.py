from flask import Blueprint, request
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response
from controllers.RepoScanResultsController import RepoScanResultsController

repo_scan_results_blueprint = Blueprint(
    'repo_scan_results_blueprint', __name__)
repoScanResultsController = RepoScanResultsController()

@repo_scan_results_blueprint.route('/crscan/repo_scan/licenses_and_sbom/<project_id>', methods=['GET'])
@repo_scan_results_blueprint.route('/crscan/repo_scan/licenses_and_sbom/group/<project_id>', methods=['GET'])
@swag_from({
    'tags': ['Repository Scan Results'],
    'summary': 'Retrieve repository scan results for licenses and SBOM',
    'description': 'Fetch repository scan results including software licenses and Software Bill of Materials (SBOM) data. Can be grouped by type and risk level.',
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
            'description': 'Project ID to retrieve scan results for'
        },
        {
            'name': 'license_type',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter by specific license type (e.g., MIT, Apache, GPL)'
        }
    ],
    'responses': {
        200: {
            'description': 'Repository scan results retrieved successfully',
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
                                'project_id': {'type': 'string', 'example': '507f1f77bcf86cd799439012'},
                                'package_name': {'type': 'string', 'example': 'express'},
                                'version': {'type': 'string', 'example': '4.18.2'},
                                'license_type': {'type': 'string', 'example': 'MIT'},
                                'risk_level': {'type': 'string', 'example': 'low'},
                                'sbom_data': {'type': 'object', 'example': {}},
                                'scan_date': {'type': 'string', 'format': 'date-time'}
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request - Missing Project ID',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized - Invalid or missing token',
            'schema': error_response
        },
        404: {
            'description': 'Not found - No scan results found for project',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def repo_scan_results(project_id = None):
    if project_id:
        fields = {}
        fields['project_id'] = project_id
        if 'group' in request.path:
            return repoScanResultsController.fetch_licenses_groupby_type_and_risk(request, fields)
        else:
            fields['license_type'] = request.args.get('license_type', None)
            return repoScanResultsController.fetch_licenses_and_sbom(request, fields)
    return {'error': 'Missing Project ID'}, '400 Bad request'

@repo_scan_results_blueprint.route('/crscan/repo_scan/licenses_and_sbom/vuln/<project_id>', methods=['GET'])
@swag_from({
    'tags': ['Repository Scan Results'],
    'summary': 'Retrieve SBOM vulnerability scan results',
    'description': 'Fetch vulnerability information from Software Bill of Materials (SBOM) analysis for a specific project.',
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
            'description': 'Project ID to retrieve vulnerability results for'
        }
    ],
    'responses': {
        200: {
            'description': 'SBOM vulnerability results retrieved successfully',
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
                                'project_id': {'type': 'string', 'example': '507f1f77bcf86cd799439012'},
                                'vulnerability_id': {'type': 'string', 'example': 'CVE-2022-1234'},
                                'package_name': {'type': 'string', 'example': 'lodash'},
                                'affected_version': {'type': 'string', 'example': '4.17.19'},
                                'severity': {'type': 'string', 'example': 'high'},
                                'description': {'type': 'string', 'example': 'Prototype pollution vulnerability'},
                                'fixed_version': {'type': 'string', 'example': '4.17.21'}
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request - Missing Project ID',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized - Invalid or missing token',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def vulnerability_scan_results(project_id = None):
    if project_id:
        fields = {}
        fields['project_id'] = project_id
        return repoScanResultsController.fetch_sbom_vulnerabilities(request, fields)
    return {'error': 'Missing Project ID'}, '400 Bad request'

@repo_scan_results_blueprint.route('/crscan/repo_scan/licenses/<project_id>', methods=['GET'])
def get_licenses_by_project_id(project_id = None):
    if project_id:
        fields = {}
        fields['project_id'] = project_id
        return repoScanResultsController.fetch_licenses_by_project_id(request, fields)
    return {'error': 'Missing Project ID'}, '400 Bad request'