# try:
#     # runtime import
#     from entities.InterventionEntity import Intervention
# except Exception as e:
#     # testing import
#     from ..entities.InterventionEntity import Intervention
# from controllers.util import *
from typing import List
from flask import request, jsonify
from mongoengine import *
from controllers.util import *
from marshmallow import Schema, fields, ValidationError
from datetime import datetime, timezone
import uuid
import json
from entities.CyberServiceEntity import Scanners


class ScannersController():
    """
    Defines controller methods for the Intervention Entity.
    """

    def __init__(self) -> None:
        pass

    def add_entity(self, request) -> dict:
        # Fetching user id from jwt token and validate jwt token
        current_user = get_current_user_from_jwt_token()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401
        
        request_json = request.get_json()

        # Fetching data from jwt token
        # decoded_token_data = get_decoded_token(request)
        name = request_json.get('name', None)
        description = request_json.get('description', None)
        version = request_json.get('version', None)

        try:
            new_scanner_obj = Scanners(
                scanner_id=str(uuid.uuid4()),
                name=name,
                description=description,
                version=version,
                created=datetime.now(timezone.utc),
                creator=current_user
            )
            new_scanner_obj.save()
            response = json.loads(new_scanner_obj.to_json())
            return {'success': 'Record Created Successfully', 'data': response}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Empty query: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'
    
    def fetch_all(self, request, fields) -> List[dict]:
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
        scanners_list = list(Scanners.objects.aggregate(pipeline))
        response = scanners_list
        return {'success': 'Records Fetched Successfully', 'data': response}, '200 Ok'
    
    
    def update_scanner(self, request, scanner_id):
        if not hasattr(request, 'get_json'):
            return jsonify({"error": "Invalid request object"}), 400

        current_user = get_current_user_from_jwt_token()
        if not current_user:
           return jsonify({"error": "Unauthorized"}), 401

        request_json = request.get_json()
        if not scanner_id:
           return jsonify({"error": "scanner_id is required"}), 400
    # Fetch the scanner entity
        scanner_entity = Scanners.objects(scanner_id=scanner_id).first()
        if not scanner_entity:
            return jsonify({"error": "Scanner not found"}), 404
    # Update fields 
        for field in ["name", "description", "version"]:
            if request_json.get(field):
                setattr(scanner_entity, field, request_json[field])
        scanner_entity.updated = datetime.now(timezone.utc)
        scanner_entity.updator = current_user
    # Save the updated entity
        scanner_entity.save()
        return jsonify({"message": "Scanner updated successfully", "data": json.loads(scanner_entity.to_json())}), 200


    def delete_scanner(self, scanner_id):
        current_user = get_current_user_from_jwt_token()
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401
        try:
            scanner_entity = Scanners.objects.get(scanner_id=scanner_id)
            if not scanner_entity:
                return jsonify({"error": "Scanner not found"}), 404
            scanner_entity.isdeleted = True
            scanner_entity.updated = datetime.now(timezone.utc)
            scanner_entity.updator = current_user
            scanner_entity.save()
            return {'success': 'Scanner deleted successfully'}, '200 Ok'
        except DoesNotExist as e:
            return {'error': 'Scanner not found: ' + str(e)}, '404 Not Found'
        except ValidationError as e:
            return {'error': 'Validation error: ' + e.message}, '400 Bad Request'

