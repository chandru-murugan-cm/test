from flask import Blueprint, request
from controllers.DomainWapiti1Controller import DomainWapiti1Controller
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response


domain_wapiti_1_blueprint = Blueprint(
    'domain_wapiti_1_blueprint', __name__)
domain_wapiti_1_controller = DomainWapiti1Controller()


@domain_wapiti_1_blueprint.route('/crscan/domain_2/<domain_2_id>', methods=['GET'])
@swag_from({
    'tags': ['Domain Scans - Wapiti'],
    'summary': 'Get Wapiti domain scan results by ID',
    'description': 'Retrieve specific Wapiti web vulnerability scan results for a domain by scan ID',
    'parameters': [
        {
            'name': 'domain_2_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Domain Wapiti scan ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'Wapiti scan results retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'scan_id': {'type': 'string'},
                    'domain': {'type': 'string'},
                    'vulnerabilities': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'type': {'type': 'string'},
                                'severity': {'type': 'string'},
                                'url': {'type': 'string'},
                                'description': {'type': 'string'}
                            }
                        }
                    },
                    'scan_date': {'type': 'string', 'format': 'date-time'},
                    'status': {'type': 'string'}
                }
            }
        },
        '404': {
            'description': 'Scan not found',
            'schema': error_response
        }
    }
})
def get_domain_wapiti_1_by_id(domain_2_id=None):
    fields = {}
    if domain_2_id:
        fields['_id'] = domain_2_id
        return domain_wapiti_1_controller.fetch_by_id(fields)
