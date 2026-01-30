from controllers.util import *
from entities.CyberServiceEntity import Repository, FindingMaster, LanguagesAndFramework, RepoSecretDetections, FixRecommendations, RepositoryTrivy1, FindingSBOMVulnerability, FindingLicense
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request
from mongoengine import *
from marshmallow import Schema, fields, ValidationError, INCLUDE, validates, validates_schema
from datetime import datetime, timezone
from typing import List
from bson import ObjectId
import uuid
import json
from enum import Enum

class RepositoryProvider(Enum):
    GITLAB = "gitlab"
    GITHUB = "github"
    NOT_APPLICABLE = "not_applicable"

class RepositoryAddSchema(Schema):
    project_id = fields.String(required=True, error_messages={
        "required": "Project ID is required."})
    repository_url = fields.String(required=True, error_messages={
        "required": "Repository URL is missing."})
    repository_label = fields.String(null=True)
    is_private_repo = fields.Boolean(default=False)
    access_token = fields.String(null=True)
    repository_provider = fields.String(required=True, error_messages={"required": "Repository provider is missing."})


    # Checks that the repository_provider has one of the supported values
    @validates("repository_provider")
    def validate_repository_provider(self, provider, **kwargs):
        if provider not in RepositoryProvider._value2member_map_:
            raise ValidationError(f"Unsupported provider: {provider}")
        

    # Checks that the repository provider is consistent with the visibility of the repo
    # public => not-applicable
    # private => NOT not-applicable => gitlab / github
    @validates_schema
    def validate_repository_provider_consistency(self, data, **kwargs):
        # Retrieve the data necessary for validation
        is_private_repo = data.get("is_private_repo")
        repository_provider = data.get("repository_provider")

        # repo is public 
        if not is_private_repo and repository_provider != RepositoryProvider.NOT_APPLICABLE.value:
            raise ValidationError("Public repositories must have 'not_applicable' as repository_provider")
        
        # repo is private
        if is_private_repo and repository_provider == RepositoryProvider.NOT_APPLICABLE.value:
            raise ValidationError("Private repositories must have a real repository_provider (GitHub / GitLab)")



class RepositoryUpdateSchema(Schema):
    repository_url = fields.String(required=True, error_messages={
        "required": "Repository URL is missing."})
    repository_label = fields.String(null=True)
    is_private_repo = fields.Boolean(default=False)
    access_token = fields.String(null=True)
    repository_provider = fields.String(required=True)

class RepositoryController:
    """
    Defines controller methods for the Repository Entity.
    """

    def __init__(self) -> None:
        pass

    def _validateRepositoryAdd(self, request_json):
        schema = RepositoryAddSchema()
        try:
            schema.load(request_json, unknown=INCLUDE)
        except ValidationError as err:
            return False, err.messages, '400 Bad Request'
        return True, {'message': 'Validation successful'}, '200 Ok'

    def _validateRepositoryUpdate(self, request_json):
        schema = RepositoryUpdateSchema()
        try:
            schema.load(request_json, unknown=INCLUDE)
        except ValidationError as err:
            return False, err.messages, '400 Bad Request'
        return True, {'message': 'Validation successful'}, '200 Ok'

    def _validateRepository(self, repository_id):
        """
        Validates repository id with the database.
        """
        try:
            Repository.objects.get(target_repository_id=repository_id)
            return True, {'message': 'Record exists in db'}, '200 Ok'
        except DoesNotExist as e:
            return False, {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return False, {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_all(self, request, fields) -> List[dict]:
        """
        Fetches all the repository objects from the database.
        """
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()

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
        repo_list = list(Repository.objects.aggregate(pipeline))
        response = repo_list
        return {'success': 'Records Fetched Successfully', 'data': response}, '200 Ok'

    def update_by_id(self, request, target_repository_id) -> dict:
        """
        Updates a repository object by its ID, updating only the fields provided in the request.
        """
        # Fetching user id from JWT token and validate JWT token
        current_user = get_current_user_from_jwt_token()

        # Get the JSON data from the request
        request_json = request.get_json()

        # Validate the repository update
        status, result, status_code = self._validateRepositoryUpdate(request_json)
        if not status:
            return jsonify(result), status_code

        # Validate repository ID
        if target_repository_id != request_json.get('target_repository_id'):
            return {'error': 'Repository ID in URL does not match the provided target_repository_id in the body'}, '400 Bad Request'
        print(f"Repository ID mismatch: URL ID ({target_repository_id}) != Body ID ({request_json.get('target_repository_id')})")
        try:
            # Fetch the repository from the database
            repository_obj = Repository.objects.get(target_repository_id=target_repository_id)

            

            # Update fields only if they are present in the request
            for field in ['project_id', 'repository_url','repository_label', 'is_private_repo', 'access_token']:
                if field in request_json:
                    repository_obj[field] = request_json[field]

            # Update metadata
            repository_obj['updator'] = current_user
            repository_obj['updated'] = datetime.now(timezone.utc)

            # Save changes
            repository_obj.save()
            response = json.loads(repository_obj.to_json())

            return {'success': 'Record Updated Successfully', 'data': response}, '200 Ok'

        except DoesNotExist as e:
            return {'error': 'Repository not found: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def add_entity(self, request_json) -> dict:
        """
        Creates a new repository object in the database.
        """
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()

        request_json = request.get_json()
        status, result, status_code = self._validateRepositoryAdd(request_json)
        if not status:
            return jsonify(result), status_code

        try:
            new_repository_obj = Repository(
                target_repository_id=str(uuid.uuid4()),
                project_id=request_json.get('project_id'),
                repository_url=request_json.get('repository_url'),
                repository_label=request_json.get('repository_label'),
                is_private_repo=request_json.get('is_private_repo', False),
                access_token=request_json.get('access_token'),
                repository_provider=request_json.get("repository_provider"),
                created=datetime.now(timezone.utc),
                creator=current_user,
            )
            new_repository_obj.save()
            response = json.loads(new_repository_obj.to_json())
            return {'success': 'Record Created Successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'


    def delete_by_id(self, target_repository_id: str) -> dict:
        """
        Deletes a Repository object by its target_repository_id from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()

        try:
            # Fetch the Repository object by its ID
            print(f"Fetching Repository record with target_repository_id: {target_repository_id}")
            repository_obj = Repository.objects.get(target_repository_id=target_repository_id)

            if not repository_obj:
                print(f"No Repository record found for target_repository_id: {target_repository_id}")
                return {'error': 'No repository record found with the given ID'}, '404 Not Found'

            current_time = datetime.now(timezone.utc)
            print(f"Current UTC time: {current_time}")

            # Perform bulk update for LanguagesAndFramework records
            print(f"Marking LanguagesAndFramework records as deleted for target_id: {target_repository_id}")
            result_lang_fram = LanguagesAndFramework.objects(target_id=target_repository_id).update(
                set__isdeleted=True, set__updated=current_time
            )
            print(f"Marked {result_lang_fram} LanguagesAndFramework records as deleted.")

            # Perform bulk update for FindingSBOMVulnerability records
            print(f"Marking FindingSBOMVulnerability records as deleted for target_id: {target_repository_id}")
            result_sbom_vul = FindingSBOMVulnerability.objects(target_id=target_repository_id).update(
                set__isdeleted=True, set__updated=current_time
            )
            print(f"Marked {result_sbom_vul} FindingSBOMVulnerability records as deleted.")

            # Perform bulk update for FindingLicense records
            print(f"Marking FindingLicense records as deleted for target_id: {target_repository_id}")
            result_lic_data = FindingLicense.objects(target_id=target_repository_id).update(
                set__isdeleted=True, set__updated=current_time
            )
            print(f"Marked {result_lic_data} FindingLicense records as deleted.")

            # Perform bulk update for FindingMaster and associated records
            print(f"Fetching FindingMaster records for target_id: {target_repository_id}")
            finding_master_queryset = FindingMaster.objects(target_id=target_repository_id)

            # Bulk update RepoSecretDetections records
            print(f"Marking RepoSecretDetections records as deleted for findings associated with target_repository_id: {target_repository_id}")
            for finding in finding_master_queryset:
                RepoSecretDetections.objects(repo_secret_detections_id=finding.extended_finding_details_id).update(
                    set__isdeleted=True, set__updated=current_time
                )

            # Bulk update RepositoryTrivy1 records
            print(f"Marking RepositoryTrivy1 records as deleted for findings associated with target_repository_id: {target_repository_id}")
            for finding in finding_master_queryset:
                RepositoryTrivy1.objects(repository_trivy_1_id=finding.extended_finding_details_id).update(
                    set__isdeleted=True, set__updated=current_time
                )

            # Bulk update FixRecommendations records
            print(f"Marking FixRecommendations records as deleted for findings associated with target_repository_id: {target_repository_id}")
            for finding in finding_master_queryset:
                FixRecommendations.objects(fix_recommendation_id=finding.fix_recommendation_id).update(
                    set__isdeleted=True, set__updated=current_time
                )

            # Bulk update FindingMaster records
            print(f"Marking FindingMaster records as deleted for target_id: {target_repository_id}")
            result_finding_master = finding_master_queryset.update(
                set__isdeleted=True, set__updated=current_time
            )
            print(f"Marked {result_finding_master} FindingMaster records as deleted.")

            # Mark the Repository object as deleted
            print(f"Marking Repository record as deleted for target_repository_id: {target_repository_id}")
            repository_obj.isdeleted = True
            repository_obj.deleted_at = current_time
            repository_obj.save()
            print(f"Marked Repository record as deleted for target_repository_id: {target_repository_id}")

            return {'success': f'Repository record with ID {target_repository_id} has been marked as deleted'}, '200 Ok'

        except Repository.DoesNotExist as e:
            print(f"Error: Repository record with target_repository_id {target_repository_id} not found. Exception: {e}")
            return {'error': f'Repository record with ID {target_repository_id} not found'}, '404 Not Found'
        except ValidationError as e:
            print(f"Validation error while deleting repository: {e}")
            return {'error': 'Validation error: ' + str(e)}, '400 Bad Request'
        except Exception as e:
            print(f"Error while deleting repository record with target_repository_id {target_repository_id}: {e}")
            return {'error': 'Error deleting Repository record: ' + str(e)}, '500 Internal Server Error'