from controllers.util import *
from entities.CyberServiceEntity import Domain, FindingMaster, DomainZap1, DomainWapiti1
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request
from mongoengine import *
from marshmallow import Schema, fields, INCLUDE
from marshmallow import ValidationError as MarshmallowValidationError
from mongoengine import ValidationError as MongoValidationError
from datetime import datetime, timezone
from typing import List
from bson import ObjectId
import uuid
import json


class DomainAddSchema(Schema):
    project_id = fields.String(required=True, error_messages={
        "required": "Project ID is required."})
    domain_url = fields.String(required=True, error_messages={
        "required": "Domain URL is missing."})
    domain_label = fields.String(null=True)


class DomainUpdateSchema(Schema):
    domain_url = fields.String(required=True, error_messages={
        "required": "Domain URL is missing."})
    domain_label = fields.String(null=True)


class DomainController:
    """
    Defines controller methods for the Domain Entity.
    """

    def __init__(self) -> None:
        pass

    def _validateDomainAdd(self, request_json):
        schema = DomainAddSchema()
        try:
            schema.load(request_json, unknown=INCLUDE)
        except MarshmallowValidationError as err:
            return False, err.messages, '400 Bad Request'
        return True, {'message': 'Validation successful'}, '200 Ok'

    def _validateDomainUpdate(self, request_json):
        schema = DomainUpdateSchema()
        try:
            schema.load(request_json, unknown=INCLUDE)
        except MarshmallowValidationError as err:
            return False, err.messages, '400 Bad Request'
        return True, {'message': 'Validation successful'}, '200 Ok'

    def _validateDomain(self, domain_id):
        """
        Validates domain id with the database.
        """
        try:
            Domain.objects.get(target_domain_id=domain_id)
            return True, {'message': 'Record exists in db'}, '200 Ok'
        except DoesNotExist as e:
            return False, {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return False, {'error': 'Validation error: ' + e.message}, '400 Bad Request'

    def fetch_all(self, request, fields) -> List[dict]:
        """
        Fetches all the domain objects from the database.
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
        domain_list = list(Domain.objects.aggregate(pipeline))
        response = domain_list
        return {'success': 'Records Fetched Successfully', 'data': response}, '200 Ok'

    def update_by_id(self, request, target_domain_id) -> dict:
        """
        Updates a domain object by its ID, updating only the fields provided in the request.
        """
        # Fetching user id from JWT token and validate JWT token
        current_user = get_current_user_from_jwt_token()

        # Get the JSON data from the request
        request_json = request.get_json()

        # Validate the domain update
        status, result, status_code = self._validateDomainUpdate(request_json)
        if not status:
            return jsonify(result), status_code

        # Validate domain ID
        if target_domain_id != request_json.get('target_domain_id'):
            return {'error': 'Domain ID in URL does not match the provided target_domain_id in the body'}, '400 Bad Request'
        print(f"Domain ID mismatch: URL ID ({target_domain_id}) != Body ID ({request_json.get('target_domain_id')})")
        try:
            # Fetch the domain from the database
            domain_obj = Domain.objects.get(target_domain_id=target_domain_id)

            # Update fields only if they are present in the request
            if 'domain_url' in request_json:
                domain_obj['domain_url'] = request_json['domain_url']
                domain_obj['domain_label'] = request_json['domain_label']

            # Update metadata
            domain_obj['updator'] = current_user
            domain_obj['updated'] = datetime.now(timezone.utc)

            # Save changes
            domain_obj.save()
            response = json.loads(domain_obj.to_json())

            return {'success': 'Record Updated Successfully', 'data': response}, '200 Ok'

        except DoesNotExist as e:
            return {'error': 'Domain not found: ' + str(e)}, '404 Not Found'
        except MarshmallowValidationError as e:
            return {'error': 'Validation error: ' + str(e)}, '400 Bad Request'
        except MongoValidationError as e:
            return {'error': 'Database validation error: ' + str(e)}, '400 Bad Request'

    def add_entity(self, request_json) -> dict:
        """
        Creates a new domain object in the database.
        """
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()

        request_json = request.get_json()
        status, result, status_code = self._validateDomainAdd(request_json)
        if not status:
            return jsonify(result), status_code

        try:
            new_domain_obj = Domain(
                target_domain_id=str(uuid.uuid4()),
                project_id=request_json.get('project_id'),
                domain_url=request_json.get('domain_url'),
                domain_label=request_json.get('domain_label'),
                created=datetime.now(timezone.utc),
                creator=current_user,
            )
            new_domain_obj.save()
            response = json.loads(new_domain_obj.to_json())
            return {'success': 'Record Created Successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except MarshmallowValidationError as e:
            return {'error': 'Validation error: ' + str(e)}, '400 Bad Request'
        except MongoValidationError as e:
            return {'error': 'Database validation error: ' + str(e)}, '400 Bad Request'

    def delete_by_id(self, domain_id: str) -> dict:
        """
        Deletes a Domain object by its domain_id from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()

        try:
            # Fetch the Domain object by its ID
            domain_obj = Domain.objects.get(target_domain_id=domain_id)

            if not domain_obj:
                return {'error': 'No domain record found with the given ID'}, '404 Not Found'

            # Optionally, mark as deleted without removing from the database (soft delete)
            finding_master_queryset = FindingMaster.objects(target_id=domain_id)
            finding_master_data = json.loads(finding_master_queryset.to_json())

            if finding_master_data:
                for finding in finding_master_queryset:
                    try:
                        # Fetch ZAP scan output related object and mark as deleted
                        domain_zap1_obj = DomainZap1.objects.get(domain_zap_1_id=finding.extended_finding_details_id)
                        domain_zap1_data = json.loads(domain_zap1_obj.to_json())
                        domain_zap1_obj.isdeleted = True
                        domain_zap1_obj.deleted_at = datetime.now(timezone.utc)
                        domain_zap1_obj.save()
                        
                        # Print the deletion details for DomainZap1
                        print(f"Deleted DomainZap1 record with domain_zap_1_id: {domain_zap1_obj.domain_zap_1_id}")
                    
                    except DomainZap1.DoesNotExist:
                        # Log and skip the missing DomainZap1 record
                        print(f"DomainZap1 record with target id {finding.extended_finding_details_id} not found")

                    try:
                        # Fetch Wapiti scan output related object and mark as deleted
                        domain_wapiti1_data = DomainWapiti1.objects.get(domain_wapiti_1_id=finding.extended_finding_details_id)
                        domain_zap1_data = json.loads(domain_wapiti1_data.to_json())
                        domain_wapiti1_data.isdeleted = True
                        domain_wapiti1_data.deleted_at = datetime.now(timezone.utc)
                        domain_wapiti1_data.save()
                        
                        # Print the deletion details for DomainWapiti1
                        print(f"Deleted DomainWapiti1 record with cloud_google_id: {domain_wapiti1_data.domain_wapiti_1_id}")
                    
                    except DomainWapiti1.DoesNotExist:
                        # Log and skip the missing DomainWapiti1 record
                        print(f"DomainWapiti1 record with target id {finding.extended_finding_details_id} not found")

                # Update each object in the FindingMaster queryset
                for finding_master_obj in finding_master_queryset:
                    finding_master_obj.isdeleted = True
                    finding_master_obj.deleted_at = datetime.now(timezone.utc)
                    finding_master_obj.save()
                    
                    # Print the deletion details for FindingMaster
                    print(f"Deleted FindingMaster record with ID: {finding_master_obj.id}")

            # Mark the Domain object as deleted
            domain_obj.isdeleted = True
            domain_obj.deleted_at = datetime.now(timezone.utc)
            domain_obj.save()

            # Print the deletion details for Domain
            print(f"Deleted Domain record with domain id: {domain_id}")

            return {'success': f'Domain record with ID {domain_id} has been marked as deleted'}, '200 Ok'

        except DoesNotExist as e:
            print("Error deleting Domain record: ", e)
            return {'error': f'Domain record with ID {domain_id} not found'}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + str(e)}, '400 Bad Request'
        except Exception as e:
            print("Error deleting Domain record: ", e)
            return {'error': 'Error deleting Domain record: ' + str(e)}, '500 Internal Server Error'


