
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response
from controllers.cloud.GoogleController import GoogleController
from dotenv import load_dotenv
import os


target_google_cloud_blueprint = Blueprint('target_google_cloud_blueprint', __name__)
target_google_controller = GoogleController()

@target_google_cloud_blueprint.route('/crscan/cloud/google', methods=['POST'])
@swag_from({
    'tags': ['Google Cloud Security'],
    'summary': 'Add Google Cloud configuration',
    'description': 'Create a new Google Cloud Platform security configuration for scanning GCP resources and services.',
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
                'required': ['project_id', 'gcp_project_id', 'service_account_key'],
                'properties': {
                    'project_id': {'type': 'string', 'example': '507f1f77bcf86cd799439012'},
                    'gcp_project_id': {'type': 'string', 'example': 'my-gcp-project-123'},
                    'service_account_key': {'type': 'string', 'example': 'base64-encoded-key'},
                    'region': {'type': 'string', 'example': 'us-central1'},
                    'zone': {'type': 'string', 'example': 'us-central1-a'},
                    'scan_type': {'type': 'string', 'example': 'security_command_center'},
                    'description': {'type': 'string', 'example': 'GCP security scan configuration'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Google Cloud configuration created successfully',
            'schema': success_response
        },
        400: {
            'description': 'Bad request - Missing Google Cloud details',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized - Invalid or missing token',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def add_google_config():
    """
    API to add Google cloud configuration.
    """
    if request.data:
        return target_google_controller.add_entity(request)
    return {'error': 'Missing Google cloud details'}, 400

@target_google_cloud_blueprint.route('/crscan/cloud/google', methods=['GET'])
def get_target_google_details():
    """
    API to fetch all Google cloud scans.
    """
    fields = {}
    if 'scans_id' in request.args:
        fields['_id'] = request.args['scans_id']
    return target_google_controller.fetch_all(fields)

@target_google_cloud_blueprint.route('/crscan/cloud/google/<project_id>', methods=['GET'])
def get_scans_by_project_id(project_id=None):
    """
    API to fetch Google scans by project ID.
    """
    fields = {}
    if project_id:
        fields['project_id'] = project_id
        return target_google_controller.fetch_by_project_id(fields)
    return {'error': 'Project ID not provided'}, 400

@target_google_cloud_blueprint.route('/crscan/cloud/google/name/<name>', methods=['GET'])
def get_scans_by_name(name):
    """
    API to fetch Google scans by name.
    """
    return target_google_controller.fetch_by_name(name)

@target_google_cloud_blueprint.route('/crscan/cloud/google/<google_id>', methods=['DELETE'])
def delete_google_scan_by_id(google_id):
    """
    API to delete an Google scan by its google_id.
    """
    return target_google_controller.delete_by_id(google_id)