from flask import Blueprint, request,jsonify
import urllib.parse
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response
from controllers.SammController import SammController

samm_blueprint = Blueprint('samm_blueprint', __name__)
samm_controller = SammController()


# @samm_blueprint.route('/cs/samm', methods=['GET'])
# def get_unique_samm_types():
#     return sam_controller.get_unique_samm_types()


@samm_blueprint.route('/crscan/samm', methods=['GET'])
@swag_from({
    'tags': ['SAMM Compliance'],
    'summary': 'Retrieve SAMM compliance data',
    'description': 'Fetch SAMM (Software Assurance Maturity Model) compliance data by project ID or all records. SAMM is a framework for secure software development lifecycle.',
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
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Project ID to filter SAMM records'
        }
    ],
    'responses': {
        200: {
            'description': 'SAMM compliance data retrieved successfully',
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
                                'business_function': {'type': 'string', 'example': 'Governance'},
                                'security_practice': {'type': 'string', 'example': 'Strategy & Metrics'},
                                'maturity_level': {'type': 'integer', 'example': 2},
                                'compliance_status': {'type': 'string', 'example': 'compliant'}
                            }
                        }
                    }
                }
            }
        },
        401: {
            'description': 'Unauthorized - Invalid or missing token',
            'schema': error_response
        },
        404: {
            'description': 'Not found - No SAMM records found',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def get_samm():
    """
    Fetch samm by _id, samm, or compliance_group_name using query parameters.
    """
    project_id = urllib.parse.unquote(request.args.get('project_id', ''))
    if project_id:
        return samm_controller.fetch_by_project_id(project_id)
    if request.method == "GET":
        return samm_controller.fetch_all(request)
    

@samm_blueprint.route('/crscan/samm', methods=['POST'])
@swag_from({
    'tags': ['SAMM Compliance'],
    'summary': 'Create SAMM compliance record',
    'description': 'Create a new SAMM compliance record for a project with business function, security practice, and maturity level information.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['project_id', 'business_function', 'security_practice'],
                'properties': {
                    'project_id': {'type': 'string', 'example': '507f1f77bcf86cd799439012'},
                    'business_function': {'type': 'string', 'example': 'Governance'},
                    'security_practice': {'type': 'string', 'example': 'Strategy & Metrics'},
                    'maturity_level': {'type': 'integer', 'example': 2},
                    'compliance_status': {'type': 'string', 'example': 'compliant'},
                    'notes': {'type': 'string', 'example': 'Assessment completed successfully'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'SAMM compliance record created successfully',
            'schema': success_response
        },
        400: {
            'description': 'Bad request - Missing SAMM details',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized - Invalid or missing token',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def postSamm():
    if request.method == "POST":
        if request.data:
            return samm_controller.add_entity(request)
        return {'error': 'Missing SAMM details'}, '400 Bad Request'

@samm_blueprint.route('/crscan/samm/<samm_id>', methods=['PUT', 'DELETE'])
def samm(samm_id):
    if request.method == "DELETE":
        if samm_id:
            return samm_controller.delete_entity(samm_id)
        return jsonify({'error': 'Missing Samm ID'}), 400

    elif request.method == 'PUT':
        if samm_id and request.data:
                response = samm_controller.update_entity(samm_id,request.get_json())
                return response
        return jsonify({'error': 'Missing Samm details for update'}), 400
    
    
@samm_blueprint.route('/crscan/samm/l1_business_function', methods=['GET'])
def get_all_l1_business_functions():
    if request.method == "GET":
        return samm_controller.fetch_all_l1_business_functions()
        
         





