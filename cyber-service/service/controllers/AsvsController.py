from flask import request, jsonify
from mongoengine import *
from controllers.util import *
from entities.CyberServiceEntity import DomainWapiti1, Compliance,Samm,AsvsRequirement
from typing import List
import uuid, json
from datetime import datetime, timezone

class AsvsController():
    """
    Defines controller methods for the AsvsController Entity.
    """

    def __init__(self) -> None:
        pass

    def fetch_by_id(self, fields) -> List[dict]:
        """
        Fetches a Asvs Controller  object by its _id from the database.
        """
        # Validate JWT Token
        verify_jwt_in_request()
        if "_id" in fields:
            chapter_id = fields['_id']

            try:
                pipeline = [
                    {
                        "$match": {
                            "_id": chapter_id
                        }
                    },
                    {
                        "$project": {
                            "isdeleted": 0
                        }
                    }
                ]

                # Execute the aggregation pipeline
                asvs_list = list(
                    AsvsRequirement.objects.aggregate(*pipeline)
                )
                
                return {'success': 'Records fetched successfully', 'data': asvs_list}, '200 Ok'

            except DoesNotExist as e:
                return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
            except ValidationError as e:
                return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

        
    def fetch_all(self, request) -> List[dict]:
        """
        Fetches all AsvsRequirement records from the database.
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

            asvs_list = list(AsvsRequirement.objects.aggregate(*pipeline))

            return {'success': 'Records fetched successfully', 'data': asvs_list}, '200 Ok'

        except DoesNotExist as e:
            return {'error': 'No records found: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'


    def add_entity(self, request_json) -> dict:
        """
        Creates new project obj in database
        """
        # Fetching user id from jwt token and validate jwt token
        # current_user = get_current_user_from_jwt_token()
        print("request_json", request_json)
        request_json = request.get_json()

        try:
            for record in request_json:
                new_asvs_obj = AsvsRequirement(asvs_id=str(uuid.uuid4()),
                                        # user_id=current_user,
                                        requirement_id=record.get('requirement_id'),
                                        chapter_id=record.get('chapter_id'),
                                        chapter_name=record.get('chapter_name'),
                                        section_id=record.get('section_id'),
                                        section_name=record.get('section_name'),
                                        requirement_name=record.get('requirement_name'),
                                        requirement_reference=record.get('requirement_reference'),
                                        created=datetime.now(timezone.utc),
                                        # creator=current_user,
                                         )
                new_asvs_obj.save()
                response = json.loads(new_asvs_obj.to_json())
            return {'success': 'Record Created Successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
        
    def update_entity(self, asvs_id: str, request_json: dict) -> tuple:
        """
        Updates an existing ASVS requirement in the database.
        """
        # print("Request JSON received:", request_json)
        try:
            # Validate request body
            if not request_json or not isinstance(request_json, dict):
                return {'error': 'Request body is invalid or empty'}, 400
            # Filter out None values (to avoid updating fields with None)
            updated_data = {k: v for k, v in request_json.items() if v is not None}
            if not updated_data:
                return {'error': 'No valid fields provided for update'}, 400
            # Fetch and update the ASVS record
            asvs_record = AsvsRequirement.objects.get(asvs_id=asvs_id)
            asvs_record.update(**updated_data)
            # Retrieve updated record
            updated_record = AsvsRequirement.objects.get(asvs_id=asvs_id)
            response = json.loads(updated_record.to_json())
            return response, 200
        except DoesNotExist:
            return {'error': f'ASVS record with ID {asvs_id} not found'}, 404
        except Exception as e:
            print(f"Unexpected error occurred while updating: {e}")
            return {'error': f'Unexpected error: {str(e)}'}, 500
        
    
    def delete_entity(self, asvs_id) -> dict:
        try:
            asvs_record = AsvsRequirement.objects.get(asvs_id=asvs_id)
            asvs_record.delete()
            return {'message': 'ASCV successfully deleted'}, 200
        except AsvsRequirement.DoesNotExist:
            return {'error': 'ASVS ID not found'}, 404
        except Exception as e:
            print(f"Unexpected error occurred while deleting: {e}")
            return {'error': f'Unexpected error: {str(e)}'}, 500

















