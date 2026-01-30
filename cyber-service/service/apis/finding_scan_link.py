from flask import Blueprint, request
from controllers.FindingScanLinkController import FindingScanLinkController
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response


finding_scan_link_blueprint = Blueprint(
    'finding_scan_link_blueprint', __name__)
finding_scan_link_controller = FindingScanLinkController()


@finding_scan_link_blueprint.route('/crscan/finding_scan_link', methods=['POST'])
@swag_from({
    'tags': ['Finding Scan Links'],
    'summary': 'Create finding-scan link',
    'description': 'Create a link between a security finding and its originating scan',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'finding_id': {'type': 'string', 'description': 'ID of the security finding'},
                    'scan_id': {'type': 'string', 'description': 'ID of the originating scan'},
                    'scanner_type': {'type': 'string', 'description': 'Type of scanner that found the issue'},
                    'confidence_level': {'type': 'string', 'description': 'Confidence level of the finding'}
                },
                'required': ['finding_id', 'scan_id']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Finding-scan link created successfully',
            'schema': success_response
        },
        '400': {
            'description': 'Invalid input data',
            'schema': error_response
        }
    }
})
def add_finding_scan_link():
    if request.data:
        return finding_scan_link_controller.add_entity(request)
    return {'error': 'Missing Finding Scan Link details'}, 400


@finding_scan_link_blueprint.route('/crscan/finding_scan_link', methods=['GET'])
@swag_from({
    'tags': ['Finding Scan Links'],
    'summary': 'Get finding-scan links',
    'description': 'Retrieve finding-scan link relationships with optional filtering',
    'parameters': [
        {
            'name': 'finding_scan_link_id',
            'in': 'query',
            'type': 'string',
            'description': 'Filter by specific finding-scan link ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'Finding-scan links retrieved successfully',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'link_id': {'type': 'string'},
                        'finding_id': {'type': 'string'},
                        'scan_id': {'type': 'string'},
                        'scanner_type': {'type': 'string'},
                        'confidence_level': {'type': 'string'},
                        'created_date': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        }
    }
})
def get_finding_scan_link():
    fields = {}
    if 'finding_scan_link_id' in request.args:
        fields['_id'] = request.args.get('finding_scan_link_id')
    return finding_scan_link_controller.fetch_all(request, fields)
