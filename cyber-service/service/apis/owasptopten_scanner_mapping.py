from flask import Blueprint, request, jsonify
import urllib.parse
from controllers.OwaspScannerMappingController import OwaspTopTenScannerMappingController

owasptopten_scanner_mapping_blueprint = Blueprint('owasptopten_scanner_mapping_blueprint', __name__)
owasptopten_scanner_mapping_controller = OwaspTopTenScannerMappingController()

@owasptopten_scanner_mapping_blueprint.route('/crscan/owasptopten_scanner_mapping', methods=['GET'])
def get_owasptopten_scanner_mapping():
    """
    Fetch OWASP Top Ten Scanner Mapping by _id using query parameters.
    """
    owasp_top_ten_id = urllib.parse.unquote(request.args.get('_id', ''))
    
    if owasp_top_ten_id:
        fields = {'_id': owasp_top_ten_id}
        response = owasptopten_scanner_mapping_controller.fetch_by_id(fields)
        return jsonify(response), 200 if isinstance(response, list) else 500
    
    return jsonify({'error': 'No valid query parameter provided'}), 400

@owasptopten_scanner_mapping_blueprint.route('/crscan/owasptopten_scanner_mapping', methods=['POST'])
def create_owasptopten_scanner_mapping():
    """
    Create a new OWASP Top Ten Scanner Mapping.
    """
    request_json = request.get_json(silent=True)  

    if not isinstance(request_json, dict): 
        return jsonify({'error': 'Invalid JSON format'}), 400

    return owasptopten_scanner_mapping_controller.add_entity(request_json)

@owasptopten_scanner_mapping_blueprint.route('/crscan/owasptopten_scanner_mapping/<owasptopten_scanner_mapping_id>', methods=['PUT', 'DELETE'])
def modify_or_delete_owasptopten_scanner_mapping(owasptopten_scanner_mapping_id):
    """
    Update or delete OWASP Top Ten Scanner Mapping by _id.
    """
    if request.method == 'PUT':
        request_json = request.get_json()
        
        if not request_json:
            return jsonify({'error': 'Missing Owasp Scanner Mapping details for update'}), 400
        
        request_json['_id'] = owasptopten_scanner_mapping_id
        response = owasptopten_scanner_mapping_controller.update_entity(request_json)
        return response

    elif request.method == 'DELETE':
        response = owasptopten_scanner_mapping_controller.delete_entity(owasptopten_scanner_mapping_id)
        return response

    return jsonify({'error': 'Invalid request method'}), 400

@owasptopten_scanner_mapping_blueprint.route('/crscan/owasptopten_with_scanner_types', methods=['GET'])
def get_owasptopten_with_scanner_types():
    """
    Fetch all OWASP Top Ten Scanner Mappings with scanner type details.
    """
    try:
        response = owasptopten_scanner_mapping_controller.fetch_by()
        return response
    except Exception as e:
        return ({'error': str(e)}), 500
