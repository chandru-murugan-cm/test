from flask import Blueprint, request
from controllers.RepositoryTrivy1Controller import RepositoryTrivy1Controller
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response


repository_trivy_1_blueprint = Blueprint(
    'repository_trivy_1_blueprint', __name__)
repository_trivy_1_controller = RepositoryTrivy1Controller()


@repository_trivy_1_blueprint.route('/crscan/repository_1/<repository_1_id>', methods=['GET'])
@swag_from({
    'tags': ['Repository Scans - Trivy'],
    'summary': 'Get Trivy repository scan results by ID',
    'description': 'Retrieve specific Trivy vulnerability scan results for a repository by scan ID',
    'parameters': [
        {
            'name': 'repository_1_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Repository Trivy scan ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'Trivy scan results retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'scan_id': {'type': 'string'},
                    'repository': {'type': 'string'},
                    'vulnerabilities': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'VulnerabilityID': {'type': 'string'},
                                'PkgName': {'type': 'string'},
                                'Severity': {'type': 'string'},
                                'Title': {'type': 'string'},
                                'Description': {'type': 'string'},
                                'FixedVersion': {'type': 'string'},
                                'References': {
                                    'type': 'array',
                                    'items': {'type': 'string'}
                                }
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
def get_domain_wapiti_1_by_id(repository_1_id=None):
    fields = {}
    if repository_1_id:
        fields['_id'] = repository_1_id
        return repository_trivy_1_controller.fetch_by_id(fields)
