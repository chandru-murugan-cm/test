from flask import Blueprint, request,jsonify
from controllers.ScannersController import ScannersController
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response

scanners_blueprint = Blueprint('scanners_blueprint', __name__)
scanners_controller = ScannersController()


@scanners_blueprint.route('/cs/scanners', methods=['POST'])
@swag_from({
    'tags': ['Scanners'],
    'summary': 'Create a new security scanner configuration',
    'description': 'Add a new scanner to the system with its configuration and capabilities',
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
                    'required': ['name', 'scanner_type', 'configuration'],
                    'properties': {
                        'name': {'type': 'string', 'example': 'OWASP ZAP Scanner'},
                        'scanner_type': {'type': 'string', 'example': 'DAST'},
                        'configuration': {
                            'type': 'object',
                            'example': {'url': 'http://zap:8080', 'timeout': 300}
                        },
                        'description': {'type': 'string', 'example': 'Web application security scanner'},
                        'capabilities': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'example': ['web_scan', 'api_scan']
                        }
                    }
                }
            }
        }
    },
    'responses': {
        201: {
            'description': 'Scanner created successfully',
            'schema': success_response
        },
        400: {
            'description': 'Missing or invalid scanner details',
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
        return scanners_controller.add_entity(request)
    return {'error': 'Missing scanners details'}, 400


@scanners_blueprint.route('/cs/scanners', methods=['GET'])
@swag_from({
    'tags': ['Scanners'],
    'summary': 'Get all scanners or specific scanner by ID',
    'description': 'Retrieve list of all configured scanners or get specific scanner by providing scanner_id parameter',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'name': 'scanner_id',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Optional scanner ID to get specific scanner'
        }
    ],
    'responses': {
        200: {
            'description': 'Scanners retrieved successfully',
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
                                'name': {'type': 'string', 'example': 'OWASP ZAP Scanner'},
                                'scanner_type': {'type': 'string', 'example': 'DAST'},
                                'configuration': {'type': 'object'},
                                'status': {'type': 'string', 'example': 'active'},
                                'created_at': {'type': 'string', 'format': 'date-time'},
                                'updated_at': {'type': 'string', 'format': 'date-time'}
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
def get_scanners():
    fields = {}
    if 'scanner_id' in request.args:
        fields['_id'] = request.args['scanner_id']
    return scanners_controller.fetch_all(request, fields)


@scanners_blueprint.route('/cs/scanners/status', methods=['GET'])
@swag_from({
    'tags': ['Scanners'],
    'summary': 'Get scanner system status',
    'description': 'Check the overall status and health of all configured scanners',
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
            'description': 'Scanner status retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'total_scanners': {'type': 'integer', 'example': 5},
                            'active_scanners': {'type': 'integer', 'example': 4},
                            'inactive_scanners': {'type': 'integer', 'example': 1},
                            'scanner_status': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'name': {'type': 'string', 'example': 'OWASP ZAP'},
                                        'status': {'type': 'string', 'example': 'active'},
                                        'last_health_check': {'type': 'string', 'format': 'date-time'}
                                    }
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
def get_scanner_status():
    return scanners_controller.get_status()

@scanners_blueprint.route('/cs/scanners/<scanner_id>', methods=['PUT', 'DELETE'])
@swag_from({
    'tags': ['Scanners'],
    'summary': 'Update or delete a scanner',
    'description': 'Update scanner configuration or delete a scanner by ID',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'name': 'scanner_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'ID of the scanner to update or delete'
        }
    ],
    'requestBody': {
        'required': False,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string', 'example': 'Updated Scanner Name'},
                        'configuration': {
                            'type': 'object',
                            'example': {'url': 'http://new-zap:8080', 'timeout': 600}
                        },
                        'description': {'type': 'string', 'example': 'Updated description'},
                        'status': {'type': 'string', 'example': 'active'}
                    }
                }
            }
        }
    },
    'responses': {
        200: {
            'description': 'Scanner updated/deleted successfully',
            'schema': success_response
        },
        400: {
            'description': 'Missing or invalid scanner details',
            'schema': error_response
        },
        404: {
            'description': 'Scanner not found',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized - Invalid or missing JWT token',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def scanner(scanner_id):
    # DELETE Method
    if request.method == "DELETE":
        print("Scanner Id", scanner_id)
        if scanner_id:
            return scanners_controller.delete_scanner(scanner_id)
        return jsonify({'error': 'Missing Scanner ID'}), 400

    # PUT Method
    elif request.method == 'PUT':
        if scanner_id:
            response = scanners_controller.update_scanner(request,scanner_id)
            return response
        return jsonify({'error': 'Missing project details for update'}), 400
