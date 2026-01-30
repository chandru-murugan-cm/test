from flask import request, jsonify
from mongoengine import *
from controllers.util import *
from entities.CyberServiceEntity import DomainWapiti1, Compliance,Samm
from typing import List
import uuid, json
from datetime import datetime, timezone

class SammController():
    """
    Defines controller methods for the SammController Entity.
    """

    def __init__(self) -> None:
        pass

    def fetch_by_id(self, fields) -> List[dict]:
        """
        Fetches a Samm Controller  object by its _id from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()
        if "_id" in fields:
            samm_id = fields['_id']

            try:
                pipeline = [
                    {
                        "$match": {
                            "_id": samm_id
                        }
                    },
                    {
                        "$project": {
                            "isdeleted": 0
                        }
                    }
                ]

                # Execute the aggregation pipeline
                samm_list = list(
                    Samm.objects.aggregate(*pipeline)
                )
                
                return {'success': 'Records fetched successfully', 'data': samm_list}, '200 Ok'

            except DoesNotExist as e:
                return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_by_compliance_type(self, compliance_type) -> List[dict]:
        """
        Fetches Compliance records by compliance_type from the database.
        """
        verify_jwt_in_request()

        try:
            pipeline = [
                {
                    "$match": {
                        "compliance_type": compliance_type
                    }
                },
                {
                    "$project": {
                        "isdeleted": 0 
                    }
                }
            ]
            compliance_list = list(Compliance.objects.aggregate(*pipeline))

            return {'success': 'Records fetched successfully', 'data': compliance_list}, '200 Ok'

        except DoesNotExist as e:
            return {'error': 'No records found for compliance_type: ' + compliance_type}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_by_compliance_group_name(self, compliance_group_name) -> List[dict]:
        """
        Fetches Compliance records by compliance_group_name from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()

        try:
            # Find compliance records by compliance_group_name
            pipeline = [
                {
                    "$match": {
                        "compliance_group_name": compliance_group_name
                    }
                },
                {
                    "$project": {
                        "isdeleted": 0  # Optionally exclude isdeleted field
                    }
                }
            ]
            # Execute the aggregation pipeline
            compliance_list = list(Compliance.objects.aggregate(*pipeline))

            return {'success': 'Records fetched successfully', 'data': compliance_list}, '200 Ok'

        except DoesNotExist as e:
            return {'error': 'No records found for compliance_group_name: ' + compliance_group_name}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def get_unique_compliance_types(self) -> dict:
            """
            Fetches unique compliance_type values from the database.
            """
            # Validate JWT Token
            verify_jwt_in_request()

            try:
                # Fetch distinct compliance_type values
                compliance_types = Compliance.objects.distinct('compliance_type')

                if not compliance_types:
                    return {'error': 'No compliance types found'}, '404 Not Found'

                return {'success': 'Unique compliance types fetched successfully', 'data': compliance_types}, '200 Ok'

            except Exception as e:
                return {'error': 'Error fetching compliance types: ' + str(e)}, '500 Internal Server Error'
        
    def fetch_all(self, request) -> List[dict]:
        """
        Fetches all Compliance records from the database.
        """
        # Validate JWT Token
        # verify_jwt_in_request()

        try:
            pipeline = [
                {
                    "$project": {
                        "isdeleted": 0  
                    }
                }
            ]

            samm_list = list(Samm.objects.aggregate(*pipeline))

            return {'success': 'Records fetched successfully', 'data': samm_list}, '200 Ok'

        except DoesNotExist as e:
            return {'error': 'No records found: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
        
    def add_entity(self, request) -> dict:
    # Validate JWT Token
        verify_jwt_in_request()

    # Get the request data
        record = request.get_json()
        print("Request JSON Data:", record)  # Debugging line
        required_fields = [
            'l1_business_function', 'l2_security_practice', 'l3_stream',
            'l4_strategy_and_metrics', 'l4_strategy_and_metrics_question',
            'l4_strategy_and_metrics_description', 'l4_strategy_and_metrics_coverage'
        ]
        missing_fields = [field for field in required_fields if field not in record]
        if missing_fields:
            return {'error': f'Missing fields: {", ".join(missing_fields)}'}, '400 Bad Request'
    # Ensure that coverage is handled properly if it's an array
        coverage_data = record.get('l4_strategy_and_metrics_coverage', [])
        if not isinstance(coverage_data, list):
            return {'error': 'l4_strategy_and_metrics_coverage should be an array'}, '400 Bad Request'
    # Create new Samm object
        try:
            new_samm_obj = Samm(
                samm_id=str(uuid.uuid4()),
                l1_business_function=record.get('l1_business_function', None),
                l2_security_practice=record.get('l2_security_practice', None),
                l3_stream=record.get('l3_stream', None),
                l4_strategy_and_metrics=record.get('l4_strategy_and_metrics', None),
                l4_strategy_and_metrics_question=record.get('l4_strategy_and_metrics_question', None),
                l4_strategy_and_metrics_description=record.get('l4_strategy_and_metrics_description', None),
                l4_strategy_and_metrics_coverage=coverage_data,
            )
        # Save the new Samm entity
            new_samm_obj.save()
            return {'success': 'Samm entity created successfully', 'data': new_samm_obj.to_json()}, '201 Created'
        except Exception as e:
            return {'error': f'Error creating Samm entity: {str(e)}'}, '500 Internal Server Error'

         
    def get_unique_samm_types(self) -> tuple:
        verify_jwt_in_request()  # Ensures the request is authenticated
        try:
            l1_business_function = Compliance.objects.distinct('l1_business_function')
            if not l1_business_function:
                return jsonify({
                    'error': 'No l1_business_function found'
                }), 404
            return jsonify({'success': 'Unique l1_business_function fetched successfully','data': l1_business_function}), 200
        except DoesNotExist:
            return jsonify({'error': 'No records found in the database'}), 404
        except Exception as e:
            return jsonify({'error': f'Error fetching data: {str(e)}'}), 500
        
    def update_entity(self, samm_id: str, request_json: dict) -> tuple:
        print("Request JSON received:", request_json)
        try:
            if not request_json or not isinstance(request_json, dict):
                return {'error': 'Request body is invalid or empty'}, 400
            updated_data = {k: v for k, v in request_json.items() if v is not None}
            if not updated_data:
                return {'error': 'No valid fields provided for update'}, 400
            samm_record = Samm.objects.get(samm_id=samm_id)
            samm_record.update(**updated_data)
            updated_record = Samm.objects.get(samm_id=samm_id)
            response = json.loads(updated_record.to_json())
            return response, 200
        except Samm.DoesNotExist:
            return {'error': f'samm record with ID {samm_id} not found'}, 404
        except Exception as e:
            print(f"Unexpected error occurred while saving: {e}")
            return {'error': f'Unexpected error: {str(e)}'}, 500
   
        
    def delete_entity(self, samm_id: str) -> dict:
        verify_jwt_in_request()  
        try:
            samm_entity = Samm.objects.get(samm_id=samm_id)
            samm_entity.delete()
            return {'success': f'Samm entity with _id: {samm_id} deleted successfully'}, '200 Ok'
        except DoesNotExist:
            return {'error': f'No Samm entity found with _id: {samm_id}'}, '404 Not Found'
        except ValidationError as e:
            return {'error': f'Invalid _id: {e.message}'}, '400 Bad Request'
        except Exception as e:
            return {'error': f'Error deleting Samm entity: {str(e)}'}, '500 Internal Server Error'
        
        
    def fetch_all_l1_business_functions(self) -> dict:
        verify_jwt_in_request()  
        try:
            unique_l1_business_functions = Samm.objects.distinct('l1_business_function')
            if not unique_l1_business_functions:
                return {'error': 'No records found'}, 404
            return {'success': 'Unique l1_business_function fields fetched successfully', 'data': unique_l1_business_functions}, 200
        except Exception as e:
            return {'error': f'Unexpected error: {str(e)}'}, 500


    def fetch_by_project_id(self, project_id) -> dict:
        """"
        Fetches Framework records by project_id from the database.
        """
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
                    "$lookup": {
                        "from": "FindingMaster",
                        "let": {
                            "scanner_types_ids": "$scanner_types._id",
                            "project_id": project_id
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$in": ["$scan_type_id", "$$scanner_types_ids"]},
                                            {"$eq": ["$project_id", "$$project_id"]}
                                        ]
                                    }
                                }
                            }
                        ],
                        "as": "matched_findings"
                    }
                },
                {
                    "$project": {
                        "isdeleted": 0
                    }
                }
            ]

            # Execute query on Samm collection
            samm_list = list(Samm.objects.aggregate(*pipeline))

            return {'success': 'Records fetched successfully', 'data': samm_list}, '200 Ok'
        
        except DoesNotExist as e:
            return {'error': 'No records found for project_id: ' + project_id}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

