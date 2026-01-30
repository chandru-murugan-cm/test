from flask import Blueprint, request
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response
from controllers.RefinedScanResultsController import RefinedScanResultsController


refined_scan_results_blueprint = Blueprint(
    'refined_scan_results_blueprint', __name__)
refined_scan_results_controller = RefinedScanResultsController()


@refined_scan_results_blueprint.route('/cs/refined_scan', methods=['GET', 'POST'])
@refined_scan_results_blueprint.route('/cs/refined_scan/<refined_scan_results_id>', methods=['GET', 'PUT', 'DELETE'])
@refined_scan_results_blueprint.route('/cs/refined_scan/raw_results/<unformatted_scan_results_id>', methods=['GET'])
@swag_from({
    'tags': ['Refined Scan Results'],
    'summary': 'Manage refined scan results',
    'description': 'Create, retrieve, update, and delete refined scan results. These are processed and normalized scan results from various security scanners.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'name': 'refined_scan_results_id',
            'in': 'path',
            'type': 'string',
            'required': False,
            'description': 'ID of the refined scan result'
        },
        {
            'name': 'unformatted_scan_results_id',
            'in': 'path',
            'type': 'string',
            'required': False,
            'description': 'ID of the unformatted scan result to retrieve refined data for'
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
                            'unformatted_scan_results_id': {'type': 'string', 'example': '507f1f77bcf86cd799439012'},
                            'severity': {'type': 'string', 'example': 'high'},
                            'vulnerability_type': {'type': 'string', 'example': 'SQL Injection'},
                            'description': {'type': 'string', 'example': 'SQL injection vulnerability detected'},
                            'location': {'type': 'string', 'example': '/api/login.php:line 25'},
                            'remediation': {'type': 'string', 'example': 'Use parameterized queries'},
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
def refined_scan_results(refined_scan_results_id=None, unformatted_scan_results_id=None):
    if request.method == 'POST':
        if request.data:
            return refined_scan_results_controller.add_entity(request)
        return {'error': 'Missing Unformatted Scan Results details'}, '400 Bad request'

    elif request.method == "DELETE":
        if refined_scan_results_id:
            return refined_scan_results_controller.delete_entity(refined_scan_results_id)
        return {'error': 'Missing Unformatted Scan Results ID details'}, '400 Bad request'

    elif request.method == "GET":
        fields = dict()
        if '/cs/refined_scan/raw_results' in request.path:
            if unformatted_scan_results_id:
                fields['unformatted_scan_results_id'] = request.args.get(
                    'unformatted_scan_results_id')
        if request.args.get('refined_scan_results_id') != None:
            fields['_id'] = request.args.get('refined_scan_results_id')
        else:
            fields['_id'] = refined_scan_results_id
            fields['unformatted_scan_results_id'] = unformatted_scan_results_id
        fields = {k: v for k, v in fields.items() if v is not None}
        return refined_scan_results_controller.fetch_all(request, fields)

    elif request.method == 'PUT':
        if refined_scan_results_id:
            response = refined_scan_results_controller.update_by_id(request)
            return response
        return {'error': 'Missing Refined Scan Results ID'}, '400 Bad request'
