from flask import request, jsonify
from mongoengine import *
from controllers.util import *
from entities.CyberServiceEntity import DomainWapiti1, Compliance
from typing import List
import uuid, json
from datetime import datetime, timezone

class ComplianceController():
    """
    Defines controller methods for the ComplianceController Entity.
    """

    def __init__(self) -> None:
        pass

    def fetch_by_id(self, fields) -> List[dict]:
        """
        Fetches a Compliance Controller object by its _id from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()
        if "_id" in fields:
            compliance_id = fields['_id']

            try:
                pipeline = [
                    {
                        "$match": {
                            "_id": compliance_id
                        }
                    },
                    {
                        "$project": {
                            "isdeleted": 0
                        }
                    }
                ]

                # Execute the aggregation pipeline
                compliance_list = list(
                    Compliance.objects.aggregate(*pipeline)
                )
                
                return {'success': 'Records fetched successfully', 'data': compliance_list}, '200 Ok'

            except DoesNotExist as e:
                return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_by_compliance_type(self, compliance_type, project_id) -> List[dict]:
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
                    "$lookup": {
                        "from": "ComplianceScannerMapping",
                        "localField": "_id",
                        "foreignField": "compliance_id",
                        "as": "compliance_scanner_mapping"
                    }
                },
                {
                    "$unwind": {
                        "path": "$compliance_scanner_mapping",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$lookup": {
                        "from": "ScannerTypes",
                        "localField": "compliance_scanner_mapping.scanner_type_id",
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
                                            { "$in": ["$scan_type_id", "$$scanner_types_ids"] },
                                            { "$eq": ["$project_id", "$$project_id"] }
                                        ]
                                    }
                                }
                            }
                        ],
                        "as": "matched_findings"
                    }
                },
                {
                    "$lookup": {
                        "from": "ManualComplianceEvaluation",
                        "let": {
                            "compliance_id": "$_id",
                            "project_id": project_id
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            { "$eq": ["$compliance_id", "$$compliance_id"] },
                                            { "$eq": ["$project_id", "$$project_id"] }
                                        ]
                                    }
                                }
                            }
                        ],
                        "as": "manual_compliance_evaluation"
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
    
    def fetch_compliance_summary(self, project_id) -> dict:
        """
        Fetch compliance summary grouped by compliance_type for a given project_id.
        """
        verify_jwt_in_request()

        try:
            pipeline = [
                {
                    "$lookup": {
                        "from": "ComplianceScannerMapping",
                        "localField": "_id",
                        "foreignField": "compliance_id",
                        "as": "compliance_scanner_mapping"
                    }
                },
                {
                    "$unwind": {
                        "path": "$compliance_scanner_mapping",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$lookup": {
                        "from": "ScannerTypes",
                        "localField": "compliance_scanner_mapping.scanner_type_id",
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
                    "$lookup": {
                        "from": "ManualComplianceEvaluation",
                        "let": {
                            "compliance_id": "$_id",
                            "project_id": project_id
                        },
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$compliance_id", "$$compliance_id"]},
                                            {"$eq": ["$project_id", "$$project_id"]}
                                        ]
                                    }
                                }
                            }
                        ],
                        "as": "manual_compliance_evaluation"
                    }
                },
                {
                    "$group": {
                        "_id": "$compliance_type",
                        "total_count": {"$sum": 1},
                        "non_complying_count": {
                            "$sum": {
                                "$cond": {
                                    "if": {
                                        "$or": [
                                            {"$gt": [{"$size": "$matched_findings"}, 0]},
                                            {
                                                "$gt": [
                                                    {
                                                        "$size": {
                                                            "$filter": {
                                                                "input": "$manual_compliance_evaluation",
                                                                "as": "eval",
                                                                "cond": {"$eq": ["$$eval.evaluation_status", "not-complying"]}
                                                            }
                                                        }
                                                    },
                                                    0
                                                ]
                                            }
                                        ]
                                    },
                                    "then": 1,
                                    "else": 0
                                }
                            }
                        },
                        "complying_count": {
                            "$sum": {
                                "$cond": {
                                    "if": {
                                        "$gt": [
                                            {
                                                "$size": {
                                                    "$filter": {
                                                        "input": "$manual_compliance_evaluation",
                                                        "as": "eval",
                                                        "cond": {"$eq": ["$$eval.evaluation_status", "complying"]}
                                                    }
                                                }
                                            },
                                            0
                                        ]
                                    },
                                    "then": 1,
                                    "else": 0
                                }
                            }
                        }
                    }
                },
                {
                    "$project": {
                        "compliance_type": "$_id",
                        "_id": 0,
                        "non_complying_count": 1,
                        "complying_count": 1,
                        "manual_evaluation_needed_count": {
                            "$subtract": [
                                "$total_count",
                                {"$add": ["$non_complying_count", "$complying_count"]}
                            ]
                        }
                    }
                }
            ]

            compliance_summary = list(Compliance.objects.aggregate(*pipeline))

            return {'success': 'Summary fetched successfully', 'data': compliance_summary}, 200

        except Exception as e:
            return {'error': str(e)}, 500


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
        
    def fetch_all(self) -> List[dict]:
        """
        Fetches all Compliance records from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()

        try:
            pipeline = [
                {
                    "$project": {
                        "isdeleted": 0  
                    }
                }
            ]

            compliance_list = list(Compliance.objects.aggregate(*pipeline))

            return {'success': 'Records fetched successfully', 'data': compliance_list}, '200 Ok'

        except DoesNotExist as e:
            return {'error': 'No records found: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'


    def add_entity(self, request) -> dict:
        """
        Creates new project obj in database
        """
        # Fetching user id from jwt token and validate jwt token
        # current_user = get_current_user_from_jwt_token()
        request_json = request.get_json()
        compliance_type = None
        if 'compliance_type' in request_json:
            compliance_type = request_json.get('compliance_type', None)
        compliance_control_name = None
        if 'compliance_control_name' in request_json:
            compliance_control_name = request_json.get('compliance_control_name', None)
        compliance_group_name = None
        if 'compliance_group_name' in request_json:
            compliance_group_name = request_json.get('compliance_group_name', None)
        compliance_subset_name = None
        if 'compliance_subset_name' in request_json:
            compliance_subset_name = request_json.get('compliance_subset_name', None)
        try:
            for record in request_json:
                new_compliance_obj = Compliance(
                    compliance_id=str(uuid.uuid4()),
                    compliance_type=compliance_type,  
                    compliance_control_name=compliance_control_name, 
                    compliance_group_name=compliance_group_name, 
                    compliance_subset_name=compliance_subset_name,
                    created=datetime.now(timezone.utc),
                    # creator=current_user,
            )
            new_compliance_obj.save()
            response = json.loads(new_compliance_obj.to_json())
            return {'success': 'Record Created Successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
        
        
        
    def update_entity(self, compliance_id: str, request_json: dict) -> tuple:
        print("Request JSON received:", request_json)
        try:
            if not request_json or not isinstance(request_json, dict):
                return {'error': 'Request body is invalid or empty'}, 400
            updated_data = {k: v for k, v in request_json.items() if v is not None}
            if not updated_data:
                return {'error': 'No valid fields provided for update'}, 400
            compliance_record = Compliance.objects.get(compliance_id=compliance_id)
            compliance_record.update(**updated_data)
            updated_record = Compliance.objects.get(compliance_id=compliance_id)
            response = json.loads(updated_record.to_json())
            return response, 200
        except Compliance.DoesNotExist:
            return {'error': f'Compliance record with ID {compliance_id} not found'}, 404
        except Exception as e:
            print(f"Unexpected error occurred while saving: {e}")
            return {'error': f'Unexpected error: {str(e)}'}, 500




    def delete_entity(self, compliance_id) -> dict:
        try:
            compliance_record = Compliance.objects.get(compliance_id=compliance_id)
            compliance_record.delete()
            return {'message': 'Compliance successfully deleted'}, 200
        except Compliance.DoesNotExist:
            return {'error': 'Compliance ID not found'}, 404
        except Exception as e:
            print(f"Unexpected error occurred while deleting: {e}")
            return {'error': f'Unexpected error: {str(e)}'}, 500


