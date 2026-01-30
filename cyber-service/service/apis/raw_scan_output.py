
from flask import Blueprint, request
from controllers.RawScanOutputController import RawScanOutputController
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response


raw_scan_output_blueprint = Blueprint('raw_scan_output_blueprint', __name__)
raw_scan_output_controller = RawScanOutputController()


@raw_scan_output_blueprint.route('/cs/rawscanoutput', methods=['POST'])
@swag_from({
    'tags': ['Raw Scan Output'],
    'summary': 'Store raw scan output',
    'description': 'Store raw, unprocessed output from security scanners for archival and debugging purposes',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'scan_id': {'type': 'string', 'description': 'ID of the associated scan'},
                    'scanner_type': {'type': 'string', 'description': 'Type of scanner that generated the output'},
                    'raw_output': {'type': 'string', 'description': 'Raw scanner output data'},
                    'output_format': {'type': 'string', 'description': 'Format of the raw output (JSON, XML, text, etc.)'},
                    'scan_date': {'type': 'string', 'format': 'date-time', 'description': 'When the scan was performed'}
                },
                'required': ['scan_id', 'scanner_type', 'raw_output']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Raw scan output stored successfully',
            'schema': success_response
        },
        '400': {
            'description': 'Invalid input data',
            'schema': error_response
        }
    }
})
def add_raw_scan_output():
    if request.data:
        return raw_scan_output_controller.add_entity(request)
    return {'error': 'Missing scans details'}, 400


@raw_scan_output_blueprint.route('/cs/rawscanoutput', methods=['GET'])
@swag_from({
    'tags': ['Raw Scan Output'],
    'summary': 'Get raw scan output',
    'description': 'Retrieve raw scan output data with optional filtering by output ID',
    'parameters': [
        {
            'name': 'raw_scan_output_id',
            'in': 'query',
            'type': 'string',
            'description': 'Filter by specific raw scan output ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'Raw scan output retrieved successfully',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'output_id': {'type': 'string'},
                        'scan_id': {'type': 'string'},
                        'scanner_type': {'type': 'string'},
                        'raw_output': {'type': 'string'},
                        'output_format': {'type': 'string'},
                        'scan_date': {'type': 'string', 'format': 'date-time'},
                        'file_size': {'type': 'integer'},
                        'created_date': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        }
    }
})
def get_raw_scan_output():
    fields = {}
    if 'raw_scan_output_id' in request.args:
        fields['_id'] = request.args['raw_scan_output_id']
    return raw_scan_output_controller.fetch_all(request, fields)
