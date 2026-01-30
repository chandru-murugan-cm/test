

import json
from entities.CyberServiceEntity import OwaspTopTen
from mongoengine.errors import DoesNotExist
from bson import ObjectId
from datetime import datetime
import uuid

class OwaspTopTenController:
    def fetch_by_id(self, owasp_top_ten_id):
        """
        Fetch an OwaspTopTen record by its ID.
        """
        try:
            record = OwaspTopTen.objects(owasp_top_ten_id=owasp_top_ten_id, isdeleted=False).first()
            if record:
                return record.to_json(), 200
            return {'error': 'Record not found'}, 404
        except Exception as e:
            return {'error': str(e)}, 500

    def fetch_all(self):
        """
        Fetch all OwaspTopTen records that are not deleted.
        """
        try:
           
            pipeline = [
                            {
                                "$project": {
                                    "isdeleted": 0  
                                }
                            }
                        ]

            records = list(OwaspTopTen.objects.aggregate(*pipeline))

            return {'success': 'Records fetched successfully', 'data': records}, '200 Ok'
            
          
        except Exception as e:
            return {'error': str(e)}, 500

    def add_entity(self, request):
        """
        Create a new OwaspTopTen record.
        """
        try:
            data = request.get_json()
            new_record = OwaspTopTen(owasp_top_ten_id=str(uuid.uuid4()),
                control_name=data.get('control_name'),
                group_name=data.get('group_name'),
                created=datetime.utcnow(),
                creator=data.get('creator')
            )
            new_record.save()
            return new_record.to_json(), 201
        except Exception as e:
            return {'error': str(e)}, 400
            
    def update_entity(self, owasp_top_ten_id: str, request_json: dict) -> tuple:
        """
        Updates an existing OWASP requirement in the database.
        """
        try:
            print(f"Received request_json: {request_json}")  

            if not request_json or not isinstance(request_json, dict):
                return {'error': 'Request body is invalid or empty'}, 400

            updated_data = {k: v for k, v in request_json.items() if v is not None}
            print(f"Filtered updated_data: {updated_data}") 
            
            if not updated_data:
                return {'error': 'No valid fields provided for update'}, 400

            OWASP_record = OwaspTopTen.objects.get(owasp_top_ten_id=owasp_top_ten_id)
            OWASP_record.update(**updated_data)

            updated_record = OwaspTopTen.objects.get(owasp_top_ten_id=owasp_top_ten_id)
            response = json.loads(updated_record.to_json())

            return response, 200

        except DoesNotExist:
            return {'error': f'OWASP record with ID {owasp_top_ten_id} not found'}, 404
        except Exception as e:
            print(f"Unexpected error occurred while updating: {e}")
            return {'error': f'Unexpected error: {str(e)}'}, 500

    def delete_entity(self, owasp_top_ten_id):
        """
        Soft delete an OwaspTopTen record.
        """
        try:
            record = OwaspTopTen.objects.get(owasp_top_ten_id=owasp_top_ten_id) 
            if record:
                record.isdeleted = True 
                record.save() 
                return {'message': 'Record deleted successfully'}, 200
            
            return {'error': 'Record not found'}, 404
        except DoesNotExist:  
            return {'error': 'Record not found'}, 404
        except Exception as e:
            return {'error': str(e)}, 400
