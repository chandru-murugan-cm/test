from flask import Blueprint, request
from flasgger import swag_from
from docs.swagger.swagger_models import success_response, error_response
from controllers.ContractController import ContractController

contract_blueprint = Blueprint('contract_blueprint', __name__)
contract_controller = ContractController()

@contract_blueprint.route('/crscan/contract', methods=['GET', 'POST'])
@contract_blueprint.route('/crscan/contract/<target_contract_id>', methods=['GET', 'PUT', 'DELETE'])
@swag_from({
    'tags': ['Smart Contract Security'],
    'summary': 'Manage smart contract targets',
    'description': 'Create, retrieve, update, and delete smart contract targets for security scanning. Supports various blockchain platforms and contract languages.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'name': 'target_contract_id',
            'in': 'path',
            'type': 'string',
            'required': False,
            'description': 'ID of the smart contract target'
        },
        {
            'name': 'project_id',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Project ID to filter contracts'
        },
        {
            'name': 'contract_url',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Contract URL to filter by'
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
                            'contract_url': {'type': 'string', 'example': 'https://github.com/user/contract.sol'},
                            'contract_type': {'type': 'string', 'example': 'Solidity'},
                            'blockchain': {'type': 'string', 'example': 'Ethereum'},
                            'scan_status': {'type': 'string', 'example': 'pending'},
                            'created_at': {'type': 'string', 'format': 'date-time'}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request - Missing contract details',
            'schema': error_response
        },
        401: {
            'description': 'Unauthorized - Invalid or missing token',
            'schema': error_response
        },
        404: {
            'description': 'Not found - Contract not found',
            'schema': error_response
        }
    },
    'security': [{'Bearer': []}]
})
def contract(target_contract_id=None):
    if request.method == 'POST':
        if request.form:
            return contract_controller.add_entity(request)
        return {'error': 'Missing Contract details'}, 400
    
    elif request.method == 'DELETE':
        if target_contract_id:
            return contract_controller.remove_entity(target_contract_id)
        return {'error': 'Missing Contract ID'}, 400
    
    elif request.method == 'GET':
        fields = {}
        if request.args.get('target_contract_id') is not None:
            fields['target_contract_id'] = request.args.get('target_contract_id')
        if request.args.get('project_id') is not None:
            fields['project_id'] = request.args.get('project_id')
        if request.args.get('contract_url') is not None:
            fields['contract_url'] = request.args.get('contract_url')

        fields = {k: v for k, v in fields.items() if v is not None}
        return contract_controller.fetch_all(request, fields)
    
    elif request.method == 'PUT':
        if target_contract_id:
            return contract_controller.update_by_id(request, target_contract_id)
        return {'error': 'Missing Contract ID'}, 400