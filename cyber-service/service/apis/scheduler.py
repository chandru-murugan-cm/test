from flask import Blueprint, request
from controllers.SchedulerController import SchedulerController
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response


scheduler_blueprint = Blueprint('scheduler_blueprint', __name__)
scheduler_controller = SchedulerController()


@scheduler_blueprint.route('/cs/scheduler', methods=['GET', 'POST'])
@scheduler_blueprint.route('/cs/scheduler/<scheduler_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from({
    'tags': ['Scheduler'],
    'summary': 'Manage scan schedules',
    'description': 'Create, read, update, or delete scan schedules for automated security assessments',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'name': 'scheduler_id',
            'in': 'path',
            'type': 'string',
            'required': False,
            'description': 'ID of the scheduler (required for PUT/DELETE operations)'
        },
        {
            'name': 'project_id',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter schedules by project ID'
        },
        {
            'name': 'name',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Filter schedules by name'
        }
    ],
    'requestBody': {
        'required': False,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'required': ['name', 'project_id', 'schedule_config'],
                    'properties': {
                        'name': {'type': 'string', 'example': 'Weekly Security Scan'},
                        'project_id': {'type': 'string', 'example': '507f1f77bcf86cd799439011'},
                        'schedule_config': {
                            'type': 'object',
                            'required': ['frequency', 'time'],
                            'properties': {
                                'frequency': {'type': 'string', 'example': 'weekly', 'enum': ['daily', 'weekly', 'monthly']},
                                'time': {'type': 'string', 'example': '02:00', 'description': 'Time in HH:MM format'},
                                'day_of_week': {'type': 'integer', 'example': 1, 'description': 'Day of week (0=Sunday, 6=Saturday)'}
                            }
                        },
                        'scanner_types': {
                            'type': 'array',
                            'items': {'type': 'string'},
                            'example': ['zap', 'trivy']
                        },
                        'enabled': {'type': 'boolean', 'example': True},
                        'description': {'type': 'string', 'example': 'Automated weekly security assessment'}
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
                                'name': {'type': 'string', 'example': 'Weekly Security Scan'},
                                'project_id': {'type': 'string'},
                                'schedule_config': {'type': 'object'},
                                'enabled': {'type': 'boolean'},
                                'next_run': {'type': 'string', 'format': 'date-time'},
                                'created_at': {'type': 'string', 'format': 'date-time'}
                            }
                        }
                    }
                }
            }
        },
        201: {
            'description': 'Schedule created successfully',
            'schema': success_response
        },
        400: {
            'description': 'Missing or invalid request data',
            'schema': error_response
        },
        404: {
            'description': 'Schedule not found',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized - Invalid or missing JWT token',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def scheduler(scheduler_id=None, project_id=None):
    if request.method == "POST":
        if request.data:
            return scheduler_controller.add_entity(request)
        return {'error': 'Missing Scheduler details'}, '400 Bad request'

    elif request.method == "DELETE":
        if scheduler_id:
            return scheduler_controller.remove_entity(scheduler_id)
        return {'error': 'Missing Scheduler ID details'}, '400 Bad request'

    elif request.method == "GET":
        fields = dict()
        if request.args.get('project_id') != None:
            fields['project_id'] = request.args.get('project_id')
            if request.args.get('name') != None:
                fields['name'] = request.args.get('name')
        else:
            fields['project_id'] = project_id
        fields = {k: v for k, v in fields.items() if v is not None}
        return scheduler_controller.fetch_schedules(request, fields)

    elif request.method == 'PUT':
        if scheduler_id:
            response = scheduler_controller.update_by_id(request)
            return response
        return {'error': 'Missing Intervention ID'}, '400 Bad request'
    

 
