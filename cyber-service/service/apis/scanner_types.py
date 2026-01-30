
from flask import Blueprint, jsonify, request
from controllers.ScannerTypeController import ScannerTypeController
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response

scanner_type_blueprint = Blueprint('scanner_type_blueprint', __name__)
scanner_type_controller = ScannerTypeController()

@scanner_type_blueprint.route('/cs/scanner-types', methods=['POST'])
@swag_from({
    'tags': ['Scanner Types'],
    'summary': 'Create a new scanner type',
    'description': 'Add a new scanner type definition with its capabilities and target mappings',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        }
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'required': ['name', 'scanner_type', 'target_types'],
                    'properties': {
                        'name': {'type': 'string', 'example': 'OWASP ZAP DAST'},
                        'scanner_type': {'type': 'string', 'example': 'DAST', 'enum': ['SAST', 'DAST', 'SCA', 'CSPM']},
                        'target_types': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'example': ['web_application', 'api']
                        },
                        'description': {'type': 'string', 'example': 'Dynamic Application Security Testing'},
                        'configuration_schema': {
                            'type': 'object',
                            'example': {'url': {'type': 'string', 'required': True}}
                        },
                        'supported_formats': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'example': ['json', 'xml', 'html']
                        }
                    }
                }
            }
        }
    },
    'responses': {
        201: {
            'description': 'Scanner type created successfully',
            'schema': success_response
        },
        400: {
            'description': 'Missing or invalid scanner type details',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized - Invalid or missing JWT token',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def add_scanner():
    if request.data:
        return scanner_type_controller.add_entity(request)
    return {'error': 'Missing scanner type details'}, 400

@scanner_type_blueprint.route('/cs/scanner-types', methods=['GET'])
def get_scanners():
    fields = {}
    if 'scanner_id' in request.args:
        fields['_id'] = request.args['scanner_id']
    return scanner_type_controller.fetch_all(request, fields)

@scanner_type_blueprint.route('/cs/scanner-types/status', methods=['GET'])
def get_scanner_status():
    return scanner_type_controller.get_status()

@scanner_type_blueprint.route('/cs/scanner-types/<scanner_id>', methods=['PUT', 'DELETE'])
def scanner(scanner_id):
    if request.method == "DELETE":
        print("Scanner Id", scanner_id)
        if scanner_id:
            return scanner_type_controller.delete_entity( scanner_id)
        return jsonify({'error': 'Missing Scanner ID'}), 400
    elif request.method == 'PUT':
        if scanner_id:
            response = scanner_type_controller.update_entity(request,scanner_id)
            return response
        return jsonify({'error': 'Missing project details for update'}), 400
    
    
@scanner_type_blueprint.route('/cs/scanner-types/scan-target-types', methods=['GET'])
@swag_from({
    'tags': ['Scanner Types'],
    'summary': 'Get available scan target types',
    'description': 'Retrieve all available target types that can be scanned (web applications, repositories, cloud infrastructure, etc.)',
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
            'description': 'Scan target types retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'type': {'type': 'string', 'example': 'web_application'},
                                'display_name': {'type': 'string', 'example': 'Web Application'},
                                'description': {'type': 'string', 'example': 'Web applications and websites'},
                                'compatible_scanners': {
                                    'type': 'array',
                                    'items': {'type': 'string'},
                                    'example': ['zap', 'wapiti']
                                }
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
def get_scan_target_types():
     return scanner_type_controller.get_scan_target_types()
    









