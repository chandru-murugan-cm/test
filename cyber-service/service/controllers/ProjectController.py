from controllers.util import get_current_user_from_jwt_token
from entities.CyberServiceEntity import Project, Scanners, Repository, Scheduler
from typing import List
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from mongoengine import *
from marshmallow import Schema, fields, ValidationError, INCLUDE
from datetime import datetime, timezone
import uuid
import json
from bson import ObjectId


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


class ProjectAddSchema(Schema):
    domain_value = fields.String(required=True, error_messages={
        "required": "Domain Value is required."})
    organization = fields.String(required=True, error_messages={
                                 "required": "Organization is required."})
    name = fields.String(required=True, error_messages={
                         "required": "Name is required."})
    description =fields.String(null=True)
    

class ProjectUpdateSchema(Schema):
    _id = fields.String(required=True, error_messages={
        "required": "Project ID is required."})

    organization = fields.String(required=True, error_messages={
                                 "required": "Organization is required."})
    status = fields.String(required=True, error_messages={
        "required": "Status is required."})
    name = fields.String(required=True, error_messages={
                         "required": "Name is required."})
    description =fields.String(null=True)
   


class ProjectController:
    """
    Defines controller methods for the Project Entity.
    """

    def __init__(self) -> None:
        pass

    def _validateProjectAdd(self, request_json):
        schema = ProjectAddSchema()
        try:
            schema.load(request_json, unknown=INCLUDE)
        except ValidationError as err:
            return False, err.messages, '400 Bad Request'
        return True, {'message': 'validation successful'}, '200 Ok'

    def _validateProjectUpdate(self, request_json):
        schema = ProjectUpdateSchema()
        try:
            schema.load(request_json, unknown=INCLUDE)
        except ValidationError as err:
            return False, err.messages, '400 Bad Request'
        return True, {'message': 'validation successful'}, '200 Ok'

    def _validateProject(self, project_id):
        """
        Validates project id with database
        """
        try:
            Project.objects.get(project_id=project_id)
            return True, {'message': 'Record exists in db'}, '200 Ok'
        except DoesNotExist as e:
            return False, {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return False, {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def _getorganizationproject(self, org_id):
        """
        Validates Organization based Project list
        """
        try:
            org_interv_objs = Project.objects.filter(
                organization=org_id).only("project_id")
            org_interv_ids_list = [str(obj.project_id)
                                   for obj in org_interv_objs]
            return True, org_interv_ids_list, '200 Ok'
        except DoesNotExist as e:
            return False, {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return False, {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def _getcreatorproject(self, current_user):
        """
        Get Creator based project list
        """
        try:
            creator_project_objs = Project.objects.filter(
                creator=current_user).only("project_id")
            creator_project_ids_list = [
                str(obj.project_id) for obj in creator_project_objs]
            return True, creator_project_ids_list, '200 Ok'
        except DoesNotExist as e:
            return False, {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return False, {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def _get_repo_url_from_target_repository(self, project_id):
        """
        Fetch the repo_url from the TargetRepository collection where the project_id matches.
        """
        try:
            repo_docs = Repository.objects.filter(project_id=project_id).only("repo_url")
            repo_urls = [doc.repo_url for doc in repo_docs]
            return repo_urls
        except DoesNotExist as e:
            return None, {'error': 'Repo URL not found in TargetRepository for project_id: ' + str(project_id)}, '404 Not Found'
        except ValidationError as e:
            return None, {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    pipeline = [
        {
            "$match": fields  # Additional match condition (if any) passed through the request
        },
        {
            "$lookup": {
                "from": "TargetRepository",  # Join with the TargetRepository collection
                "let": {"project_id": "$_id"},  # Define local variable
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$eq": ["$project_id", "$$project_id"]  # Match project_id
                            }
                        }
                    }
                ],
                "as": "repo_url_data"
            }
        },
        {
            "$lookup": {
                "from": "TargetDomain", 
                "let": {"project_id": "$_id"}, 
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$eq": ["$project_id", "$$project_id"]  # Match project_id
                            }
                        }
                    }
                ],
                "as": "domain_data"  # This will add the domain data to the result
            }
        },
        {
            "$lookup": {
                "from": "TargetContract",
                "let": {"project_id": "$_id"},  # Define local variable
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$eq": ["$project_id", "$$project_id"]  # Match project_id
                            }
                        }
                    }
                ],
                "as": "contract_data"  # This will add the contract data to the result
            }
        },
        {
            "$addFields": {
                "repo_url": {
                    "$arrayElemAt": ["$repo_url_data.repo_url", 0]  # Extract first repo_url
                },
                "domain_info": {
                    "$arrayElemAt": ["$domain_data.domain_value", 0]  # Extract first domain value
                },
                "contract_info": {
                    "$arrayElemAt": ["$contract_data.contract_info", 0]  # Extract first contract value
                }
            }
        },
        {
            "$project": {
                "isdeleted": 0  # Exclude the "isdeleted" field from the result
            }
        }
    ]

    def fetch_all(self, request, fields) -> List[dict]:
        """
        Fetches all the project objects from the database, with repo_url from TargetRepository,
        filtered first by creator (current user).
        """
        verify_jwt_in_request()
        claims = get_jwt()
        is_admin = claims.get('role') == 'admin'
        current_user = get_current_user_from_jwt_token()
        
        # Filter projects by creator (current user)
        if is_admin:
            creator_filter = {}
        else:
            creator_filter = {"creator": current_user}  # Filter for projects created by the current user
        
        # First, filter the projects based on the creator (current user)
        try:
            filtered_projects = Project.objects.filter(**creator_filter)  # Get the projects for the current user
        except DoesNotExist as e:
            return {'error': 'No projects found for the current user.'}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        # After filtering the projects, apply the aggregation pipeline
        pipeline = [
        {
            "$match": fields  # Additional match condition (if any) passed through the request
        },
        {
            "$lookup": {
                "from": "TargetRepository",  # Join with the TargetRepository collection
                "let": {"project_id": "$_id"},  # Define local variable
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    { "$eq": ["$project_id", "$$project_id"] },  # Match project_id
                                    { "$eq": ["$isdeleted", None] }  
                                ]
                            }
                        }
                    }
                ],
                "as": "repo_url_data"
            }
        },
        {
            "$lookup": {
                "from": "TargetDomain",  # Join with the TargetDomain collection
                "let": {"project_id": "$_id"},  # Define local variable
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    { "$eq": ["$project_id", "$$project_id"] },  # Match project_id
                                    { "$eq": ["$isdeleted", None] }  
                                ]
                            }
                        }
                    }
                ],
                "as": "domain_data"  # This will add the domain data to the result
            }
        },
        {
            "$lookup": {
                "from": "TargetContract",  # Join with the TargetContract collection
                "let": {"project_id": "$_id"},  # Define local variable
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    { "$eq": ["$project_id", "$$project_id"] },  # Match project_id
                                    { "$eq": ["$isdeleted", None] }  # Check if isdeleted is null
                                ]
                            }
                        }
                    }
                ],
                "as": "contract_data"  # This will add the contract data to the result
            }
        },
        {
            "$lookup": {
                "from": "TargetAzureCloud",  
                "let": {"project_id": "$_id"},  
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    { "$eq": ["$project_id", "$$project_id"] },  
                                    { "$eq": ["$isdeleted", None] }  
                                ]
                            }
                        }
                    }
                ],
                "as": "azure_cloud_data"  
            }
        },
        {
            "$lookup": {
                "from": "TargetGoogleCloud",  
                "let": {"project_id": "$_id"},  
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    { "$eq": ["$project_id", "$$project_id"] },  
                                    { "$eq": ["$isdeleted", None] }  
                                ]
                            }
                        }
                    }
                ],
                "as": "google_cloud_data"  
            }
        },
        {
            "$addFields": {
                "repo_url": {
                    "$arrayElemAt": ["$repo_url_data.repo_url", 0]  # Extract first repo_url
                },
                "domain_info": {
                    "$arrayElemAt": ["$domain_data.domain_value", 0]  # Extract first domain value
                },
                "contract_info": {
                    "$arrayElemAt": ["$contract_data.contract_info", 0]  # Extract first contract value
                },
                "azure_cloud_info": {
                    "$arrayElemAt": ["$azure_cloud_data.azure_cloud_info", 0]  
                }
            }
        },
        {
            "$project": {
                "isdeleted": 0  # Exclude the "isdeleted" field from the result
            }
        }
    ]

        
        # Execute the aggregation pipeline after filtering projects by creator
        try:
            project_list = list(filtered_projects.aggregate(pipeline))  # Apply the aggregation on the filtered projects
            response = project_list
            response = serialize_mongo_data(response)
            return {'success': 'Records Fetched Successfully', 'data': response}, '200 Ok'
        except Exception as e:
            return {'error': str(e)}, '500 Internal Server Error'



    def update_by_id(self, request_json) -> dict:
        """
        Updates a project object by its ID, updating only the fields provided in the request,
        and returns the updated project with repo_url information.
        """
        # Fetching user id from JWT token and validate JWT token
        current_user = get_current_user_from_jwt_token()

        # Parse the incoming request JSON
        request_json = request.get_json()
        
        # Validate the incoming request data
        status, result, status_code = self._validateProjectUpdate(request_json)
        if not status:
            return jsonify(result), status_code

        # Validate project ID
        project_id = request_json.get('_id')
        if not project_id or not project_id.strip():
            return {'error': 'Invalid Project ID'}, '400 Bad Request'

        try:
            # Fetch the project from the database
            project_obj = Project.objects.get(project_id=project_id)

            # Update fields only if they are present in the request
            for field in ['organization', 'status', 'name', 'description']:
                if field in request_json:
                    project_obj[field] = request_json[field]

            # Update metadata
            project_obj['updator'] = current_user
            project_obj['updated'] = datetime.now(timezone.utc)

            # Save changes
            project_obj.save()

            # Apply the aggregation pipeline to fetch repo_url data
            pipeline = [
            {
                "$match": {
                    "_id": project_obj.id  # Match the project by its ID
                }
            },
            {
                "$lookup": {
                    "from": "TargetRepository",  # Join with the TargetRepository collection
                    "let": {"project_id": "$_id"},  # Define local variable
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$eq": ["$project_id", "$$project_id"]  # Match project_id
                                }
                            }
                        }
                    ],
                    "as": "repo_url_data"
                }
            },
            {
                "$lookup": {
                    "from": "TargetDomain",  # Join with the TargetDomain collection
                    "let": {"project_id": "$_id"},  # Define local variable
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$eq": ["$project_id", "$$project_id"]  # Match project_id
                                }
                            }
                        }
                    ],
                    "as": "domain_data"  # This will add the domain data to the result
                }
            },
            {
            "$lookup": {
                "from": "TargetContract",  # Join with the TargetContract collection
                "let": {"project_id": "$_id"},  # Define local variable
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$eq": ["$project_id", "$$project_id"]  # Match project_id
                            }
                        }
                    }
                ],
                "as": "contract_data"  # This will add the contract data to the result
            }
            },
            {
                "$addFields": {
                    "repo_url": {
                        "$arrayElemAt": ["$repo_url_data.repo_url", 0]  # Extract first repo_url
                    },
                    "domain_info": {
                        "$arrayElemAt": ["$domain_data.domain_value", 0]  # Extract first domain value
                    },
                    "contract_info": {
                    "$arrayElemAt": ["$contract_data.contract_info", 0]  # Extract first domain value
                    }
                }
            },
            {
                "$project": {
                    "isdeleted": 0  # Exclude the "isdeleted" field from the result
                }
            }
        ]


            # Run the aggregation pipeline on the updated project
            updated_project = list(Project.objects.aggregate(pipeline))

            # Check if the project was found and return the updated response
            if updated_project:
                response = updated_project[0]  # Assuming a single result
                response = serialize_mongo_data(response)
                return {'success': 'Record Updated Successfully', 'data': response}, '200 Ok'
            else:
                return {'error': 'Project not found after update'}, '404 Not Found'

        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def add_entity(self, request_json) -> dict:
        """
        Creates new project obj in database
        """
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()

        request_json = request.get_json()
        status, result, status_code = self._validateProjectAdd(
            request_json)
        if not status:
            return jsonify(result), status_code

        organization = None
        if 'organization' in request_json:
            organization = request_json['organization']

        name = None
        if 'name' in request_json:
            name = request_json['name']

        description = None
        if 'description' in request_json:
            description = request_json['description']


        try:
            new_project_obj = Project(project_id=str(uuid.uuid4()),
                                      user_id=current_user,
                                      organization=organization,
                                      status="init",
                                      name=name,
                                      description=description,
                                      created=datetime.now(timezone.utc),
                                      creator=current_user,
                                      )
            new_project_obj.save()
            response = json.loads(new_project_obj.to_json())
            response = serialize_mongo_data(response)
            return {'success': 'Record Created Successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def remove_entity(self, project_id):
        """
        Removes the Project object from the database.
        """
        # Validates the JWT Token
        verify_jwt_in_request()
        try:
            project_obj = Project.objects.get(
                project_id=project_id)
            project_obj.soft_delete()
            return {'success': 'Record Deleted Successfully'}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
