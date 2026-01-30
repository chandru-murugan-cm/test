from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from mongoengine import *
from controllers.util import *
import uuid
from datetime import datetime, timezone
import json
from entities.CyberServiceEntity import FindingMaster, DomainWapiti1, DomainZap1, RepositoryTrivy1,RepoSecretDetections, RepoSmartContractSlither1, CloudCloudSploitAzure1, CloudCloudSploitGoogle1, ScannerTypes
from typing import List
from bson import ObjectId

collection_map = {
    "DomainWapiti1": {"model": DomainWapiti1, "id_field": "domain_wapiti_1_id"},
    "DomainZap1": {"model": DomainZap1, "id_field": "domain_zap_1_id"},
    "RepositoryTrivy1": {"model": RepositoryTrivy1, "id_field": "repository_trivy_1_id"},
    "RepoSmartContractSlither1": {"model": RepoSmartContractSlither1, "id_field": "repo_smart_contract_slither_1_id"},
    "RepoSecretDetections": {"model": RepoSecretDetections, "id_field": "repo_secret_detections_id"},
    "CloudCloudSploitAzure1": {"model": CloudCloudSploitAzure1, "id_field": "cloud_azure_id"},
    "CloudCloudSploitGoogle1": {"model": CloudCloudSploitGoogle1, "id_field": "cloud_google_id"},
    # Add other mappings here as needed
}

def serialize_mongo_data(data):
    """
    Recursively converts ObjectId instances in MongoDB documents to strings.
    """
    if isinstance(data, dict):
        return {key: serialize_mongo_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_mongo_data(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    return data

class FindingMasterController():
    """
    Defines controller methods for the Finding Master Entity.
    """

    def __init__(self) -> None:
        pass


    def add_entity(self, request):
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        request_json = request.get_json()

        project_id = request_json.get('project_id')
        scan_type_id = request_json.get('scan_type_id')
        target_id = request_json.get('target_id')
        extended_finding_details_id = request_json.get(
            'extended_finding_details_id')
        fix_recommendation_id = request_json.get('fix_recommendation_id')
        raw_scan_output_id = request_json.get('raw_scan_output_id')
        finding_name = request_json.get('finding_name')
        finding_desc = request_json.get('finding_desc')
        finding_date = request_json.get('finding_date')
        severity = request_json.get('severity')
        status = request_json.get('status')

        if not project_id:
            return jsonify({"error": "Finding Id not provided"}), 400

        if not scan_type_id:
            return jsonify({"error": "Scan Type Id not provided"}), 400

        if not target_id:
            return jsonify({"error": "Target Id not provided"}), 400

        if not raw_scan_output_id:
            return jsonify({"error": "Raw Scan Output Id not provided"}), 400

        # Creating the Finding Scan Link entry
        finding_master_obj = FindingMaster(
            finding_id=str(uuid.uuid4()),
            project_id=project_id,
            target_id=target_id,
            scan_type_id=scan_type_id,
            extended_finding_details_id=extended_finding_details_id,
            fix_recommendation_id=fix_recommendation_id,
            raw_scan_output_id=raw_scan_output_id,
            finding_name=finding_name,
            finding_desc=finding_desc,
            finding_date=finding_date,
            severity=severity,
            status=status,
            created=datetime.now(timezone.utc),
            creator=current_user,
        )

        # Save the entity to the database
        finding_master_obj.save()
        response = json.loads(finding_master_obj.to_json())
        return jsonify({"message": "Finding Master Entry created successfully", "data": response}), 200

    def fetch_all(self, request, fields) -> List[dict]:
        """
        Fetches all the finding master object from the database.
        """
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        pipeline = [
            {
                "$match": {
                    **fields
                }
            },
            {
                "$project": {
                    "isdeleted": 0
                }
            }
        ]

        # Execute the aggregation pipeline
        finding_scan_link_list = list(
            FindingMaster.objects.aggregate(pipeline))
        response = serialize_mongo_data(finding_scan_link_list)
        return {'success': 'Records Fetched Successfully', 'data': response}, '200 Ok'
    
    def update_status(self, finding_id, request):
        """
        Updates the status field of a FindingMaster entry identified by finding_id.
        Non-admin users can only update their own Manual VAPT findings.
        """
        # Validate JWT Token
        current_user = get_current_user_from_jwt_token()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        # Check for admin role
        claims = get_jwt()
        is_admin = claims.get('role') == 'admin'

        # Parse request data
        request_json = request.get_json()
        new_status = request_json.get('status')


        try:
            # Fetch the FindingMaster entry
            finding_master = FindingMaster.objects.get(finding_id=finding_id)
            if finding_master.isdeleted:
                return jsonify({"error": "Cannot update a deleted record"}), 400

            # For non-admin users, check if this is a Manual VAPT finding they own
            if not is_admin:
                try:
                    scanner_type = ScannerTypes.objects.get(scan_type="Manual VAPT")
                    if finding_master.scan_type_id == scanner_type.scan_type_id:
                        if finding_master.creator != current_user:
                            return jsonify({"error": "You can only update your own Manual VAPT findings"}), 403
                except DoesNotExist:
                    pass

            # Update the status field
            finding_master.status = new_status
            finding_master.updated = datetime.now(timezone.utc)
            finding_master.updator = current_user
            finding_master.save()

            # Return the updated document
            response = json.loads(finding_master.to_json())
            return jsonify({"message": "Status updated successfully", "data": response}), 200

        except DoesNotExist:
            return jsonify({"error": "FindingMaster entry not found"}), 404
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    def get_finding_master_counts(self, project_id):
        """
        Get the count of issues categorized by severity and status for a specific project_id.
        Non-admin users only see counts for their own Manual VAPT findings.
        """
        # Validate JWT Token
        verify_jwt_in_request()
        current_user = get_jwt_identity()

        # Check for admin role
        claims = get_jwt()
        is_admin = claims.get('role') == 'admin'

        try:
            # Build match conditions
            match_conditions = [{"project_id": project_id}]

            # For non-admin users, filter Manual VAPT findings to only count their own
            if not is_admin:
                manual_vapt_scan_type_id = None
                try:
                    scanner_type = ScannerTypes.objects.get(scan_type="Manual VAPT")
                    manual_vapt_scan_type_id = scanner_type.scan_type_id
                except DoesNotExist:
                    pass

                if manual_vapt_scan_type_id:
                    match_conditions.append({
                        "$or": [
                            {"scan_type_id": {"$ne": manual_vapt_scan_type_id}},
                            {"$and": [
                                {"scan_type_id": manual_vapt_scan_type_id},
                                {"creator": current_user}
                            ]}
                        ]
                    })

            # Combine conditions
            match_stage = {"$and": match_conditions} if len(match_conditions) > 1 else match_conditions[0]

            # Define the aggregation pipeline
            pipeline = [
    {
        "$match": match_stage
    },
    {
        "$group": {
            "_id": None,  # Grouping everything together
            "critical_count": {"$sum": {"$cond": [{"$eq": ["$severity", "critical"]}, 1, 0]}},
            "high_count": {"$sum": {"$cond": [{"$eq": ["$severity", "high"]}, 1, 0]}},
            "medium_count": {"$sum": {"$cond": [{"$eq": ["$severity", "medium"]}, 1, 0]}},
            "low_count": {"$sum": {"$cond": [{"$eq": ["$severity", "low"]}, 1, 0]}},
            "informational_count": {"$sum": {"$cond": [{"$eq": ["$severity", "informational"]}, 1, 0]}},
            "open_count": {"$sum": {"$cond": [{"$eq": ["$status", "open"]}, 1, 0]}},
            "closed_count": {"$sum": {"$cond": [{"$eq": ["$status", "closed"]}, 1, 0]}},
            "ignored_count": {"$sum": {"$cond": [{"$eq": ["$status", "ignored"]}, 1, 0]}},
            "false_positive_count": {"$sum": {"$cond": [{"$eq": ["$status", "false positive"]}, 1, 0]}}
        }
    }
]


            # Execute the aggregation pipeline
            result = list(FindingMaster.objects.aggregate(*pipeline))
            print(result)

            # If no results were returned, default the counts to 0
            if not result:
                counts = {
                    "critical_count": 0,
                    "high_count": 0,
                    "medium_count": 0,
                    "low_count": 0,
                    "informational_count": 0,
                    "open_count": 0,
                    "closed_count": 0,
                    "ignored_count": 0,
                    "false_positive_count": 0
                }
            else:
                counts = result[0]  # Extract the count from the aggregation result

            return jsonify({
                "message": "Counts fetched successfully",
                "data": {
                    "severity_counts": {
                        "critical": counts.get('critical_count', 0),
                        "high": counts.get('high_count', 0),
                        "medium": counts.get('medium_count', 0),
                        "low": counts.get('low_count', 0),
                        "informational": counts.get('informational_count', 0),
                    },
                    "status_counts": {
                        "open": counts.get('open_count', 0),
                        "closed": counts.get('closed_count', 0),
                        "ignored": counts.get('ignored_count', 0),
                        "false_positive": counts.get('false_positive_count', 0),
                    }
                }
            }), 200

        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500


    def fetch_by_project_id(self, fields) -> List[dict]:
        """
        Fetches a finding master object by its project_id from the database with pagination.
        Includes additional details for `target_id` and `scan_type_id`.
        Non-admin users can only see their own Manual VAPT findings.
        """
        # Validate JWT Token
        verify_jwt_in_request()
        current_user = get_jwt_identity()

        # Check for admin role
        claims = get_jwt()
        is_admin = claims.get('role') == 'admin'

        if "project_id" in fields:
            project_id = fields['project_id']
            target_type = request.args.get('targetType')
            severity = request.args.get('severity')
            status = request.args.get('status')
            scan_type_ids = request.args.get("scanTypeIds")  # Get comma-separated values as a string
            if scan_type_ids:
                scan_type_ids = scan_type_ids.split(",")  # Convert to list
            order_by = request.args.get('orderBy', 'finding_date')
            order_direction = request.args.get('orderDirection', 'desc')

            try:
                # Fetch pagination parameters
                page = int(request.args.get('page', 1))
                limit = int(request.args.get('limit', 10))
                skip = (page - 1) * limit

                # Build match conditions
                match_conditions = [{"project_id": project_id}]

                # For non-admin users, filter Manual VAPT findings to only show their own
                if not is_admin:
                    # Get the Manual VAPT scanner type ID
                    manual_vapt_scan_type_id = None
                    try:
                        scanner_type = ScannerTypes.objects.get(scan_type="Manual VAPT")
                        manual_vapt_scan_type_id = scanner_type.scan_type_id
                    except DoesNotExist:
                        pass  # No Manual VAPT type exists yet

                    if manual_vapt_scan_type_id:
                        # Show findings that are either:
                        # 1. NOT Manual VAPT findings, OR
                        # 2. Manual VAPT findings created by the current user
                        match_conditions.append({
                            "$or": [
                                {"scan_type_id": {"$ne": manual_vapt_scan_type_id}},
                                {"$and": [
                                    {"scan_type_id": manual_vapt_scan_type_id},
                                    {"creator": current_user}
                                ]}
                            ]
                        })

                # Apply filters if any
                if target_type:
                    match_conditions.append({"target_type": target_type})
                if severity:
                    match_conditions.append({"severity": severity})
                if status:
                    match_conditions.append({"status": status})
                if scan_type_ids:
                    match_conditions.append({"scan_type_id": {"$in": scan_type_ids}})

                # Combine all conditions with $and
                match_stage = {"$and": match_conditions} if len(match_conditions) > 1 else match_conditions[0]

                # Determine sorting direction
                sort_direction = 1 if order_direction == 'asc' else -1

                pipeline = [
                    {
                        "$match": match_stage  # Apply the match stage with filters
                    },
                    {
                        "$lookup": {
                            "from": "TargetDomain",
                            "localField": "target_id",
                            "foreignField": "_id",
                            "as": "target_domain_details"
                        }
                    },
                    {
                        "$lookup": {
                            "from": "TargetRepository",
                            "localField": "target_id",
                            "foreignField": "_id",
                            "as": "target_repository_details"
                        }
                    },
                    {
                        "$lookup": {
                            "from": "TargetContract",
                            "localField": "target_id",
                            "foreignField": "_id",
                            "as": "target_contract_details"
                        }
                    },
                    {
                        "$lookup": {
                            "from": "TargetAzureCloud",
                            "localField": "target_id",
                            "foreignField": "_id",
                            "as": "target_azure_cloud_details"
                        }
                    },
                    {
                        "$lookup": {
                            "from": "TargetGoogleCloud",
                            "localField": "target_id",
                            "foreignField": "_id",
                            "as": "target_google_cloud_details"
                        }
                    },
                    # Combine the target details into one field
                    {
                        "$addFields": {
                            "target_details": {
                                "$cond": {
                                    "if": {"$gt": [{"$size": "$target_domain_details"}, 0]},
                                    "then": {"$arrayElemAt": ["$target_domain_details", 0]},
                                    "else": {
                                        "$cond": {
                                            "if": {"$gt": [{"$size": "$target_repository_details"}, 0]},
                                            "then": {"$arrayElemAt": ["$target_repository_details", 0]},
                                            "else": {
                                                "$cond": {
                                                    "if": {"$gt": [{"$size": "$target_contract_details"}, 0]},
                                                    "then": {"$arrayElemAt": ["$target_contract_details", 0]},
                                                    "else": {
                                                        "$cond": {
                                                            "if": {"$gt": [{"$size": "$target_azure_cloud_details"}, 0]},
                                                            "then": {"$arrayElemAt": ["$target_azure_cloud_details", 0]},
                                                            "else": {"$arrayElemAt": ["$target_google_cloud_details", 0]}
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    # Lookup details for scan_type_id from ScannerTypes collection
                    {
                        "$lookup": {
                            "from": "ScannerTypes",
                            "localField": "scan_type_id",
                            "foreignField": "_id",
                            "as": "scan_type_details"
                        }
                    },
                    # Flatten scan_type_details array
                    {
                        "$addFields": {
                            "scan_type_details": {
                                "$arrayElemAt": ["$scan_type_details", 0]
                            }
                        }
                    },
                    # Sort by the specified field (finding_date by default)
                    {
                        "$sort": {
                            order_by: sort_direction  # Sort by finding_date, severity, or status
                        }
                    },
                    {
                        "$project": {
                            "isdeleted": 0,
                            "target_domain_details": 0,
                            "target_repository_details": 0,
                            "target_azure_cloud_details": 0,
                            "target_google_cloud_details": 0,
                            "target_contract_details": 0,
                        }
                    },
                    {"$skip": skip},
                    {"$limit": limit}
                ]

                # Execute the aggregation pipeline
                finding_master_results_list = list(FindingMaster.objects.aggregate(*pipeline))

                # Count total documents for pagination metadata using aggregation
                count_pipeline = [
                    {"$match": match_stage},
                    {"$count": "total"}
                ]
                count_result = list(FindingMaster.objects.aggregate(*count_pipeline))
                total_count = count_result[0]["total"] if count_result else 0

                return {
                    'success': 'Records fetched successfully',
                    'data': serialize_mongo_data(finding_master_results_list),
                    'pagination': {
                        'page': page,
                        'limit': limit,
                        'total': total_count,
                        'total_pages': (total_count + limit - 1) // limit
                    }
                }, '200 Ok'

            except DoesNotExist as e:
                return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    
    def get_extended_finding_details(self, finding_id):
        try:
            # Fetch the FindingMaster document using the finding_id
            finding_master = FindingMaster.objects.get(finding_id=finding_id)
            
            if not finding_master:
                return {"error": "FindingMaster not found"}, 404
            
            # Get the collection name and details_id from the FindingMaster document
            collection_name = finding_master.extended_finding_details_name
            details_id = finding_master.extended_finding_details_id

            # Fetch the model class and ID field for the collection name using the map
            collection_info = collection_map.get(collection_name)
            
            if collection_info is None:
                return {"error": "Related collection not found"}, 404
            
            # Retrieve the appropriate collection model and ID field name
            dynamic_collection = collection_info["model"]
            id_field = collection_info["id_field"]

            # Fetch the related details from the dynamic collection using the correct ID field
            related_details = dynamic_collection.objects(**{id_field: details_id}).first()
            
            if not related_details:
                return {"error": "Related details not found in the collection"}, 404

            # Prepare the response with the found data
            response = {
                "message": "Record fetched successfully",
                "data": {
                    "finding_master": json.loads(serialize_mongo_data(finding_master.to_json())),  # Parse to JSON object
                    "extended_details": json.loads(serialize_mongo_data(related_details.to_json())),  # Parse to JSON object
                    "collection_name": collection_name  # Add collection_name as part of the response
                }
            }

            return response, 200

        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}, 500


    def has_findings_bulk(self, request):
        """
        Checks for findings across multiple target IDs.
        """
        # Validate JWT Token
        current_user = get_current_user_from_jwt_token()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        # Parse request body
        request_json = request.get_json()
        target_ids = request_json.get('target_ids', [])

        # Validate input
        if not target_ids or not isinstance(target_ids, list):
            return jsonify({"error": "Invalid target IDs provided"}), 400

        try:
            # Query findings for the provided target IDs
            findings = FindingMaster.objects(
                target_id__in=target_ids,
            ).distinct('target_id')

            # Prepare response as a map
            result = {target_id: target_id in findings for target_id in target_ids}
            return jsonify(serialize_mongo_data(result)), 200

        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
