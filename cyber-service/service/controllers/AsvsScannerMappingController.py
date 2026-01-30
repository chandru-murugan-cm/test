from flask import request, jsonify
from mongoengine import *
from controllers.util import *
from entities.CyberServiceEntity import AsvsScannerMapping, ScannerTypes
from typing import List
from datetime import datetime, timezone
import json
import uuid


class AsvsScannerMappingController():
    """
    Defines Controller for Asvs Scanner Mapping
    """

    def __init__(self) -> None:
        pass

    
    def fetch_by_id(self, fields) -> List[dict]:
        """
        Fetches Asvs Scanner Mapping by ID
        """
        # Validate JWT Token
        verify_jwt_in_request()
        if "_id" in fields:
            asvs_id = fields['_id']

            try:
                pipeline = pipeline = [
                    {
                        "$match": {
                            "_id": asvs_id
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
                        "$project": {
                            "isdeleted": 0
                            }
                        },
                    {
                        "$unwind": "$scanner_type_details"
                        },
                    {
                        "$project": {
                            "asvs_id": 1,
                            "asvs_group_name": 1,
                            "scanner_type_id": 1,
                            "scanner_type_details.scan_type_id": 1,
                            "scanner_type_details.scan_type": 1,
                            "scanner_type_details.scan_target_type": 1,
                            "scanner_type_details.description": 1
                        }
                    }
                ]
                asvs_scanner_mapping = AsvsScannerMapping.objects.aggregate(pipeline)
                return list(asvs_scanner_mapping)
            except Exception as e:
                return {'error': str(e)}, '500 Internal Server Error'
        return {'error': 'No valid query parameter provided'}, '400 Bad Request'
    
    def fetch_all(self) -> dict:
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
                    "$project": {
                        "isdeleted": 0
                    }
                }
            ]
            asvs_scanner_mappings = list(AsvsScannerMapping.objects.aggregate(pipeline))
            return {'success': 'Records fetched successfully', 'data': asvs_scanner_mappings}, 200
        except ValidationError as e:
            return {'error': 'Validation error: ' + str(e)}, 400
        except Exception as e:
            return {'error': 'Error: ' + str(e)}, 500

    
    
    def add_entity(self, request) -> dict:
        """
        Add Asvs Scanner Mapping
        """
        verify_jwt_in_request()
        try:
            request_json = request.get_json()

            if not request_json:
                return jsonify({'error': 'No data provided'}), 400

            asvs_id = request_json.get('asvs_id', None)
            scanner_type_id = request_json.get("scanner_type_id", [])

            if not scanner_type_id or not isinstance(scanner_type_id, list):
                return jsonify({"error": "Invalid input. `scanner_type_id` must be a non-empty list."}), 400

            valid_scanner_types = ScannerTypes.objects.filter(scan_type_id__in=scanner_type_id)
            valid_scanner_type_ids = [scanner.scan_type_id for scanner in valid_scanner_types]

            invalid_scanner_type_ids = set(scanner_type_id) - set(valid_scanner_type_ids)
            if invalid_scanner_type_ids:
                return jsonify({"error": "Invalid scan types provided.", "invalid_ids": list(invalid_scanner_type_ids)}), 400

            asvs_scanner_mapping = AsvsScannerMapping(
                asvs_scanner_mapping_id=str(uuid.uuid4()),
                asvs_id=asvs_id,
                scanner_type_id=valid_scanner_type_ids,
                created=datetime.now(timezone.utc),
            )
            asvs_scanner_mapping.save()
            return jsonify({'success': 'Record Created Successfully', 'data': json.loads(asvs_scanner_mapping.to_json())}), 201

        except ValidationError as e:
            return jsonify({'error': f'Validation error: {e.message}'}), 400
        except Exception as e:
            return jsonify({'error': f'Error: {str(e)}'}), 500

    def update_entity(self, request_json) -> dict:
        """
        Update Asvs Scanner Mapping
        """
        verify_jwt_in_request()
        try:
            if not request_json:
                return jsonify({'error': 'No data provided'}), 400

            asvs_scanner_mapping_id = request_json.get("_id")
            if not asvs_scanner_mapping_id:
                return jsonify({'error': 'Missing `_id` field'}), 400

            scanner_type_id = request_json.get("scanner_type_id", [])
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
            asvs_scanner_mapping = AsvsScannerMapping.objects.get(asvs_scanner_mapping_id=asvs_scanner_mapping_id)

            asvs_scanner_mapping.scanner_type_id = valid_scanner_type_ids
            asvs_scanner_mapping.save(validate=False)  

            return jsonify({'success': 'Record Updated Successfully', 'data': json.loads(asvs_scanner_mapping.to_json())}), 200
        except DoesNotExist:
            return jsonify({'error': 'Asvs Scanner Mapping not found'}), 404
        except ValidationError as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'error': f'Error: {str(e)}'}), 500

    def delete_entity(self, asvs_scanner_mapping_id) -> dict:
        """
        Delete Asvs Scanner Mapping
        """
        verify_jwt_in_request()
        try:
            asvs_scanner_mapping = AsvsScannerMapping.objects.get(asvs_scanner_mapping_id=asvs_scanner_mapping_id)
            asvs_scanner_mapping.delete()
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
                        "asvs_id": 1,
                        "asvs_group_name": 1,
                        "scanner_type_id": 1,
                        "scanner_details.scan_type_id": 1,
                        "scanner_details.scan_type": 1,
                        "scanner_details.scan_target_type": 1,
                        "scanner_details.description": 1
                    }
                }
            ]
            asvs_scanner_mappings = list(AsvsScannerMapping.objects.aggregate(pipeline))
            return {'success': 'Records fetched successfully', 'data': asvs_scanner_mappings}, 200
        except ValidationError as e:
            return {'error': 'Validation error: ' + str(e)}, 400
        except Exception as e:
            return {'error': 'Error: ' + str(e)}, 500


