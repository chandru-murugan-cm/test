
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response
from controllers.cloud.AzureController import AzureController
from dotenv import load_dotenv
import os


target_azure_cloud_blueprint = Blueprint('target_azure_cloud_blueprint', __name__)
target_azure_controller = AzureController()

@target_azure_cloud_blueprint.route('/crscan/cloud/azure', methods=['POST'])
@swag_from({
    'tags': ['Azure Cloud Security'],
    'summary': 'Add Azure cloud configuration',
    'description': 'Create a new Azure cloud security configuration for scanning Azure resources and services.',
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
                'required': ['project_id', 'subscription_id', 'tenant_id'],
                'properties': {
                    'project_id': {'type': 'string', 'example': '507f1f77bcf86cd799439012'},
                    'subscription_id': {'type': 'string', 'example': 'f47ac10b-58cc-4372-a567-0e02b2c3d479'},
                    'tenant_id': {'type': 'string', 'example': 'f47ac10b-58cc-4372-a567-0e02b2c3d480'},
                    'client_id': {'type': 'string', 'example': 'f47ac10b-58cc-4372-a567-0e02b2c3d481'},
                    'client_secret': {'type': 'string', 'example': 'secret123'},
                    'resource_group': {'type': 'string', 'example': 'my-resource-group'},
                    'scan_type': {'type': 'string', 'example': 'security_center'},
                    'description': {'type': 'string', 'example': 'Azure security scan configuration'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Azure cloud configuration created successfully',
            'schema': success_response
        },
        400: {
            'description': 'Bad request - Missing Azure cloud details',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized - Invalid or missing token',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def add_azure_config():
    """
    API to add Azure cloud configuration.
    """
    if request.data:
        return target_azure_controller.add_entity(request)
    return {'error': 'Missing Azure cloud details'}, 400

@target_azure_cloud_blueprint.route('/crscan/cloud/azure', methods=['GET'])
@swag_from({
    'tags': ['Azure Cloud Security'],
    'summary': 'Retrieve Azure cloud configurations',
    'description': 'Fetch all Azure cloud security configurations or filter by scan ID.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'name': 'scans_id',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Specific scan ID to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'Azure cloud configurations retrieved successfully',
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
                                'project_id': {'type': 'string', 'example': '507f1f77bcf86cd799439012'},
                                'subscription_id': {'type': 'string', 'example': 'f47ac10b-58cc-4372-a567-0e02b2c3d479'},
                                'resource_group': {'type': 'string', 'example': 'my-resource-group'},
                                'scan_type': {'type': 'string', 'example': 'security_center'},
                                'status': {'type': 'string', 'example': 'active'},
                                'created_at': {'type': 'string', 'format': 'date-time'}
                            }
                        }
                    }
                }
            }
        },
        401: {
            'description': 'Unauthorized - Invalid or missing token',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def get_target_azure_details():
    """
    API to fetch all Azure cloud scans.
    """
    fields = {}
    if 'scans_id' in request.args:
        fields['_id'] = request.args['scans_id']
    return target_azure_controller.fetch_all(fields)

@target_azure_cloud_blueprint.route('/crscan/cloud/azure/<project_id>', methods=['GET'])
def get_scans_by_project_id(project_id=None):
    """
    API to fetch Azure scans by project ID.
    """
    fields = {}
    if project_id:
        fields['project_id'] = project_id
        return target_azure_controller.fetch_by_project_id(fields)
    return {'error': 'Project ID not provided'}, 400

@target_azure_cloud_blueprint.route('/crscan/cloud/azure/name/<name>', methods=['GET'])
def get_scans_by_name(name):
    """
    API to fetch Azure scans by name.
    """
    return target_azure_controller.fetch_by_name(name)

@target_azure_cloud_blueprint.route('/crscan/cloud/azure/<azure_id>', methods=['DELETE'])
def delete_azure_scan_by_id(azure_id):
    """
    API to delete an Azure scan by its azure_id.
    """
    return target_azure_controller.delete_by_id(azure_id)