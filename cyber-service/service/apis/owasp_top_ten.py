from flask import request, Blueprint
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response
from controllers.OwaspTopTenController import OwaspTopTenController

owasp_top_ten_blueprint = Blueprint('owasp_top_ten_blueprint', __name__)
owasp_top_ten_controller = OwaspTopTenController()

@owasp_top_ten_blueprint.route('/crscan/owasp_top_ten', methods=['GET'])
@swag_from({
    'tags': ['OWASP Top 10'],
    'summary': 'Retrieve OWASP Top 10 records',
    'description': 'Fetch OWASP Top 10 security risk records by ID or retrieve all records. OWASP Top 10 represents the most critical security risks to web applications.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'name': 'owasp_top_ten_id',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Specific OWASP Top 10 record ID to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'OWASP Top 10 records retrieved successfully',
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
                                'rank': {'type': 'integer', 'example': 1},
                                'category': {'type': 'string', 'example': 'A01:2021 – Broken Access Control'},
                                'description': {'type': 'string', 'example': 'Restrictions on what authenticated users are allowed to do are often not properly enforced'},
                                'risk_level': {'type': 'string', 'example': 'High'},
                                'year': {'type': 'string', 'example': '2021'},
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
        },
        404: {
            'description': 'Not found - No OWASP Top 10 records found',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def get_owasp_top_ten():
    """
    Fetch all OwaspTopTen records or a specific record by ID.
    """
    owasp_top_ten_id = request.args.get('owasp_top_ten_id')
    if owasp_top_ten_id:
        return owasp_top_ten_controller.fetch_by_id(owasp_top_ten_id)
    return owasp_top_ten_controller.fetch_all()

@owasp_top_ten_blueprint.route('/crscan/owasp_top_ten', methods=['POST'])
@swag_from({
    'tags': ['OWASP Top 10'],
    'summary': 'Create OWASP Top 10 record',
    'description': 'Create a new OWASP Top 10 security risk record with category, description, and risk level information.',
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
                'required': ['rank', 'category', 'description', 'risk_level'],
                'properties': {
                    'rank': {'type': 'integer', 'example': 1},
                    'category': {'type': 'string', 'example': 'A01:2021 – Broken Access Control'},
                    'description': {'type': 'string', 'example': 'Restrictions on what authenticated users are allowed to do are often not properly enforced'},
                    'risk_level': {'type': 'string', 'example': 'High'},
                    'year': {'type': 'string', 'example': '2021'},
                    'mitigation': {'type': 'string', 'example': 'Implement proper access controls and authorization mechanisms'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'OWASP Top 10 record created successfully',
            'schema': success_response
        },
        400: {
            'description': 'Bad request - Missing OWASP Top 10 details',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized - Invalid or missing token',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def create_owasp_top_ten():
    """
    Create a new OwaspTopTen record.
    """
    if request.method == "POST":
        if request.data:
            return owasp_top_ten_controller.add_entity(request)
        return {'error': 'Missing OwaspTopTen details'}, 400
    return {'error': 'Invalid request'}, 400

@owasp_top_ten_blueprint.route('/crscan/owasp_top_ten/<string:owasp_top_ten_id>', methods=['PUT'])
def update_owasp_top_ten(owasp_top_ten_id):
    """
    Update an existing OwaspTopTen record.
    """
    request_json = request.get_json()
    if not request_json:
        return {'error': 'Missing or invalid OwaspTopTen details'}, 400
    return owasp_top_ten_controller.update_entity(owasp_top_ten_id, request_json)



@owasp_top_ten_blueprint.route('/crscan/owasp_top_ten/<string:owasp_top_ten_id>', methods=['DELETE'])
def delete_owasp_top_ten(owasp_top_ten_id):
    """
    Soft delete an OwaspTopTen record.
    """
    print(f"Received delete request for ID: {owasp_top_ten_id}")  # Debugging
    response = owasp_top_ten_controller.delete_entity(owasp_top_ten_id)
    print(f"Response: {response}")  # Check the response
    return response
