from flask import request, jsonify
from mongoengine import *
from controllers.util import verify_jwt_in_request
from entities.CyberServiceEntity import OwaspTopTenScannerMapping, ScannerTypes
from typing import List
from datetime import datetime, timezone
import json
import uuid

class OwaspTopTenScannerMappingController:
    """
    Defines Controller for OwaspTopTen Scanner Mapping
    """

    def fetch_by_id(self, fields) -> List[dict]:
        """
        Fetches OwaspTopTen Scanner Mapping by ID
        """
        verify_jwt_in_request()
        if "_id" in fields:
            owasp_top_ten_id = fields['_id']

            try:
                pipeline = [
                    {"$match": {"_id": owasp_top_ten_id}},
                    {
                        "$lookup": {
                            "from": "ScannerTypes",
                            "localField": "scanner_type_id",
                            "foreignField": "scan_type_id",
                            "as": "scanner_details"
                        }
                    },
                    {"$project": {"isdeleted": 0}},
                    {"$unwind": "$scanner_details"},
                    {
                        "$project": {
                            "owasp_top_ten_id": 1,
                            "OwaspTopTen_group_name": 1,
                            "scanner_type_id": 1,
                            "scanner_details.scan_type_id": 1,
                            "scanner_details.scan_type": 1,
                            "scanner_details.scan_target_type": 1,
                            "scanner_details.description": 1
                        }
                    }
                ]
                owasptopten_scanner_mapping = OwaspTopTenScannerMapping.objects.aggregate(pipeline)
                return list(owasptopten_scanner_mapping)
            except Exception as e:
                return {'error': str(e)}, '500 Internal Server Error'
        return {'error': 'No valid query parameter provided'}, '400 Bad Request'
    
    def add_entity(self, request_json) -> dict:
        """
        Add OwaspTopTen Scanner Mapping
        """
        verify_jwt_in_request()
        try:
            if not isinstance(request_json, dict): 
                return jsonify({'error': 'Invalid request format'}), 400

            if not request_json:
                return jsonify({'error': 'No data provided'}), 400

            owasp_top_ten_id = request_json.get('owasp_top_ten_id', None)
            scanner_type_id = request_json.get("scanner_type_id", [])

            if not scanner_type_id or not isinstance(scanner_type_id, list):
                return jsonify({"error": "Invalid input. `scanner_type_id` must be a non-empty list."}), 400

            valid_scanner_types = ScannerTypes.objects.filter(scan_type_id__in=scanner_type_id)
            valid_scanner_type_ids = [scanner.scan_type_id for scanner in valid_scanner_types]

            invalid_scanner_type_ids = set(scanner_type_id) - set(valid_scanner_type_ids)
            if invalid_scanner_type_ids:
                return jsonify({"error": "Invalid scan types provided.", "invalid_ids": list(invalid_scanner_type_ids)}), 400

            owasptopten_scanner_mapping = OwaspTopTenScannerMapping(
                owasptopten_scanner_mapping_id=str(uuid.uuid4()),
                owasp_top_ten_id=owasp_top_ten_id,
                scanner_type_id=valid_scanner_type_ids,
                created=datetime.now(timezone.utc),
            )
            owasptopten_scanner_mapping.save()
            return jsonify({'success': 'Record Created Successfully', 'data': json.loads(owasptopten_scanner_mapping.to_json())}), 201

        except ValidationError as e:
            return jsonify({'error': f'Validation error: {e.message}'}), 400
        except Exception as e:
            return jsonify({'error': f'Error: {str(e)}'}), 500

    def update_entity(self, request_json) -> dict:
        """
        Update OWASP Top Ten Scanner Mapping
        """
        verify_jwt_in_request()
        
        try:
            if not request_json:
                return jsonify({'error': 'No data provided'}), 400

            owasptopten_scanner_mapping_id = request_json.get("_id")
            if not owasptopten_scanner_mapping_id:
                return jsonify({'error': 'Missing `_id` field'}), 400

            scanner_type_id = request_json.get("scanner_type_id", [])

            if not isinstance(scanner_type_id, list):
                return jsonify({"error": "Invalid input. `scanner_type_id` must be a list."}), 400

            if scanner_type_id:
                valid_scanner_types = ScannerTypes.objects.filter(scan_type_id__in=scanner_type_id)
                valid_scanner_type_ids = [scanner.scan_type_id for scanner in valid_scanner_types]

                invalid_scanner_type_ids = set(scanner_type_id) - set(valid_scanner_type_ids)
                if invalid_scanner_type_ids:
                    return jsonify({
                        "error": "Invalid scan types provided",
                        "invalid_ids": list(invalid_scanner_type_ids)
                    }), 400
            else:
                valid_scanner_type_ids = []  
            mapping = OwaspTopTenScannerMapping.objects(owasptopten_scanner_mapping_id=owasptopten_scanner_mapping_id).first()
            
            if not mapping:
                return jsonify({'error': f'OWASP Top Ten Scanner Mapping with ID {owasptopten_scanner_mapping_id} not found'}), 404

            mapping.scanner_type_id = valid_scanner_type_ids
            mapping.updated = datetime.now(timezone.utc)
            mapping.save(validate=False)  
            return jsonify({'success': 'Record Updated Successfully', 'data': json.loads(mapping.to_json())}), 200
        
        except ValidationError as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'error': f'Unexpected Error: {str(e)}'}), 500
     
    def delete_entity(self, owasptopten_scanner_mapping_id) -> dict:
        """
        Delete OwaspTopTen Scanner Mapping
        """
        verify_jwt_in_request()
        try:
            owasptopten_scanner_mapping = OwaspTopTenScannerMapping.objects.get(owasptopten_scanner_mapping_id=owasptopten_scanner_mapping_id)
            owasptopten_scanner_mapping.delete()
            return jsonify({'success': 'Record Deleted Successfully'}), 200
        except DoesNotExist:
            return jsonify({'error': 'Record not found'}), 404
        except Exception as e:
            return jsonify({'error': f'Error: {str(e)}'}), 500
        
    def fetch_by(self) -> dict:
        verify_jwt_in_request()
        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": "ScannerTypes",
                        "localField": "scanner_type_id",
                        "foreignField": "scan_type_id",
                        "as": "scanner_details"
                    }
                },
                {
                    "$unwind": {
                        "path": "$scanner_details",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$project": {
                        "owasp_top_ten_id": 1,
                        "owasptopten_group_name": 1,
                        "scanner_type_id": 1,
                        "scanner_details.scan_type_id": 1,
                        "scanner_details.scan_type": 1,
                        "scanner_details.scan_target_type": 1,
                        "scanner_details.description": 1
                    }
                }
            ]
            owasptopten_scanner_mapping = list(OwaspTopTenScannerMapping.objects.aggregate(pipeline))
            return {'success': 'Records fetched successfully', 'data': owasptopten_scanner_mapping}, 200
        except ValidationError as e:
            return {'error': 'Validation error: ' + str(e)}, 400
        except Exception as e:
            return {'error': 'Error: ' + str(e)}, 500


