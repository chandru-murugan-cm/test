from flask import Blueprint, request, jsonify
import urllib.parse
from controllers.AsvsScannerMappingController import AsvsScannerMappingController

asvs_scanner_mapping_blueprint = Blueprint('asvs_scanner_mapping_blueprint', __name__)
asvs_scanner_mapping_controller = AsvsScannerMappingController()


@asvs_scanner_mapping_blueprint.route('/crscan/asvs_scanner_mapping', methods=['GET'])
def get_asvs_scanner_mapping():
    """
    Fetch asvs scanner mapping by _id, asvs_type, or asvs_group_name using query parameters.
    """
    # Fetch query parameters
    asvs_id = urllib.parse.unquote(request.args.get('_id', ''))
    # Fetch by asvs_id
    if asvs_id:
        fields = {'_id': asvs_id}
        return asvs_scanner_mapping_controller.fetch_by_id(fields)
    return {'error': 'No valid query parameter provided'}, '400 Bad Request'


@asvs_scanner_mapping_blueprint.route('/crscan/asvs_scanner_mapping', methods=['POST'])
def create_asvs_scanner_mapping():
    """
    Create a new asvs scanner mapping.
    """
    if request.method == "POST":
        if request.data:
            return asvs_scanner_mapping_controller.add_entity(request)
        return {'error': 'Missing Compliance Scanner Mapping details'}, '400 Bad Request'

    return {'error': 'Invalid request method'}, '400 Bad Request'


@asvs_scanner_mapping_blueprint.route('/crscan/asvs_scanner_mapping/<asvs_scanner_mapping_id>', methods=['PUT', 'DELETE'])
def asvs_scanner_mapping(asvs_scanner_mapping_id):
    """
    Update or delete asvs scanner mapping by _id.
    """
    # Update asvs scanner mapping
    if request.method == 'PUT':
        if request.data:
            data = request.get_json()
            data['_id'] = asvs_scanner_mapping_id  
            response = asvs_scanner_mapping_controller.update_entity(data)
            return response
        return jsonify({'error': 'Missing Compliance Scanner Mapping details for update'}), 400

    # Delete asvs scanner mapping
    elif request.method == 'DELETE':
        if asvs_scanner_mapping_id:
            return asvs_scanner_mapping_controller.delete_entity(asvs_scanner_mapping_id)
        return jsonify({'error': 'Missing Compliance Scanner Mapping ID for deletion'}), 400
    return jsonify({'error': 'Invalid request method'}), 400

@asvs_scanner_mapping_blueprint.route('/crscan/asvs_with_scanner_types',methods=['GET'])
def get_asvs_with_scanner_types():
    try:
        response = asvs_scanner_mapping_controller.fetch_by()
        return response
    except Exception as e:
        return {'error': str(e)}, 500
    


