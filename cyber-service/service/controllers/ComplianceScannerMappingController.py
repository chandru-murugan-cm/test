from flask import request, jsonify
from mongoengine import *
from controllers.util import *
from entities.CyberServiceEntity import ComplianceScannerMapping, ScannerTypes
from typing import List
from datetime import datetime, timezone
import json
import uuid


class ComplianceScannerMappingController():
    """
    Defines Controller for Compliance Scanner Mapping
    """

    def __init__(self) -> None:
        pass

    def fetch_by_id(self, fields) -> List[dict]:
        """
        Fetches Compliance Scanner Mapping by ID
        """
        # Validate JWT Token
        verify_jwt_in_request()
        if "_id" in fields:
            compliance_scanner_mapping_id = fields['_id']

            try:
                pipeline = pipeline = [
                    {
                        "$match": {
                            "_id": compliance_scanner_mapping_id
                        }
                    },
                    {
                        "$project": {
                            "isdeleted": 0
                        }
                    },
                    {
                        "$lookup": {
                            "from": "ScannerTypes",
                            "localField": "scanner_type_id",
                            "foreignField": "scan_type_id",
                            "as": "scanner_details"
                        }
                    },
                    {
                        "$unwind": "$scanner_type_details"
                    },
                    {
                        "$project": {
                            "compliance_scanner_mapping_id": 1,
                            "compliance_id": 1,
                            "scanner_type_id": 1,
                            "scanner_type_details.scan_type_id": 1,
                            "scanner_type_details.scan_type": 1,
                            "scanner_type_details.scan_target_type": 1,
                            "scanner_type_details.description": 1
                        }
                    }
                ]

                # Execute the aggregation pipeline
                compliance_list = list(
                    ComplianceScannerMapping.objects.aggregate(*pipeline)
                )

                return {'success': 'Records fetched successfully', 'data': compliance_list}, '200 Ok'

            except DoesNotExist as e:
                return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def add_entity(self, request) -> List[dict]:
        """
        Add Compliance Scanner Mapping
        """
        # Validate JWT Token
        verify_jwt_in_request()
        try:
            # Get the data from the request
            request_json = request.get_json()
            compliance_id = None
            if 'compliance_id' in request_json:
                compliance_id = request_json.get('compliance_id', None)
            scanner_type_id = request_json.get("scanner_type_id", [])
            if not scanner_type_id or not isinstance(scanner_type_id, list):
                return jsonify({"error": "Invalid input. `scanner_type_id` must be a non-empty list."}), 400

            # Validate scanner_type_id against ScannerTypes
    
            # Fetch valid scanner types from the database
            valid_scanner_types = ScannerTypes.objects.filter(scan_type_id__in=scanner_type_id)
            valid_scanner_type_ids = [scanner.scan_type_id for scanner in valid_scanner_types]

            # Find invalid scanner_type_ids
            invalid_scanner_type_ids = set(scanner_type_id) - set(valid_scanner_type_ids)
            if invalid_scanner_type_ids:
                return jsonify({
                    "error": "Invalid scan types provided.",
                    "invalid_ids": list(invalid_scanner_type_ids)
                }), 400

            # Validate the data
            if not request_json:
                return {'error': 'No data provided'}, '400 Bad Request'
            # Insert the data
            compliance_scanner_mapping = ComplianceScannerMapping(
                compliance_scanner_mapping_id=str(uuid.uuid4()),
                compliance_id=compliance_id,
                scanner_type_id=valid_scanner_type_ids,
                created=datetime.now(timezone.utc),
            )
            compliance_scanner_mapping.save()
            response = json.loads(compliance_scanner_mapping.to_json())
            return {'success': 'Record Created Successfully', 'data': response}, '200 Ok'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
        except Exception as e:
            return {'error': 'Error: ' + str(e)}, '500 Internal Server Error'

    def update_entity(self, request_json) -> List[dict]:
        """
        Update Compliance Scanner Mapping
        """
        # Validate JWT Token
        verify_jwt_in_request()

        try:
            # Ensure request contains JSON data
            if not request_json:
                return jsonify({'error': 'No data provided'}), 400

            # Extract compliance_id and scanner_type_id
            compliance_id = request_json.get("compliance_id")
            scanner_type_id = request_json.get("scanner_type_id", [])
            compliance_scanner_mapping_id = request_json.get("_id")

            if not scanner_type_id:
                return jsonify({"error": "No scan types provided"}), 400

            # Validate scanner_type_id against ScannerTypes
            valid_scanner_types = ScannerTypes.objects.filter(scan_type_id__in=scanner_type_id)
            valid_scanner_type_ids = [scanner.scan_type_id for scanner in valid_scanner_types]

            # Identify invalid scanner_type_ids
            invalid_scanner_type_ids = set(scanner_type_id) - set(valid_scanner_type_ids)
            if invalid_scanner_type_ids:
                return jsonify({
                    "error": "Invalid scan types provided",
                    "invalid_ids": list(invalid_scanner_type_ids)
                }), 400

            # Fetch ComplianceScannerMapping record
            compliance_scanner_mapping = ComplianceScannerMapping.objects.get(compliance_scanner_mapping_id=compliance_scanner_mapping_id)
            if not compliance_scanner_mapping:
                return jsonify({'error': 'Compliance Scanner Mapping not found'}), 404

            # Update fields
            compliance_scanner_mapping.compliance_id = compliance_id
            compliance_scanner_mapping.scanner_type_id = valid_scanner_type_ids
            compliance_scanner_mapping.save()

            response = json.loads(compliance_scanner_mapping.to_json())
            return jsonify({'success': 'Record Updated Successfully', 'data': response}), 200

        except ValidationError as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400

        except Exception as e:
            return jsonify({'error': f'Error: {str(e)}'}), 500

    def delete_entity(self, compliance_scanner_mapping_id) -> List[dict]:
        """
        Delete Compliance Scanner Mapping
        """
        # Validate JWT Token
        verify_jwt_in_request()
        try:
            # Delete the record
            compliance_scanner_mapping = ComplianceScannerMapping.query.get(
                compliance_scanner_mapping_id)
            compliance_scanner_mapping.delete()
            return {'success': 'Record Deleted Successfully'}, '200 Ok'
        except Exception as e:
            return {'error': 'Error: ' + str(e)}, '500 Internal Server Error'
