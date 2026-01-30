from flask import Blueprint, request, jsonify
import urllib.parse
from controllers.ComplianceScannerMappingController import ComplianceScannerMappingController

compliance_scanner_mapping_blueprint = Blueprint(
    'compliance_scanner_mapping_blueprint', __name__)
compliance_scanner_mapping_controller = ComplianceScannerMappingController()


@compliance_scanner_mapping_blueprint.route('/crscan/compliance_scanner_mapping', methods=['GET'])
def get_compliance_scanner_mapping():
    """
    Fetch compliance scanner mapping by _id, compliance_type, or compliance_group_name using query parameters.
    """
    # Fetch query parameters
    compliance_id = urllib.parse.unquote(request.args.get('_id', ''))
    # Fetch by compliance_id
    if compliance_id:
        fields = {'_id': compliance_id}
        return compliance_scanner_mapping_controller.fetch_by_id(fields)
    return {'error': 'No valid query parameter provided'}, '400 Bad Request'


@compliance_scanner_mapping_blueprint.route('/crscan/compliance_scanner_mapping', methods=['POST'])
def create_compliance_scanner_mapping():
    """
    Create a new compliance scanner mapping.
    """
    if request.method == "POST":
        if request.data:
            return compliance_scanner_mapping_controller.add_entity(request)
        return {'error': 'Missing Compliance Scanner Mapping details'}, '400 Bad Request'

    return {'error': 'Invalid request method'}, '400 Bad Request'


@compliance_scanner_mapping_blueprint.route('/crscan/compliance_scanner_mapping/<compliance_scanner_mapping_id>', methods=['PUT', 'DELETE'])
def compliance_scanner_mapping(compliance_scanner_mapping_id):
    """
    Update or delete compliance scanner mapping by _id.
    """
    # Update compliance scanner mapping
    if request.method == 'PUT':
        if request.data:
            data = request.get_json()
            data['_id'] = compliance_scanner_mapping_id  # Ensure ID is part of the request data
            response = compliance_scanner_mapping_controller.update_entity(data)
            return response
        return jsonify({'error': 'Missing Compliance Scanner Mapping details for update'}), 400

    # Delete compliance scanner mapping
    elif request.method == 'DELETE':
        if compliance_scanner_mapping_id:
            return compliance_scanner_mapping_controller.delete_entity(compliance_scanner_mapping_id)
        return jsonify({'error': 'Missing Compliance Scanner Mapping ID for deletion'}), 400

    return jsonify({'error': 'Invalid request method'}), 400

