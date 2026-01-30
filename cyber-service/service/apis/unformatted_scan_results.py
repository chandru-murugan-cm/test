from flask import Blueprint, request
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response
from controllers.UnformattedScanResultsController import UnformattedScanResultsController

unformatted_scan_results_blueprint = Blueprint(
    'unformatted_scan_results_blueprint', __name__)
unformatted_scan_results_controller = UnformattedScanResultsController()


@unformatted_scan_results_blueprint.route('/cs/unformatted_scan', methods=['GET', 'POST'])
@unformatted_scan_results_blueprint.route('/cs/unformatted_scan/project/<project_id>', methods=['GET'])
@unformatted_scan_results_blueprint.route('/cs/unformatted_scan/refined_result/<project_id>', methods=['GET'])
@unformatted_scan_results_blueprint.route('/cs/unformatted_scan/unformatted_result/<unformatted_scan_id>', methods=['GET'])
@unformatted_scan_results_blueprint.route('/cs/unformatted_scan/<unformatted_scan_id>', methods=['GET', 'PUT', 'DELETE'])
@unformatted_scan_results_blueprint.route('/cs/unformatted_scan/scheduler/<scheduler_id>', methods=['GET'])
@unformatted_scan_results_blueprint.route('/cs/unformatted_scan/dashboard_content/<project_id>', methods=['GET'])
@swag_from({
    'tags': ['Unformatted Scan Results'],
    'summary': 'Manage unformatted scan results',
    'description': 'Comprehensive endpoint for creating, retrieving, updating, and deleting unformatted scan results. Supports various filters and specialized endpoints for different use cases.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'name': 'unformatted_scan_id',
            'in': 'path',
            'type': 'string',
            'required': False,
            'description': 'ID of the unformatted scan result'
        },
        {
            'name': 'scheduler_id',
            'in': 'path',
            'type': 'string',
            'required': False,
            'description': 'ID of the scheduler'
        },
        {
            'name': 'project_id',
            'in': 'path',
            'type': 'string',
            'required': False,
            'description': 'ID of the project'
        }
    ],
    'responses': {
        200: {
            'description': 'Operation successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'data': {
                        'type': 'object',
                        'properties': {
                            '_id': {'type': 'string', 'example': '507f1f77bcf86cd799439011'},
                            'project_id': {'type': 'string', 'example': '507f1f77bcf86cd799439012'},
                            'scanner_type': {'type': 'string', 'example': 'SAST'},
                            'scan_results': {'type': 'object', 'example': {}},
                            'status': {'type': 'string', 'example': 'completed'},
                            'created_at': {'type': 'string', 'format': 'date-time'}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request - Missing required details',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized - Invalid or missing token',
            'schema': error_response
        },
        404: {
            'description': 'Not found - Resource not found',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def unformatted_scan_results(unformatted_scan_id=None, scheduler_id=None, project_id=None):
    if request.method == "POST":
        if request.data:
            return unformatted_scan_results_controller.add_entity(request)
        return {'error': 'Missing Unformatted Scan Results details'}, '400 Bad request'

    elif request.method == "DELETE":
        if unformatted_scan_id:
            return unformatted_scan_results_controller.delete_entity(unformatted_scan_id)
        return {'error': 'Missing Unformatted Scan Results ID details'}, '400 Bad request'

    elif request.method == "GET":
        fields = dict()
        if '/cs/unformatted_scan/dashboard_content' in request.path:
            if project_id:
                fields['project_id'] = project_id
                return unformatted_scan_results_controller.fetch_dashboard_content(request, fields)
        if '/cs/unformatted_scan/scheduler' in request.path:
            if scheduler_id:
                fields['scheduler_id'] = scheduler_id
        if '/cs/unformatted_scan/project' in request.path:
            # Details for loading scans UI page
            project_id = request.args.get('project_id')
            if project_id:
                fields['project_id'] = project_id
                return unformatted_scan_results_controller.fetch_scanner_details(fields)
        if '/cs/unformatted_scan/unformatted_result' in request.path:
            # Details for loading Findings UI page re-routing from scans UI with unformatted_scan_id
            unformatted_scan_id = request.args.get('unformatted_scan_id')
            if unformatted_scan_id:
                fields['unformatted_scan_id'] = unformatted_scan_id
                return unformatted_scan_results_controller.fetch_refined_scan_results_for_unformatted_id(fields)
        if '/cs/unformatted_scan/refined_result' in request.path:
            # Details for loading Findings UI page with project_id
            project_id = request.args.get('project_id')
            if project_id:
                fields['project_id'] = project_id
                return unformatted_scan_results_controller.fetch_refined_scan_results_by_project_id(fields)
        if unformatted_scan_id is not None:
            fields['_id'] = unformatted_scan_id
        else:
            fields['scheduler_id'] = scheduler_id
        fields = {k: v for k, v in fields.items() if v is not None}
        return unformatted_scan_results_controller.fetch_all(request, fields)

    elif request.method == 'PUT':
        if unformatted_scan_id:
            response = unformatted_scan_results_controller.update_by_id(
                request)
            return response
        return {'error': 'Missing Unformatted Scan Results ID'}, '400 Bad request'
