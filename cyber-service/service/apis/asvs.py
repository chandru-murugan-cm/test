from flask import Blueprint, jsonify, request
import urllib.parse
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response
from controllers.AsvsController import AsvsController

asvs_blueprint = Blueprint('asvs_blueprint', __name__)
asvs_controller = AsvsController()


# @asvs_blueprint.route('/cs/samm', methods=['GET'])
# def get_unique_samm_types():
#     return sam_controller.get_unique_samm_types()


@asvs_blueprint.route('/crscan/asvs', methods=['GET'])
@swag_from({
    'tags': ['ASVS Compliance'],
    'summary': 'Retrieve ASVS compliance data',
    'description': 'Fetch ASVS (Application Security Verification Standard) compliance data by chapter, section, requirement, or all records. ASVS provides security requirements for web applications.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'name': 'chapter_id',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'ASVS chapter ID to filter records'
        },
        {
            'name': 'section_id',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'ASVS section ID to filter records'
        },
        {
            'name': 'requirement_id',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'ASVS requirement ID to filter records'
        }
    ],
    'responses': {
        200: {
            'description': 'ASVS compliance data retrieved successfully',
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
                                'chapter_id': {'type': 'string', 'example': 'V1'},
                                'section_id': {'type': 'string', 'example': 'V1.1'},
                                'requirement_id': {'type': 'string', 'example': 'V1.1.1'},
                                'requirement_text': {'type': 'string', 'example': 'Verify that the application enforces composition and complexity rules'},
                                'level': {'type': 'integer', 'example': 1},
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
            'description': 'Not found - No ASVS records found',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def get_asvs():
    """
    Fetch asvs by chapter_id, section_id, requirement_id, or asvs using query parameters.
    """
    if request.method == "GET":
        return asvs_controller.fetch_all(request)
    

@asvs_blueprint.route('/crscan/asvs', methods=['POST'])
@swag_from({
    'tags': ['ASVS Compliance'],
    'summary': 'Create ASVS compliance record',
    'description': 'Create a new ASVS compliance record with chapter, section, requirement details and compliance status.',
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
                'required': ['chapter_id', 'section_id', 'requirement_id', 'requirement_text'],
                'properties': {
                    'chapter_id': {'type': 'string', 'example': 'V1'},
                    'section_id': {'type': 'string', 'example': 'V1.1'},
                    'requirement_id': {'type': 'string', 'example': 'V1.1.1'},
                    'requirement_text': {'type': 'string', 'example': 'Verify that the application enforces composition and complexity rules'},
                    'level': {'type': 'integer', 'example': 1},
                    'compliance_status': {'type': 'string', 'example': 'compliant'},
                    'notes': {'type': 'string', 'example': 'Verification completed successfully'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'ASVS compliance record created successfully',
            'schema': success_response
        },
        400: {
            'description': 'Bad request - Missing ASVS details',
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
            return asvs_controller.add_entity(request)
        return {'error': 'Missing ASVS details'}, '400 Bad Request'

@asvs_blueprint.route('/crscan/asvs/<asvs_id>', methods=['PUT', 'DELETE'])
def asvs(asvs_id):
    print(f"Received request: {request.method} for ASVS ID: {asvs_id}")
    
    if request.method == "DELETE":
        print("ASVS Id:", asvs_id)
        if asvs_id:
            return asvs_controller.delete_entity(asvs_id)
        return jsonify({'error': 'Missing ASVS ID'}), 400

    elif request.method == 'PUT':
        if asvs_id and request.data:
            response = asvs_controller.update_entity(asvs_id, request.get_json())
            return response
        return jsonify({'error': 'Missing ASVS details for update'}), 400




