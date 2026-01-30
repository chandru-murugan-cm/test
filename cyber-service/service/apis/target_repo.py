from flask import Blueprint, request
from controllers.RepositoryController import RepositoryController
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response


repository_blueprint = Blueprint('repository_blueprint', __name__)
repository_controller = RepositoryController()


@repository_blueprint.route('/crscan/repository', methods=['GET', 'POST'])
@repository_blueprint.route('/crscan/repository/<target_repository_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from({
    'tags': ['Targets'],
    'summary': 'Manage repository scan targets',
    'description': 'Create, read, update, or delete repository targets for source code security scanning (SAST/SCA)',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'name': 'target_repository_id',
            'in': 'path',
            'type': 'string',
            'required': False,
            'description': 'ID of the repository target (required for PUT/DELETE operations)'
        },
        {
            'name': 'project_id',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter repositories by project ID'
        },
        {
            'name': 'repository_url',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter by specific repository URL'
        }
    ],
    'requestBody': {
        'required': False,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'required': ['project_id', 'repository_url'],
                    'properties': {
                        'project_id': {'type': 'string', 'example': '507f1f77bcf86cd799439011'},
                        'repository_url': {'type': 'string', 'example': 'https://github.com/username/project.git', 'format': 'uri'},
                        'name': {'type': 'string', 'example': 'Main Application Repository'},
                        'description': {'type': 'string', 'example': 'Primary application source code for security analysis'},
                        'branch': {'type': 'string', 'example': 'main', 'default': 'main'},
                        'access_token': {'type': 'string', 'example': 'ghp_1234567890abcdef', 'description': 'GitHub/GitLab access token for private repos'},
                        'scan_config': {
                            'type': 'object',
                            'properties': {
                                'include_paths': {
                                    'type': 'array',
                                    'items': {'type': 'string'},
                                    'example': ['src/', 'lib/'],
                                    'description': 'Paths to include in scan'
                                },
                                'exclude_paths': {
                                    'type': 'array',
                                    'items': {'type': 'string'},
                                    'example': ['node_modules/', 'test/', '*.min.js'],
                                    'description': 'Paths to exclude from scan'
                                },
                                'languages': {
                                    'type': 'array',
                                    'items': {'type': 'string'},
                                    'example': ['javascript', 'python', 'solidity'],
                                    'description': 'Programming languages to scan'
                                },
                                'scan_secrets': {'type': 'boolean', 'example': True, 'default': True},
                                'scan_dependencies': {'type': 'boolean', 'example': True, 'default': True},
                                'scan_licenses': {'type': 'boolean', 'example': True, 'default': False}
                            }
                        },
                        'repository_type': {'type': 'string', 'example': 'github', 'enum': ['github', 'gitlab', 'bitbucket', 'generic']},
                        'tags': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'example': ['frontend', 'nodejs', 'production']
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
                                'repository_url': {'type': 'string', 'example': 'https://github.com/username/project.git'},
                                'name': {'type': 'string', 'example': 'Main Application Repository'},
                                'branch': {'type': 'string', 'example': 'main'},
                                'repository_type': {'type': 'string', 'example': 'github'},
                                'scan_config': {'type': 'object'},
                                'last_scanned': {'type': 'string', 'format': 'date-time'},
                                'scan_status': {'type': 'string', 'example': 'ready', 'enum': ['ready', 'cloning', 'scanning', 'completed', 'failed']},
                                'languages_detected': {
                                    'type': 'array',
                                    'items': {'type': 'string'},
                                    'example': ['javascript', 'python']
                                },
                                'created_at': {'type': 'string', 'format': 'date-time'},
                                'updated_at': {'type': 'string', 'format': 'date-time'}
                            }
                        }
                    }
                }
            }
        },
        201: {
            'description': 'Repository target created successfully',
            'schema': success_response
        },
        400: {
            'description': 'Missing or invalid request data',
            'schema': error_response
        },
        404: {
            'description': 'Repository target not found',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized - Invalid or missing JWT token',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def repository(target_repository_id=None):
    if request.method == "POST":
        if request.data:
            return repository_controller.add_entity(request)
        return {'error': 'Missing Repository details'}, 400

    elif request.method == "DELETE":
        if target_repository_id:
            return repository_controller.delete_by_id(target_repository_id)
        return {'error': 'Missing Repository ID details'}, 400

    elif request.method == "GET":
        fields = {}
        if request.args.get('target_repository_id') is not None:
            fields['target_repository_id'] = request.args.get('target_repository_id')
        if request.args.get('project_id') is not None:
            fields['project_id'] = request.args.get('project_id')
        if request.args.get('repository_url') is not None:
            fields['repository_url'] = request.args.get('repository_url')

        fields = {k: v for k, v in fields.items() if v is not None}
        return repository_controller.fetch_all(request, fields)

    elif request.method == 'PUT':
        if target_repository_id:
            return repository_controller.update_by_id(request, target_repository_id)
        return {'error': 'Missing Repository ID'}, 400