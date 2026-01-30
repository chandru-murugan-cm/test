
from flask import Blueprint, request, jsonify
from controllers.ScansController import ScansController
from flasgger import swag_from
from docs.swagger.swagger_models import create_scan_request, scan_model, success_response, error_response
from dotenv import load_dotenv
import os

load_dotenv()
scheduler_key = os.getenv('SCHEDULER_SECRET_KEY')

scans_blueprint = Blueprint('scans_blueprint', __name__)
scans_controller = ScansController()


@scans_blueprint.route('/cs/scans', methods=['POST'])
@swag_from({
    'tags': ['Scans'],
    'summary': 'Create a new security scan',
    'description': 'Initiate a security scan for a project with specified scanner types',
    'requestBody': {
        'description': 'Scan configuration',
        'required': True,
        'content': {
            'application/json': {
                'schema': create_scan_request
            }
        }
    },
    'responses': {
        200: {
            'description': 'Scan created successfully',
            'schema': success_response
        },
        400: {
            'description': 'Invalid request data',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def add_scanner():
    if request.data:
        return scans_controller.add_entity(request)
    return {'error': 'Missing scans details'}, 400


@scans_blueprint.route('/cs/scans', methods=['GET'])
@swag_from({
    'tags': ['Scans'],
    'summary': 'Get scans',
    'description': 'Retrieve all scans or filter by scan ID',
    'parameters': [
        {
            'name': 'scans_id',
            'in': 'query',
            'type': 'string',
            'description': 'Filter by scan ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Scans retrieved successfully',
            'schema': {
                'allOf': [
                    success_response,
                    {
                        'properties': {
                            'data': {
                                'type': 'array',
                                'items': scan_model
                            }
                        }
                    }
                ]
            }
        }
    },
    'security': [{'Bearer': []}]
})
def get_scanners():
    fields = {}
    if 'scans_id' in request.args:
        fields['_id'] = request.args['scans_id']
    return scans_controller.fetch_all(request, fields)


@scans_blueprint.route('/cs/scans/<project_id>', methods=['GET'])
def get_scans_by_project_id(project_id=None):
    fields = {}
    if project_id:
        fields['project_id'] = project_id
        return scans_controller.fetch_by_project_id(fields)
    
@scans_blueprint.route('/cs/run_scheduled_scan', methods=['POST'])
def run_scheduled_scan():
    # Validate the secret header
    scheduler_secret = request.headers.get('X-Scheduler-Secret')
    if scheduler_secret != scheduler_key:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    # data = {}
    print("###############", data)
    scan_request_json = {
        "scheduler_secret": scheduler_secret,
        "scheduler_response": data,
        "scan_status":"scheduled"
    }
    return scans_controller.add_entity(scan_request_json)
