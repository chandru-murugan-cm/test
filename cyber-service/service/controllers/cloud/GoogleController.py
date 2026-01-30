from flask import request, jsonify
from mongoengine import *
from controllers.util import *
from entities.CyberServiceEntity import TargetGoogleCloud, FindingMaster, CloudCloudSploitGoogle1
from typing import List
import uuid, json
from datetime import datetime, timezone

class GoogleController():
    """
    Defines controller methods for the TargetGoogleCloud Entity.
    """

    def __init__(self) -> None:
        pass

    def fetch_by_id(self, fields) -> List[dict]:
        """
        Fetches an TargetGoogleCloud object by its google_id from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()

        if "_id" in fields:
            google_id = fields['_id']

            try:
                pipeline = [
                    {
                        "$match": {
                            "google_id": google_id
                        }
                    },
                    {
                        "$project": {
                            "isdeleted": 0  # Optionally exclude isdeleted field
                        }
                    }
                ]

                # Execute the aggregation pipeline
                google_cloud_list = list(TargetGoogleCloud.objects.aggregate(*pipeline))

                return {'success': 'Records fetched successfully', 'data': google_cloud_list}, '200 Ok'

            except DoesNotExist as e:
                return {'error': 'No records found for google_id: ' + google_id}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_by_name(self, name) -> List[dict]:
        """
        Fetches TargetGoogleCloud records by name from the database.
        """
        verify_jwt_in_request()

        try:
            pipeline = [
                {
                    "$match": {
                        "name": name
                    }
                },
                {
                    "$project": {
                        "isdeleted": 0  # Optionally exclude isdeleted field
                    }
                }
            ]
            google_cloud_list = list(TargetGoogleCloud.objects.aggregate(*pipeline))

            return {'success': 'Records fetched successfully', 'data': google_cloud_list}, '200 Ok'

        except DoesNotExist as e:
            return {'error': 'No records found for name: ' + name}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_all(self) -> List[dict]:
        """
        Fetches all TargetGoogleCloud records from the database.
        """
        verify_jwt_in_request()

        try:
            pipeline = [
                {
                    "$project": {
                        "isdeleted": 0  # Optionally exclude isdeleted field
                    }
                }
            ]

            google_cloud_list = list(TargetGoogleCloud.objects.aggregate(*pipeline))

            return {'success': 'Records fetched successfully', 'data': google_cloud_list}, '200 Ok'

        except DoesNotExist as e:
            return {'error': 'No records found: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_by_project_id(self, fields) -> List[dict]:
        """
        Fetches TargetGoogleCloud records by project_id from the database.
        """
        verify_jwt_in_request()

        if "project_id" in fields:
            project_id = fields["project_id"]

            try:
                pipeline = [
                    {
                        "$match": {
                            "project_id": project_id
                        }
                    },
                    {
                        "$project": {
                            "isdeleted": 0  # Optionally exclude isdeleted field
                        }
                    }
                ]
                google_cloud_list = list(TargetGoogleCloud.objects.aggregate(*pipeline))

                return {'success': 'Records fetched successfully', 'data': google_cloud_list}, '200 Ok'

            except DoesNotExist as e:
                return {'error': 'No records found for project_id: ' + project_id}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def add_entity(self, request) -> dict:
        """
        Creates new Google Cloud service account obj in the database with validation for required fields
        """
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()
        request_json = request.get_json()
        print("request_json", request_json)

        # List of required fields based on the input structure
        required_fields = ['cloud_name','type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id', 'auth_uri', 'token_uri', 'auth_provider_x509_cert_url', 'client_x509_cert_url', 'universe_domain']

        # Validate if all required fields are present and not missing (None), ignoring empty strings
        missing_fields = [field for field in required_fields if request_json.get(field) is None]
        
        # Fields that are empty (contain "")
        empty_fields = [field for field in required_fields if request_json.get(field) == '']

        if missing_fields:
            return {'error': f'Missing required fields: {", ".join(missing_fields)}'}, '400 Bad Request'

        if empty_fields:
            return {'error': f'Empty required fields: {", ".join(empty_fields)}'}, '400 Bad Request'

        try:
            # Create the TargetGoogleCloud object after validation
            new_google_cloud_obj = TargetGoogleCloud(
                google_id=str(uuid.uuid4()),
                name=request_json['cloud_name'],
                project_id=request_json['project_id'],
                type=request_json['type'],
                gcp_project_id=request_json['gcp_project_id'],
                private_key_id=request_json['private_key_id'],
                private_key=request_json['private_key'],
                client_email=request_json['client_email'],
                client_id=request_json['client_id'],
                auth_uri=request_json['auth_uri'],
                token_uri=request_json['token_uri'],
                auth_provider_x509_cert_url=request_json['auth_provider_x509_cert_url'],
                client_x509_cert_url=request_json['client_x509_cert_url'],
                universe_domain=request_json['universe_domain'],
                created=datetime.now(timezone.utc),
                creator=current_user,
            )
            new_google_cloud_obj.save()
            response = json.loads(new_google_cloud_obj.to_json())
            return {'success': 'Record Created Successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def delete_by_id(self, google_id: str) -> dict:
        """
        Deletes a TargetAzureCloud object by its azure_id from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()

        try:
            # Fetch the TargetGoogleCloud object by its ID
            google_cloud_obj = TargetGoogleCloud.objects.get(google_id=google_id)

            if not google_cloud_obj:
                return {'error': 'No TargetAzureCloud record found with the given ID'}, '404 Not Found'

            # Optionally, mark as deleted without removing from the database (soft delete)
            finding_master_queryset = FindingMaster.objects(target_id=google_id)
            finding_master_data = json.loads(finding_master_queryset.to_json())

            if finding_master_data:
                for finding in finding_master_queryset:
                    try:
                        # Fetch related CloudCloudSploitAzure1 object and mark as deleted
                        google1_obj = CloudCloudSploitGoogle1.objects.get(cloud_google_id=finding.extended_finding_details_id)
                        azure1_data = json.loads(google1_obj.to_json())
                        google1_obj.isdeleted = True
                        google1_obj.deleted_at = datetime.now(timezone.utc)
                        google1_obj.save()
                        
                        # Print the deletion details for CloudCloudSploitAzure1
                        print(f"Deleted CloudCloudSploitAzure1 record with cloud_google_id: {google1_obj.cloud_google_id}")
                    
                    except CloudCloudSploitGoogle1.DoesNotExist:
                        # Log and skip the missing CloudCloudSploitAzure1 record
                        print(f"CloudCloudSploitAzure1 record with cloud_google_id {finding.extended_finding_details_id} not found.")

                # Update each object in the FindingMaster queryset
                for finding_master_obj in finding_master_queryset:
                    finding_master_obj.isdeleted = True
                    finding_master_obj.deleted_at = datetime.now(timezone.utc)
                    finding_master_obj.save()
                    
                    # Print the deletion details for FindingMaster
                    print(f"Deleted FindingMaster record with ID: {finding_master_obj.id}")

            # Mark the TargetAzureCloud object as deleted
            google_cloud_obj.isdeleted = True
            google_cloud_obj.deleted_at = datetime.now(timezone.utc)
            google_cloud_obj.save()

            # Print the deletion details for TargetAzureCloud
            print(f"Deleted TargetAzureCloud record with google_id: {google_cloud_obj.google_id}")

            return {'success': f'TargetAzureCloud record with ID {google_id} has been marked as deleted'}, '200 Ok'

        except DoesNotExist as e:
            print("Error deleting TargetAzureCloud record: ", e)
            return {'error': f'TargetAzureCloud record with ID {google_id} not found'}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + str(e)}, '400 Bad Request'
        except Exception as e:
            print("Error deleting TargetAzureCloud record: ", e)
            return {'error': 'Error deleting TargetAzureCloud record: ' + str(e)}, '500 Internal Server Error'

