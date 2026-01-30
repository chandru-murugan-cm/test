from flask import Blueprint, request, jsonify
import urllib.parse
from controllers.ComplianceController import ComplianceController
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response

compliance_blueprint = Blueprint('compliance_blueprint', __name__)
compliance_controller = ComplianceController()


@compliance_blueprint.route('/crscan/compliance/unique/compliance_types', methods=['GET'])
@swag_from({
    'tags': ['Compliance'],
    'summary': 'Get unique compliance framework types',
    'description': 'Retrieve all available compliance framework types in the system (SAMM, ASVS, OWASP Top 10, etc.)',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        }
    ],
    'responses': {
        200: {
            'description': 'Compliance types retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'compliance_type': {'type': 'string', 'example': 'SAMM'},
                                'display_name': {'type': 'string', 'example': 'Software Assurance Maturity Model'},
                                'description': {'type': 'string', 'example': 'Framework for software security assurance'},
                                'version': {'type': 'string', 'example': '2.0'},
                                'total_controls': {'type': 'integer', 'example': 15}
                            }
                        }
                    }
                }
            }
        },
        401: {
            'description': 'Unauthorized - Invalid or missing JWT token',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def get_unique_compliance_types():
    return compliance_controller.get_unique_compliance_types()


@compliance_blueprint.route('/crscan/compliance', methods=['GET'])
@swag_from({
    'tags': ['Compliance'],
    'summary': 'Get compliance framework data',
    'description': 'Retrieve compliance framework assessments by ID, type, or group name with detailed control mappings',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'name': '_id',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Specific compliance record ID'
        },
        {
            'name': 'compliance_type',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter by compliance framework type (SAMM, ASVS, OWASP, etc.)'
        },
        {
            'name': 'project_id',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter compliance assessments by project ID'
        },
        {
            'name': 'compliance_group_name',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter by compliance group or category name'
        }
    ],
    'responses': {
        200: {
            'description': 'Compliance data retrieved successfully',
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
                                'compliance_type': {'type': 'string', 'example': 'SAMM'},
                                'compliance_group_name': {'type': 'string', 'example': 'Governance'},
                                'control_id': {'type': 'string', 'example': 'G-EG-1'},
                                'control_title': {'type': 'string', 'example': 'Establish governance and compliance'},
                                'control_description': {'type': 'string'},
                                'maturity_level': {'type': 'integer', 'example': 2, 'minimum': 0, 'maximum': 3},
                                'assessment_status': {'type': 'string', 'example': 'compliant', 'enum': ['compliant', 'non_compliant', 'partially_compliant', 'not_assessed']},
                                'evidence': {'type': 'string', 'example': 'Security policy document v2.1'},
                                'findings_count': {'type': 'integer', 'example': 3},
                                'last_assessment': {'type': 'string', 'format': 'date-time'},
                                'next_review': {'type': 'string', 'format': 'date'}
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'No valid query parameter provided',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized - Invalid or missing JWT token',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def get_compliance():
    """
    Fetch compliance by _id, compliance_type, or compliance_group_name using query parameters.
    """
    # Fetch query parameters
    compliance_id = urllib.parse.unquote(request.args.get('_id', ''))
    compliance_type = urllib.parse.unquote(request.args.get('compliance_type', ''))
    project_id = urllib.parse.unquote(request.args.get('project_id', ''))
    compliance_group_name = urllib.parse.unquote(request.args.get('compliance_group_name', ''))
    # Fetch by compliance_id
    if compliance_id:
        fields = {'_id': compliance_id}
        return compliance_controller.fetch_by_id(fields)
    # Fetch by compliance_type
    if compliance_type:
        return compliance_controller.fetch_by_compliance_type(compliance_type, project_id)
    # Fetch by compliance_group_name
    if compliance_group_name:
        return compliance_controller.fetch_by_compliance_group_name(compliance_group_name)
    return {'error': 'No valid query parameter provided'}, '400 Bad Request'

@compliance_blueprint.route('/crscan/compliance', methods=['POST'])
def postCompliance():
    if request.method == "POST":
        if request.data:
            return compliance_controller.add_entity(request)
        return {'error': 'Missing Compliance details'}, '400 Bad Request'

@compliance_blueprint.route('/crscan/compliance/<compliance_id>', methods=['PUT', 'DELETE'])
def compliance(compliance_id):
    if request.method == "DELETE":
        print("Compliance Id:", compliance_id)
        if compliance_id:
            return compliance_controller.delete_entity(compliance_id)
        return jsonify({'error': 'Missing Compliance ID'}), 400

    elif request.method == 'PUT':
        if compliance_id and request.data:
            response = compliance_controller.update_entity(compliance_id, request.get_json())
            return response
        return jsonify({'error': 'Missing Compliance details for update'}), 400

@compliance_blueprint.route('/crscan/compliance/summary', methods=['GET'])
def get_compliance_summary():
    project_id = urllib.parse.unquote(request.args.get('project_id', ''))
    if not project_id:
        return jsonify({'error': 'Missing project_id'}), 400
    return compliance_controller.fetch_compliance_summary(project_id)


