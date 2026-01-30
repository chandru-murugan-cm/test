from flask import request, jsonify
from mongoengine import *
from controllers.util import *
from entities.CyberServiceEntity import TargetAzureCloud, FindingMaster, CloudCloudSploitAzure1
from typing import List
import uuid, json
from datetime import datetime, timezone
import requests
class AzureController():
    """
    Defines controller methods for the TargetAzureCloud Entity.
    """

    def __init__(self) -> None:
        pass

    def validate_azure_credentials(self, application_id, directory_id, client_secret_key, subscription_id) -> bool:
        """
        Validates Azure credentials using Azure REST APIs.
        Returns True if credentials are valid, otherwise raises an exception.
        """
        # Step 1: Validate input values
        if not all([application_id, directory_id, client_secret_key, subscription_id]):
            raise ValueError("All Azure credentials must be provided and cannot be empty.")

        # Step 2: Get an access token using the Azure OAuth2 token endpoint
        token_url = f"https://login.microsoftonline.com/{directory_id}/oauth2/token"
        token_data = {
            "grant_type": "client_credentials",
            "client_id": application_id,
            "client_secret": client_secret_key,
            "resource": "https://management.azure.com/"
        }
        try:
            # Request an access token
            token_response = requests.post(token_url, data=token_data)
            token_response.raise_for_status()  # Raise an exception for HTTP errors
            access_token = token_response.json().get("access_token")

            if not access_token:
                raise ValueError("Failed to retrieve access token. Invalid credentials.")

            # Step 3: Validate the subscription ID using the Azure Management API
            subscription_url = f"https://management.azure.com/subscriptions/{subscription_id}?api-version=2020-01-01"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            subscription_response = requests.get(subscription_url, headers=headers)
            subscription_response.raise_for_status()  # Raise an exception for HTTP errors

            # If no exception is raised, the credentials are valid
            return True

        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors (e.g., 400 Bad Request)
            error_response = token_response.json()
            error_code = error_response.get("error", "Unknown error")
            error_description = error_response.get("error_description", "No additional details provided.")
            raise ValueError(f"Azure authentication failed: {error_code} - {error_description}")
        except Exception as e:
            raise ValueError(f"Error validating Azure credentials: {str(e)}")
    
    def fetch_by_id(self, fields) -> List[dict]:
        """
        Fetches an TargetAzureCloud object by its azure_id from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()

        if "_id" in fields:
            azure_id = fields['_id']

            try:
                pipeline = [
                    {
                        "$match": {
                            "azure_id": azure_id
                        }
                    },
                    {
                        "$project": {
                            "isdeleted": 0  # Optionally exclude isdeleted field
                        }
                    }
                ]

                # Execute the aggregation pipeline
                azure_cloud_list = list(TargetAzureCloud.objects.aggregate(*pipeline))

                return {'success': 'Records fetched successfully', 'data': azure_cloud_list}, '200 Ok'

            except DoesNotExist as e:
                return {'error': 'No records found for azure_id: ' + azure_id}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_by_name(self, name) -> List[dict]:
        """
        Fetches TargetAzureCloud records by name from the database.
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
            azure_cloud_list = list(TargetAzureCloud.objects.aggregate(*pipeline))

            return {'success': 'Records fetched successfully', 'data': azure_cloud_list}, '200 Ok'

        except DoesNotExist as e:
            return {'error': 'No records found for name: ' + name}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_all(self) -> List[dict]:
        """
        Fetches all TargetAzureCloud records from the database.
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

            azure_cloud_list = list(TargetAzureCloud.objects.aggregate(*pipeline))

            return {'success': 'Records fetched successfully', 'data': azure_cloud_list}, '200 Ok'

        except DoesNotExist as e:
            return {'error': 'No records found: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_by_project_id(self, fields) -> List[dict]:
        """
        Fetches TargetAzureCloud records by project_id from the database.
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
                azure_cloud_list = list(TargetAzureCloud.objects.aggregate(*pipeline))

                return {'success': 'Records fetched successfully', 'data': azure_cloud_list}, '200 Ok'

            except DoesNotExist as e:
                return {'error': 'No records found for project_id: ' + project_id}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def add_entity(self, request) -> dict:
        """
        Creates new project obj in database with validation for required fields
        """
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()
        request_json = request.get_json()
        print("request_json", request_json)

        # List of required fields
        required_fields = ['project_id', 'application_id', 'directory_id', 'client_secret_key', 'subscription_id', 'name']

        # Validate if all required fields are present and not missing (None), ignoring empty strings
        missing_fields = [field for field in required_fields if request_json.get(field) is None]
        
        # Fields that are empty (contain "")
        empty_fields = [field for field in required_fields if request_json.get(field) == '']

        if missing_fields:
            return {'error': f'Missing required fields: {", ".join(missing_fields)}'}, '400 Bad Request'

        if empty_fields:
            return {'error': f'Empty required fields: {", ".join(empty_fields)}'}, '400 Bad Request'

        try:

            # Validate Azure credentials
            is_valid = self.validate_azure_credentials(
                application_id=request_json['application_id'],
                directory_id=request_json['directory_id'],
                client_secret_key=request_json['client_secret_key'],
                subscription_id=request_json['subscription_id']
            )

            if not is_valid:
                return {'error': 'Azure credentials validation failed.'}, '400 Bad Request'

            # Create the TargetAzureCloud object after validation
            new_azure_cloud_obj = TargetAzureCloud(
                azure_id=str(uuid.uuid4()),
                project_id=request_json['project_id'],
                application_id=request_json['application_id'],
                directory_id=request_json['directory_id'],
                client_secret_key=request_json['client_secret_key'],
                subscription_id=request_json['subscription_id'],
                name=request_json['name'],
                created=datetime.now(timezone.utc),
                creator=current_user,
            )
            new_azure_cloud_obj.save()
            response = json.loads(new_azure_cloud_obj.to_json())
            return {'success': 'Record Created Successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': f'Empty query: {str(e)}'}, '404 Not Found'
        except ValidationError as e:
            return {'error': f'Validation error: {e.message}'}, '400 Bad Request'
        except ValueError as e:
            return {'error': f'Error: {str(e)}'}, '400 Bad Request'
        except Exception as e:
            return {'error': f'Internal server error: {str(e)}'}, '500 Internal Server Error'
        
    def delete_by_id(self, azure_id: str) -> dict:
        """
        Deletes a TargetAzureCloud object by its azure_id from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()

        try:
            # Fetch the TargetAzureCloud object by its ID
            azure_cloud_obj = TargetAzureCloud.objects.get(azure_id=azure_id)

            if not azure_cloud_obj:
                return {'error': 'No TargetAzureCloud record found with the given ID'}, '404 Not Found'

            # Optionally, mark as deleted without removing from the database (soft delete)
            finding_master_queryset = FindingMaster.objects(target_id=azure_id)
            finding_master_data = json.loads(finding_master_queryset.to_json())

            if finding_master_data:
                for finding in finding_master_queryset:
                    try:
                        # Fetch related CloudCloudSploitAzure1 object and mark as deleted
                        azure1_obj = CloudCloudSploitAzure1.objects.get(cloud_azure_id=finding.extended_finding_details_id)
                        azure1_data = json.loads(azure1_obj.to_json())
                        azure1_obj.isdeleted = True
                        azure1_obj.deleted_at = datetime.now(timezone.utc)
                        azure1_obj.save()
                        
                        # Print the deletion details for CloudCloudSploitAzure1
                        print(f"Deleted CloudCloudSploitAzure1 record with cloud_azure_id: {azure1_obj.cloud_azure_id}")
                    
                    except CloudCloudSploitAzure1.DoesNotExist:
                        # Log and skip the missing CloudCloudSploitAzure1 record
                        print(f"CloudCloudSploitAzure1 record with cloud_azure_id {finding.extended_finding_details_id} not found.")

                # Update each object in the FindingMaster queryset
                for finding_master_obj in finding_master_queryset:
                    finding_master_obj.isdeleted = True
                    finding_master_obj.deleted_at = datetime.now(timezone.utc)
                    finding_master_obj.save()
                    
                    # Print the deletion details for FindingMaster
                    print(f"Deleted FindingMaster record with ID: {finding_master_obj.id}")

            # Mark the TargetAzureCloud object as deleted
            azure_cloud_obj.isdeleted = True
            azure_cloud_obj.deleted_at = datetime.now(timezone.utc)
            azure_cloud_obj.save()

            # Print the deletion details for TargetAzureCloud
            print(f"Deleted TargetAzureCloud record with azure_id: {azure_cloud_obj.azure_id}")

            return {'success': f'TargetAzureCloud record with ID {azure_id} has been marked as deleted'}, '200 Ok'

        except DoesNotExist as e:
            print("Error deleting TargetAzureCloud record: ", e)
            return {'error': f'TargetAzureCloud record with ID {azure_id} not found'}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + str(e)}, '400 Bad Request'
        except Exception as e:
            print("Error deleting TargetAzureCloud record: ", e)
            return {'error': 'Error deleting TargetAzureCloud record: ' + str(e)}, '500 Internal Server Error'

