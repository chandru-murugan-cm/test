from flask import Blueprint, request
from controllers.DomainController import DomainController
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response

domain_blueprint = Blueprint('domain_blueprint', __name__)
domain_controller = DomainController()

@domain_blueprint.route('/crscan/domain', methods=['GET', 'POST'])
@domain_blueprint.route('/crscan/domain/<target_domain_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from({
    'tags': ['Targets'],
    'summary': 'Manage domain scan targets',
    'description': 'Create, read, update, or delete domain targets for web application security scanning',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'name': 'target_domain_id',
            'in': 'path',
            'type': 'string',
            'required': False,
            'description': 'ID of the domain target (required for PUT/DELETE operations)'
        },
        {
            'name': 'project_id',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter domains by project ID'
        },
        {
            'name': 'domain_url',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter by specific domain URL'
        }
    ],
    'requestBody': {
        'required': False,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'required': ['project_id', 'domain_url'],
                    'properties': {
                        'project_id': {'type': 'string', 'example': '507f1f77bcf86cd799439011'},
                        'domain_url': {'type': 'string', 'example': 'https://example.com', 'format': 'uri'},
                        'name': {'type': 'string', 'example': 'Production Website'},
                        'description': {'type': 'string', 'example': 'Main company website for security testing'},
                        'scan_config': {
                            'type': 'object',
                            'properties': {
                                'authentication': {
                                    'type': 'object',
                                    'properties': {
                                        'type': {'type': 'string', 'example': 'basic', 'enum': ['none', 'basic', 'form', 'oauth']},
                                        'username': {'type': 'string', 'example': 'testuser'},
                                        'password': {'type': 'string', 'example': 'testpass123'}
                                    }
                                },
                                'exclude_paths': {
                                    'type': 'array',
                                    'items': {'type': 'string'},
                                    'example': ['/admin', '/logout']
                                },
                                'max_depth': {'type': 'integer', 'example': 5, 'minimum': 1, 'maximum': 10}
                            }
                        },
                        'tags': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'example': ['production', 'web-app']
                        }
                    }
                }
            }
        }
    },
    'responses': {
        200: {
            'description': 'Operation completed successfully',
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
                                'domain_url': {'type': 'string', 'example': 'https://example.com'},
                                'name': {'type': 'string', 'example': 'Production Website'},
                                'scan_config': {'type': 'object'},
                                'last_scanned': {'type': 'string', 'format': 'date-time'},
                                'scan_status': {'type': 'string', 'example': 'ready', 'enum': ['ready', 'scanning', 'completed', 'failed']},
                                'created_at': {'type': 'string', 'format': 'date-time'},
                                'updated_at': {'type': 'string', 'format': 'date-time'}
                            }
                        }
                    }
                }
            }
        },
        201: {
            'description': 'Domain target created successfully',
            'schema': success_response
        },
        400: {
            'description': 'Missing or invalid request data',
            'schema': error_response
        },
        404: {
            'description': 'Domain target not found',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized - Invalid or missing JWT token',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def domain(target_domain_id=None):
    if request.method == "POST":
        if request.data:
            return domain_controller.add_entity(request)
        return {'error': 'Missing Domain details'}, 400

    elif request.method == "DELETE":
        if target_domain_id:
            return domain_controller.delete_by_id(target_domain_id)
        return {'error': 'Missing Domain ID details'}, 400

    elif request.method == "GET":
        fields = {}
        if request.args.get('target_domain_id') is not None:
            fields['target_domain_id'] = request.args.get('target_domain_id')
        if request.args.get('project_id') is not None:
            fields['project_id'] = request.args.get('project_id')
        if request.args.get('domain_url') is not None:
            fields['domain_url'] = request.args.get('domain_url')

        fields = {k: v for k, v in fields.items() if v is not None}
        return domain_controller.fetch_all(request, fields)

    elif request.method == 'PUT':
        if target_domain_id:
            return domain_controller.update_by_id(request, target_domain_id)
        return {'error': 'Missing Domain ID'}, 400
