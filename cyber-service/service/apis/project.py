from flask import Blueprint, request
from controllers.ProjectController import ProjectController
from flasgger import swag_from
from docs.swagger.swagger_models import project_model, success_response, error_response


project_blueprint = Blueprint('project_blueprint', __name__)
project_controller = ProjectController()


@project_blueprint.route('/crscan/project', methods=['GET', 'POST'])
@project_blueprint.route('/crscan/project/<project_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from({
    'tags': ['Projects'],
    'summary': 'Project management operations',
    'description': 'Create, read, update, or delete projects',
    'parameters': [
        {
            'name': 'project_id',
            'in': 'path',
            'type': 'string',
            'description': 'Project ID (for GET, PUT, DELETE)'
        },
        {
            'name': 'name',
            'in': 'query',
            'type': 'string',
            'description': 'Filter by project name (for GET)'
        }
    ],
    'requestBody': {
        'description': 'Project data (for POST, PUT)',
        'content': {
            'application/json': {
                'schema': project_model
            }
        }
    },
    'responses': {
        200: {
            'description': 'Success',
            'schema': success_response
        },
        400: {
            'description': 'Bad Request',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def project(project_id=None, name=None):
    if request.method == "POST":
        if request.data:
            return project_controller.add_entity(request)
        return {'error': 'Missing Project details'}, '400 Bad request'

    elif request.method == "DELETE":
        if project_id:
            return project_controller.remove_entity(project_id)
        return {'error': 'Missing Project ID details'}, '400 Bad request'

    elif request.method == "GET":
        fields = dict()
        if request.args.get('project_id') != None:
            fields['_id'] = request.args.get('project_id')
            if request.args.get('name') != None:
                fields['name'] = request.args.get('name')
        else:
            fields['_id'] = project_id
            fields['name'] = name
        fields = {k: v for k, v in fields.items() if v is not None}
        return project_controller.fetch_all(request, fields)

    elif request.method == 'PUT':
        if project_id:
            response = project_controller.update_by_id(request)
            return response
        return {'error': 'Missing Intervention ID'}, '400 Bad request'
