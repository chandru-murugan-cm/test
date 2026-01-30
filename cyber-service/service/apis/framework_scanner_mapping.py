from flask import Blueprint, request, jsonify
import urllib.parse
from controllers.FrameworkScannerMappingController import FrameworkScannerMappingController

framework_scanner_mapping_blueprint = Blueprint(
    'framework_scanner_mapping_blueprint', __name__)
framework_scanner_mapping_controller = FrameworkScannerMappingController()


@framework_scanner_mapping_blueprint.route('/crscan/framework_scanner_mapping', methods=['GET'])
def get_framework_scanner_mapping():
    """
    Fetch framework scanner mapping by _id, framework_type, or framework_group_name using query parameters.
    """
    framework_id = urllib.parse.unquote(request.args.get('_id', ''))
    # Fetch by framework_id
    if framework_id:
        fields = {'_id': framework_id}
        return framework_scanner_mapping_controller.fetch_by_id(fields)
    return {'error': 'No valid query parameter provided'}, '400 Bad Request'


@framework_scanner_mapping_blueprint.route('/crscan/framework_scanner_mapping', methods=['POST'])
def create_framework_scanner_mapping():
    """
    Create a new framework scanner mapping.
    """
    if request.method == "POST":
        if request.data:
            return framework_scanner_mapping_controller.add_entity(request)
        return {'error': 'Missing Framework Scanner Mapping details'}, '400 Bad Request'

    return {'error': 'Invalid request method'}, '400 Bad Request'


@framework_scanner_mapping_blueprint.route('/crscan/framework_scanner_mapping/<framework_id>', methods=['PUT', 'DELETE'])
def update_delete_framework_scanner_mapping(framework_id):
    """
    Update or delete framework scanner mapping by _id.
    """
    framework_id = urllib.parse.unquote(framework_id)
    # Update framework scanner mapping
    if request.method == 'PUT':
        if framework_id and request.data:
            response = framework_scanner_mapping_controller.update_entity(
                framework_id, request)
            return response
        return jsonify({'error': 'Missing Framework Scanner Mapping details for update'}), 400
    # Delete framework scanner mapping
    elif request.method == 'DELETE':
        if framework_id:
            return framework_scanner_mapping_controller.delete_entity(framework_id)
        return jsonify({'error': 'Missing Framework Scanner Mapping ID for deletion'}), 400
    return {'error': 'Invalid request method'}, '400 Bad Request'

@framework_scanner_mapping_blueprint.route('/crscan/framework_with_scanner_types', methods=['GET'])
def get_frameworks():
    try:
        response = framework_scanner_mapping_controller.fetch_by()
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
