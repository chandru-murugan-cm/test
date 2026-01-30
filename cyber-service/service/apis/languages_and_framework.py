from flask import Blueprint
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response
from controllers.LanguagesAndFrameworkController import LanguagesAndFrameWorkController

languages_and_framework_blueprint = Blueprint(
    'languages_and_framework_blueprint', __name__)
languages_and_framework_controller = LanguagesAndFrameWorkController()


@languages_and_framework_blueprint.route('/crscan/languages_and_framework/<project_id>', methods=['GET'])
@swag_from({
    'tags': ['Languages and Frameworks'],
    'summary': 'Retrieve detected languages and frameworks',
    'description': 'Fetch detected programming languages and frameworks for a specific project. This information is typically gathered during repository analysis.',
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
            'description': 'Project ID to retrieve language and framework information for'
        }
    ],
    'responses': {
        200: {
            'description': 'Languages and frameworks retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'data': {
                        'type': 'object',
                        'properties': {
                            '_id': {'type': 'string', 'example': '507f1f77bcf86cd799439011'},
                            'project_id': {'type': 'string', 'example': '507f1f77bcf86cd799439012'},
                            'languages': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'name': {'type': 'string', 'example': 'JavaScript'},
                                        'percentage': {'type': 'number', 'example': 85.5},
                                        'lines_of_code': {'type': 'integer', 'example': 12453}
                                    }
                                }
                            },
                            'frameworks': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'name': {'type': 'string', 'example': 'React'},
                                        'version': {'type': 'string', 'example': '18.2.0'},
                                        'confidence': {'type': 'number', 'example': 0.95}
                                    }
                                }
                            },
                            'detected_at': {'type': 'string', 'format': 'date-time'}
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
            'description': 'Not found - No language/framework data found for project',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def get_languages_and_framework(project_id=None):
    fields = {}
    if project_id:
        fields['project_id'] = project_id
        return languages_and_framework_controller.fetch_by_id(fields)