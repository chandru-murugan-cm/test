from controllers.util import *
from entities.CyberServiceEntity import Scheduler
from typing import List
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request
from mongoengine import *
from marshmallow import Schema, fields, ValidationError, INCLUDE
from datetime import datetime, timezone
import uuid
import json


class UnformattedScanResultsControllerAddSchema(Schema):
    scheduler_id = fields.String(required=True, error_messages={
        "required": "Scheduler ID is required."})
    scan_output = fields.String(required=True, error_messages={
        "required": "Scan Output is required."})


class UnformattedScanResultsControllerUpdateSchema(Schema):
    _id = fields.String(required=True, error_messages={
        "required": "Unformatted Scan Results ID is required."})
    scheduler_id = fields.String(required=True, error_messages={
        "required": "Scheduler ID is required."})
    scan_output = fields.String(required=True, error_messages={
        "required": "Scan Output is required."})


class UnformattedScanResultsController:
    """
    Defines controller methods for the Unformatted Scan Output entity.
    """

    def __init__(self) -> None:
        pass

    def _validateUnformattedScanOutputAdd(self, request_json):
        schema = UnformattedScanResultsControllerAddSchema()
        try:
            schema.load(request_json, unknown=INCLUDE)
        except ValidationError as e:
            return False, e.message, '400 Bad Request'
        return True, {'message': 'Validation successful'}, '200 Ok'

    def _validateUnformattedScanOutputUpdate(self, request_json):
        schema = UnformattedScanResultsControllerUpdateSchema()
        try:
            schema.load(request_json, unknown=INCLUDE)
        except ValidationError as e:
            return False, e.message, '400 Bad Request'
        return True, {'message': 'Validation Successful'}, '200 Ok'

    def _validateUnformattedScanOutput(self, unformatted_scan_id):
        """"
        Validates the scan id with database
        """
        try:
            Unformatted_scan_results.objects.get(
                unformatted_scan_results_id=unformatted_scan_id)
            return True, {'message': 'Record exists in db'}, '200 Ok'
        except DoesNotExist as e:
            return False, {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return False, {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_all(self, request, fields) -> List[dict]:
        """
        Fetches all the unformatted scan results objects from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()

        try:
            pipeline = [
                {
                    "$match": fields
                },
                {
                    "$lookup": {
                        "from": "Scheduler",
                        "localField": "scheduler_id",
                        "foreignField": "_id",
                        "as": "scheduler_info"
                    }
                },
                {
                    "$project": {
                        "isdeleted": 0
                    }
                }
            ]

            # Execute the aggregation pipeline
            unformatted_scan_results_list = list(
                Unformatted_scan_results.objects.aggregate(*pipeline))

            return {'success': 'Records fetched successfully', 'data': unformatted_scan_results_list}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_refined_scan_results_for_unformatted_id(self, fields) -> List[dict]:
        """
        Fetches all the unformatted and refined scan results objects from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()
        if "unformatted_scan_id" in fields:
            unformatted_scan_id = fields['unformatted_scan_id']

        try:
            pipeline = [
                {
                    "$match": {
                        "_id": unformatted_scan_id
                    }
                },
                {
                    "$lookup": {
                        "from": "Scheduler",
                        "localField": "scheduler_id",
                        "foreignField": "_id",
                        "as": "scheduler_info"
                    }
                },
                {
                    "$unwind": {
                        "path": "$scheduler_info",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$lookup": {
                        "from": "Scanners",
                        "localField": "scheduler_info.scanner_ids_list",
                        "foreignField": "_id",
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
                    "$group": {
                        "_id": "$_id",
                        "status": {"$first": "$scheduler_info.status"},
                        "created": {"$first": "$created"},
                        "unformatted_scan_results_id": {"$first": "$_id"},
                        "scanner_categories": {"$addToSet": "$scanner_details.type"}
                    }
                },
                {
                    "$lookup": {
                        "from": "Refined_scan_results",
                        "localField": "unformatted_scan_results_id",
                        "foreignField": "unformatted_scan_results_id",
                        "as": "refined_scan_output"
                    }
                },
                {
                    "$unwind": {
                        "path": "$refined_scan_output",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "findings": "$refined_scan_output.finding",
                        "target": "$refined_scan_output.target",
                        "additional_info": "$refined_scan_output.additional_info",
                        "scan_date": "$refined_scan_output.created",
                        "issue_detail": "$refined_scan_output.issue_detail",
                        "issue_background": "$refined_scan_output.issue_background",
                        "issue_remediation": "$refined_scan_output.issue_remediation",
                        "references": "$refined_scan_output.references",
                        "vulnerability_classifications": "$refined_scan_output.vulnerability_classifications",
                        "severity": "$refined_scan_output.severity",
                        "scanner_categories": {
                            "$reduce": {
                                "input": "$scanner_categories",
                                "initialValue": [],
                                "in": {
                                    "$setUnion": [
                                        "$$value",
                                        {
                                            "$cond": [
                                                {"$isArray": "$$this"},
                                                "$$this",
                                                ["$$this"]
                                            ]
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            ]

            # Execute the aggregation pipeline
            unformatted_scan_results_list = list(
                Unformatted_scan_results.objects.aggregate(*pipeline))

            return {'success': 'Records fetched successfully', 'data': unformatted_scan_results_list}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_refined_scan_results_by_project_id(self, fields) -> List[dict]:
        """
        Fetches all the refined scan results by project id
        """
        # Validate JWT Token
        verify_jwt_in_request()
        if "project_id" in fields:
            project_id = fields['project_id']

            try:
                pipeline = [
                    {
                        "$match": {
                            "project_id": project_id
                        }
                    },
                    {
                        "$lookup": {
                            "from": "Scheduler",
                            "localField": "scheduler_id",
                            "foreignField": "_id",
                            "as": "scheduler_info"
                        }
                    },
                    {
                        "$unwind": {
                            "path": "$scheduler_info",
                            "preserveNullAndEmptyArrays": True
                        }
                    },
                    {
                        "$lookup": {
                            "from": "Scanners",
                            "localField": "scheduler_info.scanner_ids_list",
                            "foreignField": "_id",
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
                        "$group": {
                            "_id": "$_id",
                            "status": {"$first": "$scheduler_info.status"},
                            "created": {"$first": "$created"},
                            "unformatted_scan_results_id": {"$first": "$_id"},
                            "scheduled_date": {"$first": "$scheduler_info.created"},
                            "scanner_types": {"$addToSet": "$scanner_details.type"}
                        }
                    },
                    {
                        "$lookup": {
                            "from": "Refined_scan_results",
                            "localField": "unformatted_scan_results_id",
                            "foreignField": "unformatted_scan_results_id",
                            "as": "refined_scan_output"
                        }
                    },
                    {
                        "$unwind": {
                            "path": "$refined_scan_output",
                            "preserveNullAndEmptyArrays": True
                        }
                    },
                    {
                        "$lookup": {
                            "from": "ZapExtendedOutputs",
                            "let": {"zap_scan_id": "$refined_scan_output._id"},
                            "pipeline": [
                                {
                                    "$match": {
                                        "$expr": {
                                            "$eq": ["$refined_scan_results_id", "$$zap_scan_id"]
                                        }
                                    }
                                }
                            ],
                            "as": "instances"
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "findings": "$refined_scan_output.finding",
                            "target": "$refined_scan_output.target",
                            "additional_info": "$refined_scan_output.additional_info",
                            "scan_date": "$refined_scan_output.created",
                            "severity": "$refined_scan_output.severity",
                            "scheduled_date": "$scheduled_date",
                            "issue_detail": "$refined_scan_output.issue_detail",
                            "issue_background": "$refined_scan_output.issue_background",
                            "issue_remediation": "$refined_scan_output.issue_remediation",
                            "references": "$refined_scan_output.references",
                            "vulnerability_classifications": "$refined_scan_output.vulnerability_classifications",
                            "scanner_categories": {
                                "$reduce": {
                                    "input": {
                                        "$filter": {
                                            "input": "$scanner_types",
                                            "as": "type",
                                            "cond": {"$ne": ["$$type", None]}
                                        }
                                    },
                                    "initialValue": [],
                                    "in": {
                                        "$setUnion": [
                                            "$$value",
                                            {
                                                "$cond": [
                                                    {"$isArray": "$$this"},
                                                    "$$this",
                                                    ["$$this"]
                                                ]
                                            }
                                        ]
                                    }
                                }
                            },
                            "instances": {
                                "$cond": {
                                    "if": {"$eq": ["$refined_scan_output.scanner", "ZAP"]},
                                    "then": "$instances",
                                    "else": []
                                }
                            }
                        }
                    },
                    {
                        "$match": {
                            "scanner_categories": {"$ne": []},
                            "findings": {"$exists": True, "$ne": None}
                        }
                    }
                ]

                # Execute the aggregation pipeline
                unformatted_scan_results_list = list(
                    Unformatted_scan_results.objects.aggregate(*pipeline)
                )

                return {'success': 'Records fetched successfully', 'data': unformatted_scan_results_list}, '200 Ok'

            except DoesNotExist as e:
                return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_scanner_details(self, fields) -> List[dict]:
        """
        Fetches all the scan objects based on Project Id from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()
        if "project_id" in fields:
            project_id = fields['project_id']

        try:
            pipeline = [
                {
                    "$match": {
                        "project_id": project_id
                    }
                },
                {
                    "$lookup": {
                        "from": "Scheduler",
                        "localField": "scheduler_id",
                        "foreignField": "_id",
                        "as": "scheduler_info"
                    }
                },
                {
                    "$unwind": {
                        "path": "$scheduler_info",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$lookup": {
                        "from": "Scanners",
                        "localField": "scheduler_info.scanner_ids_list",
                        "foreignField": "_id",
                        "as": "scanner_details"
                    }
                },
                {
                    "$lookup": {
                        "from": "Project",
                        "localField": "project_id",
                        "foreignField": "_id",
                        "as": "project_info"
                    }
                },
                {
                    "$unwind": {
                        "path": "$project_info",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$project": {
                        "project_name": "$project_info.name",
                        "status": "$scheduler_info.status",
                        "scheduled_date": "$scheduler_info.created",
                        "scan_types": {
                            "$reduce": {
                                "input": {
                                    "$map": {
                                        "input": "$scanner_details",
                                        "as": "scanner",
                                        "in": "$$scanner.type"
                                    }
                                },
                                "initialValue": [],
                                "in": {
                                    "$concatArrays": [
                                        "$$value",
                                        {
                                            "$cond": [
                                                {
                                                    "$isArray": "$$this"
                                                },
                                                "$$this",
                                                ["$$this"]
                                            ]
                                        }
                                    ]
                                }
                            }
                        },
                        "created": 1
                    }
                },
                {
                    "$unwind": {
                        "path": "$scan_types",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "unformatted_scan_results_id": "$_id",
                            "project_name": "$project_name",
                            "status": "$status",
                            "scheduled_date": "$scheduled_date",
                            "created": "$created"
                        },
                        "scan_types": {
                            "$addToSet": "$scan_types"
                        }
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "unformatted_scan_results_id": "$_id.unformatted_scan_results_id",
                        "project_name": "$_id.project_name",
                        "status": "$_id.status",
                        "scheduled_date": "$_id.scheduled_date",
                        "unformatted_scan_result_date": "$_id.created",
                        "scan_types": "$scan_types"
                    }
                }
            ]

            # Execute the aggregation pipeline
            unformatted_scan_results_list = list(
                Unformatted_scan_results.objects.aggregate(*pipeline))

            return {'success': 'Records fetched successfully', 'data': unformatted_scan_results_list}, '200 Ok'

        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
            
    def fetch_dashboard_content(self, request, fields) -> List[dict]:
        """
        Fetches the dashboard content for the given refined scan results.
        """
        # Validate JWT Token
        verify_jwt_in_request()
        if "project_id" in fields:
            project_id = fields['project_id']

        try:
            pipeline = [
                {
                    "$match": {
                        "project_id": project_id
                    }
                },
                {
                    "$lookup": {
                        "from": "Refined_scan_results",
                        "localField": "_id",
                        "foreignField": "unformatted_scan_results_id",
                        "as": "refined_results"
                    }
                },
                {
                    "$unwind": "$refined_results"
                },
                {
                    "$group": {
                        "_id": "$project_id",
                        "refined_ids": {
                            "$push": "$refined_results._id"
                        },
                        "severity_counts": {
                            "$push": {
                                "$toLower": "$refined_results.severity"
                            }
                        },
                        "solved_issues": {
                            "$sum": {
                                "$cond": [
                                    {
                                        "$eq": ["$refined_results.scan_status", "Fixed"]
                                    },
                                    1,
                                    0
                                ]
                            }
                        },
                        "new_issues": {
                            "$sum": {
                                "$cond": [
                                    {
                                        "$eq": ["$refined_results.scan_status", "Open"]
                                    },
                                    1,
                                    0
                                ]
                            }
                        },
                        "ignored_issues": {
                            "$sum": {
                                "$cond": [
                                    {
                                        "$eq": ["$refined_results.scan_status", "Ignored"]
                                    },
                                    1,
                                    0
                                ]
                            }
                        }
                    }
                },
                {
                    "$project": {
                        "project_id": "$_id",
                        "_id": 0,
                        "refined_ids": 1,
                        "severity_counts": {
                            "$arrayToObject": {
                                "$map": {
                                    "input": {
                                        "$setUnion": ["$severity_counts", []]
                                    },
                                    "as": "severity",
                                    "in": {
                                        "k": {
                                            "$switch": {
                                                "branches": [
                                                    {
                                                        "case": {
                                                            "$or": [
                                                                {"$eq": [
                                                                    "$$severity", "critical"]},
                                                                {"$eq": [
                                                                    "$$severity", "Critical"]}
                                                            ]
                                                        },
                                                        "then": "Critical"
                                                    },
                                                    {
                                                        "case": {
                                                            "$or": [
                                                                {"$eq": [
                                                                    "$$severity", "high"]},
                                                                {"$eq": [
                                                                    "$$severity", "High"]}
                                                            ]
                                                        },
                                                        "then": "High"
                                                    },
                                                    {
                                                        "case": {
                                                            "$or": [
                                                                {"$eq": [
                                                                    "$$severity", "medium"]},
                                                                {"$eq": [
                                                                    "$$severity", "Medium"]}
                                                            ]
                                                        },
                                                        "then": "Medium"
                                                    },
                                                    {
                                                        "case": {
                                                            "$or": [
                                                                {"$eq": [
                                                                    "$$severity", "low"]},
                                                                {"$eq": [
                                                                    "$$severity", "Low"]}
                                                            ]
                                                        },
                                                        "then": "Low"
                                                    }
                                                ],
                                                "default": "$$severity"
                                            }
                                        },
                                        "v": {
                                            "$size": {
                                                "$filter": {
                                                    "input": "$severity_counts",
                                                    "as": "item",
                                                    "cond": {"$eq": ["$$item", "$$severity"]}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "solved_issues": 1,
                        "new_issues": 1,
                        "ignored_issues": 1
                    }
                }
            ]

            # Execute the aggregation pipeline
            unformatted_scan_results_list = list(
                Unformatted_scan_results.objects.aggregate(*pipeline))

            return {'success': 'Records fetched successfully', 'data': unformatted_scan_results_list}, '200 Ok'

        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def update_by_id(self, request_json) -> dict:
        """"
        Updates the scan result object by id
        """
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()

        request_json = request.get_json()
        status, result, status_code = self._validateUnformattedScanOutputUpdate(
            request_json)
        if not status:
            return jsonify(result), status_code

        unformatted_scan_id = None
        if '_id' in request_json:
            unformatted_scan_id = request_json['_id']
            if request_json['_id'] is None or 0 == len(str(request_json['_id']).strip()):
                pass
            else:
                status, result, status_code = self._validateUnformattedScanOutput(
                    request_json['_id'])
                if not status:
                    return result, status_code

        scheduler_id = None
        if 'scheduler_id' in request_json:
            scheduler_id = request_json['scheduler_id']

        scan_output = None
        if 'scan_output' in request_json:
            scan_output = request_json['scan_output']

        try:
            unformatted_scan_obj = Unformatted_scan_results.objects.get(
                unformatted_scan_results_id=unformatted_scan_id)
            unformatted_scan_obj['scheduler_id'] = scheduler_id
            unformatted_scan_obj['scan_output'] = scan_output
            unformatted_scan_obj['updator'] = current_user
            unformatted_scan_obj['updated'] = datetime.now(timezone.utc)
            unformatted_scan_obj.save()
            response = json.loads(unformatted_scan_obj.to_json())
            return {'success': 'Record updated successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def add_entity(self, request_json) -> dict:
        """
        Creates new scheduler obj in database
        """
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()

        request_json = request.get_json()
        status, result, status_code = self._validateUnformattedScanOutputAdd(
            request_json)
        if not status:
            return jsonify(result), status_code

        scheduler_id = None
        if 'scheduler_id' in request_json:
            scheduler_id = request_json['scheduler_id']

        scan_output = None
        if 'scan_output' in request_json:
            scan_output = request_json['scan_output']

        try:
            new_unformatted_scan_obj = Unformatted_scan_results(unformatted_scan_results_id=str(uuid.uuid4()),
                                                                scheduler_id=scheduler_id,
                                                                scan_output=scan_output,
                                                                created=datetime.now(
                                                                    timezone.utc),
                                                                creator=current_user,
                                                                )
            new_unformatted_scan_obj.save()
            response = json.loads(new_unformatted_scan_obj.to_json())
            return {'success': 'Record created successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def remove_entity(self, unformatted_scan_id):
        """
        Removes the Unformatted scan result object from the database.
        """
        # Validates the JWT Token
        verify_jwt_in_request()
        try:
            unformatted_scan_obj = Unformatted_scan_results.objects.get(
                unformatted_scan_results_id=unformatted_scan_id)
            unformatted_scan_obj.soft_delete()
            return {'success': 'Record Deleted Successfully'}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
