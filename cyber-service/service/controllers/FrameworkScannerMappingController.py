from flask import jsonify
from mongoengine import *
from controllers.util import *
from entities.CyberServiceEntity import FrameworkScannerMapping, Samm, ScannerTypes
from typing import List
import uuid, json
from datetime import datetime, timezone

class FrameworkScannerMappingController():
    """
    Defines Controller for Framework Scanner Mapping
    """

    def __init__(self) -> None:
        pass

    def fetch_by_id(self, fields) -> List[dict]:
        """
        Fetches Framework Scanner Mapping by ID
        """
        # Validate JWT Token
        verify_jwt_in_request()
        if "_id" in fields:
            framework_id = fields['_id']

            try:
                pipeline = pipeline = [
                    {
                        "$match": {
                            "_id": framework_id
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
                            "framework_id": 1,
                            "framework_group_name": 1,
                            "scanner_type_id": 1,
                            "scanner_type_details.scan_type_id": 1,
                            "scanner_type_details.scan_type": 1,
                            "scanner_type_details.scan_target_type": 1,
                            "scanner_type_details.description": 1
                        }
                    }
                ]
                # Fetch Framework Scanner Mapping
                framework_scanner_mapping = FrameworkScannerMapping.objects.aggregate(pipeline)
                return list(framework_scanner_mapping)
            except Exception as e:
                return {'error': str(e)}, '500 Internal Server Error'
        return {'error': 'No valid query parameter provided'}, '400 Bad Request'

    def add_entity(self, request) -> dict:
        """
        Adds a new Framework Scanner Mapping
        """
        # Validate JWT Token
        verify_jwt_in_request()
        try:
            # Get the data from the request
            request_json = request.get_json()
            # Create a new Framework Scanner Mapping
            framework_id = None
            if 'framework_id' in request_json:
                framework_id = request_json['framework_id']
            scanner_type_id = request_json['scanner_type_id']
            if not scanner_type_id or not isinstance(scanner_type_id, list):
                return {'error': 'Missing scanner_type_id'}, '400 Bad Request'
            
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
            framework_scanner_mapping = FrameworkScannerMapping(
                framework_scanner_mapping_id=str(uuid.uuid4()),
                framework_id=framework_id,
                scanner_type_id=valid_scanner_type_ids,
                created=datetime.now(timezone.utc),
            )
            framework_scanner_mapping.save()
            response = json.loads(framework_scanner_mapping.to_json())
            return {'success': 'Record Created Successfully', 'data': response}, '200 Ok'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
        except Exception as e:
            return {'error': 'Error: ' + str(e)}, '500 Internal Server Error'
        
    def update_entity(self, framework_id, request) -> List[dict]:
        """
        Update Framework Scanner Mapping
        """
        # Validate JWT Token
        verify_jwt_in_request()
        try:
            # Get the data from the request
            request_json = request.get_json()
            framework_id = request_json.get('framework_id', None)
            scanner_type_id = request_json.get("scanner_type_id", [])

            if scanner_type_id:
                valid_scanner_types = ScannerTypes.objects.filter(scan_type_id__in=scanner_type_id)
                valid_scanner_type_ids = [scanner.scan_type_id for scanner in valid_scanner_types]

                # Find invalid scanner_type_id
                invalid_scanner_type_ids = set(scanner_type_id) - set(valid_scanner_type_ids)
                if invalid_scanner_type_ids:
                    return jsonify({
                        "error": "Invalid scan types provided.",
                        "invalid_ids": list(invalid_scanner_type_ids)
                    }), 400
            else:
                valid_scanner_type_ids = []  
            # Retrieve the framework scanner mapping
            framework_scanner_mapping = FrameworkScannerMapping.objects.filter(framework_id=framework_id).first()
            if not framework_scanner_mapping:
                return jsonify({'error': 'Compliance Scanner Mapping not found'}), 404
            
            # Update the data
            framework_scanner_mapping.framework_id = framework_id
            framework_scanner_mapping.scanner_type_id = valid_scanner_type_ids
            framework_scanner_mapping.save(validate=False) 

            response = json.loads(framework_scanner_mapping.to_json())
            return {'success': 'Record Updated Successfully', 'data': response}, '200 Ok'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
        except Exception as e:
            return {'error': 'Error: ' + str(e)}, '500 Internal Server Error'
        
    def delete_entity(self, framework_id) -> dict:
        """
        Delete Framework Scanner Mapping
        """
        # Validate JWT Token
        verify_jwt_in_request()
        try:
            # Delete the Framework Scanner Mapping
            framework_scanner_mapping = FrameworkScannerMapping.objects.get(
                _id=framework_id)
            framework_scanner_mapping.delete()
            return {'success': 'Record Deleted Successfully'}, '200 Ok'
        except DoesNotExist:
            return {'error': 'Record not found'}, '404 Not Found'
        except Exception as e:
            return {'error': 'Error: ' + str(e)}, '500 Internal Server Error'
        
    def fetch_by(self) -> dict:
        verify_jwt_in_request()
        try:

            pipeline = [
                {
                    "$lookup": {
                        "from": "FrameworkScannerMapping",
                        "localField": "_id",
                        "foreignField": "framework_id",
                        "as": "framework_scanner_mapping"
                    }
                },
                {
                    "$unwind": {
                        "path": "$framework_scanner_mapping",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$lookup": {
                        "from": "ScannerTypes",
                        "localField": "framework_scanner_mapping.scanner_type_id",
                        "foreignField": "_id",
                        "as": "scanner_types"
                    }
                },
                {
                    "$project": {
                        "isdeleted": 0
                    }
                }
            ]
            samm_list = list(Samm.objects.aggregate(pipeline))
            return {'success': 'Records fetched successfully', 'data': samm_list}, 200
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, 400
        except Exception as e:
            return {'error': 'Error: ' + str(e)}, 500
