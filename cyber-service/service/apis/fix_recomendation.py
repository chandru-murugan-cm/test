from flask import Blueprint, request
from controllers.FixRecomendationController import FixRecomendationController
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response


fix_recomendation_blueprint = Blueprint(
    'fix_recomendation_blueprint', __name__)
fix_recomendation_controller = FixRecomendationController()


@fix_recomendation_blueprint.route('/crscan/finding_master/fix/<fix_id>', methods=['GET'])
@swag_from({
    'tags': ['Fix Recommendations'],
    'summary': 'Get fix recommendation by ID',
    'description': 'Retrieve specific fix recommendation details for a security finding',
    'parameters': [
        {
            'name': 'fix_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Fix recommendation ID'
        }
    ],
    'responses': {
        '200': {
            'description': 'Fix recommendation retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'fix_id': {'type': 'string'},
                    'finding_id': {'type': 'string'},
                    'vulnerability_type': {'type': 'string'},
                    'severity': {'type': 'string'},
                    'recommendation': {'type': 'string'},
                    'code_example': {'type': 'string'},
                    'references': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    },
                    'priority': {'type': 'string'},
                    'effort_estimate': {'type': 'string'},
                    'created_date': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        '404': {
            'description': 'Fix recommendation not found',
            'schema': error_response
        }
    }
})
def get_domain_wapiti_1_by_id(fix_id=None):
    fields = {}
    if fix_id:
        fields['_id'] = fix_id
        return fix_recomendation_controller.fetch_by_id(fields)

