from flask import Blueprint, request
from controllers.DomainZap1Controller import DomainZap1Controller
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response


domain_zap_1_blueprint = Blueprint(
    'domain_zap_1_blueprint', __name__)
domain_zap_1_controller = DomainZap1Controller()


@domain_zap_1_blueprint.route('/crscan/domain_1/<domain_1_id>', methods=['GET'])
@swag_from({
    'tags': ['Domain Scans - ZAP'],
    'summary': 'Get OWASP ZAP domain scan results by ID',
    'description': 'Retrieve specific OWASP ZAP web vulnerability scan results for a domain by scan ID',
    'parameters': [
        {
            'name': 'domain_1_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Domain ZAP scan ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'ZAP scan results retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'scan_id': {'type': 'string'},
                    'domain': {'type': 'string'},
                    'alerts': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'alertRef': {'type': 'string'},
                                'name': {'type': 'string'},
                                'riskdesc': {'type': 'string'},
                                'confidence': {'type': 'string'},
                                'url': {'type': 'string'},
                                'description': {'type': 'string'},
                                'solution': {'type': 'string'}
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
def get_domain_zap_1_by_id(domain_1_id=None):
    fields = {}
    if domain_1_id:
        fields['_id'] = domain_1_id
        return domain_zap_1_controller.fetch_by_id(fields)
